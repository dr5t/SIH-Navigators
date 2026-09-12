import json
import os
import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class RoadSegment:
    road_id: str
    nodes: List[tuple[float, float]]  # [(lat, lon), ...]
    direction: str  # "FORWARD", "BACKWARD", "BIDIRECTIONAL"
    road_type: str  # e.g., "highway", "residential"
    speed_limit: Optional[float] = None # m/s
    
    def length(self) -> float:
        # Approximate length in meters
        if not self.nodes or len(self.nodes) < 2:
            return 0.0
        d = 0.0
        for i in range(len(self.nodes) - 1):
            p1 = self.nodes[i]
            p2 = self.nodes[i+1]
            d += self._haversine(p1[0], p1[1], p2[0], p2[1])
        return d
        
    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2) -> float:
        r = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
        return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1-a))

class OfflineMapProvider:
    """Base interface for offline map queries."""
    def load_region(self, region_id: str) -> bool:
        raise NotImplementedError
        
    def unload_region(self) -> None:
        raise NotImplementedError
        
    def query_nearby_roads(self, lat: float, lon: float, radius_m: float) -> List[RoadSegment]:
        raise NotImplementedError
        
    def get_connected_roads(self, road_id: str) -> List[str]:
        raise NotImplementedError
        
    def check_coverage(self, lat: float, lon: float) -> bool:
        raise NotImplementedError
        
    def get_map_version(self) -> str:
        raise NotImplementedError

class LocalMapPackage(OfflineMapProvider):
    """
    A lightweight, pure-Python offline map provider that loads a GeoJSON-like 
    package and uses a basic grid-based spatial index for fast mobile queries.
    """
    def __init__(self, package_path: str = "map_package.json"):
        self.package_path = package_path
        self.segments: Dict[str, RoadSegment] = {}
        self.grid: Dict[tuple[int, int], List[str]] = {} # Spatial index
        self.grid_size_m = 500.0 # 500m grid cells
        self.metadata: Dict[str, Any] = {}
        self.is_loaded = False
        
    def load_region(self, region_id: str = "default") -> bool:
        if not os.path.exists(self.package_path):
            self.metadata["status"] = "MAP_UNAVAILABLE"
            return False
            
        try:
            with open(self.package_path, 'r') as f:
                data = json.load(f)
                
            self.metadata = data.get("metadata", {})
            self.metadata["status"] = "COVERAGE_GOOD"
            
            for feature in data.get("features", []):
                props = feature.get("properties", {})
                geom = feature.get("geometry", {})
                if geom.get("type") == "LineString":
                    # GeoJSON is [lon, lat], convert to (lat, lon)
                    nodes = [(coord[1], coord[0]) for coord in geom.get("coordinates", [])]
                    road_id = props.get("id", str(len(self.segments)))
                    
                    seg = RoadSegment(
                        road_id=road_id,
                        nodes=nodes,
                        direction=props.get("direction", "BIDIRECTIONAL"),
                        road_type=props.get("highway", "unclassified"),
                        speed_limit=props.get("maxspeed")
                    )
                    self.segments[road_id] = seg
                    self._index_segment(seg)
                    
            self.is_loaded = True
            return True
        except Exception as e:
            self.metadata["status"] = "MAP_CORRUPTED"
            return False
            
    def _index_segment(self, seg: RoadSegment):
        """Indexes a segment into the grid."""
        for lat, lon in seg.nodes:
            cell = self._get_grid_cell(lat, lon)
            if cell not in self.grid:
                self.grid[cell] = []
            if seg.road_id not in self.grid[cell]:
                self.grid[cell].append(seg.road_id)
                
    def _get_grid_cell(self, lat: float, lon: float) -> tuple[int, int]:
        # Approx: 1 deg lat = 111km, 1 deg lon = 111km * cos(lat)
        lat_grid = int((lat * 111000.0) / self.grid_size_m)
        lon_grid = int((lon * 111000.0 * math.cos(math.radians(lat))) / self.grid_size_m)
        return (lat_grid, lon_grid)

    def query_nearby_roads(self, lat: float, lon: float, radius_m: float) -> List[RoadSegment]:
        if not self.is_loaded:
            return []
            
        cell_radius = max(1, int(radius_m / self.grid_size_m) + 1)
        center_cell = self._get_grid_cell(lat, lon)
        
        candidate_ids = set()
        for i in range(-cell_radius, cell_radius + 1):
            for j in range(-cell_radius, cell_radius + 1):
                cell = (center_cell[0] + i, center_cell[1] + j)
                candidate_ids.update(self.grid.get(cell, []))
                
        return [self.segments[rid] for rid in candidate_ids]

    def get_connected_roads(self, road_id: str) -> List[str]:
        # A simple node-matching approach for connectivity
        if road_id not in self.segments:
            return []
        seg = self.segments[road_id]
        endpoints = {seg.nodes[0], seg.nodes[-1]}
        
        connected = []
        for other_id, other_seg in self.segments.items():
            if other_id == road_id:
                continue
            if endpoints.intersection({other_seg.nodes[0], other_seg.nodes[-1]}):
                connected.append(other_id)
        return connected

    def check_coverage(self, lat: float, lon: float) -> bool:
        if not self.is_loaded:
            return False
        # If there are any roads in the 3x3 grid neighborhood, we assume coverage
        center = self._get_grid_cell(lat, lon)
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (center[0] + i, center[1] + j) in self.grid:
                    return True
        return False

    def get_map_version(self) -> str:
        return self.metadata.get("map_version", "unknown")
