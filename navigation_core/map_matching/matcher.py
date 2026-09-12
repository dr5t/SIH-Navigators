import math
from typing import List, Optional
from dataclasses import dataclass
from navigation_core.map_matching.offline_map import OfflineMapProvider, RoadSegment
from navigation_core.state import NavigationState

@dataclass
class MapMatchCandidate:
    segment: RoadSegment
    distance: float
    projected_lat: float
    projected_lon: float
    road_heading: float
    score: float
    confidence: float

class MapMatcher:
    def __init__(self, provider: OfflineMapProvider):
        self.provider = provider
        self.last_matched_segment_id: Optional[str] = None
        self.consecutive_matches = 0
        
        # Scoring weights
        self.W_DIST = 1.0
        self.W_HEADING = 0.5
        self.W_CONTINUITY = 2.0
        self.W_SPEED = 0.2
        
    def _point_to_line_dist(self, p_lat: float, p_lon: float, a_lat: float, a_lon: float, b_lat: float, b_lon: float):
        """Returns distance, proj_lat, proj_lon, and heading of the segment A->B"""
        # Flat earth approximation for very short distances
        lat_to_m = 111000.0
        lon_to_m = 111000.0 * math.cos(math.radians(p_lat))
        
        px, py = (p_lon - a_lon) * lon_to_m, (p_lat - a_lat) * lat_to_m
        bx, by = (b_lon - a_lon) * lon_to_m, (b_lat - a_lat) * lat_to_m
        
        l2 = bx**2 + by**2
        if l2 == 0:
            return self.provider._haversine(p_lat, p_lon, a_lat, a_lon), a_lat, a_lon, 0.0
            
        t = max(0.0, min(1.0, (px*bx + py*by) / l2))
        
        proj_x, proj_y = a_lon * lon_to_m + t * bx, a_lat * lat_to_m + t * by
        proj_lon, proj_lat = proj_x / lon_to_m, proj_y / lat_to_m
        
        dist = self.provider._haversine(p_lat, p_lon, proj_lat, proj_lon)
        heading = (math.degrees(math.atan2(bx, by)) + 360) % 360
        
        return dist, proj_lat, proj_lon, heading

    def _closest_point_on_segment(self, lat: float, lon: float, segment: RoadSegment):
        min_dist = float('inf')
        best_proj_lat = lat
        best_proj_lon = lon
        best_heading = 0.0
        
        for i in range(len(segment.nodes) - 1):
            alat, alon = segment.nodes[i]
            blat, blon = segment.nodes[i+1]
            dist, plat, plon, hdg = self._point_to_line_dist(lat, lon, alat, alon, blat, blon)
            
            if dist < min_dist:
                min_dist = dist
                best_proj_lat = plat
                best_proj_lon = plon
                best_heading = hdg
                
        return min_dist, best_proj_lat, best_proj_lon, best_heading

    def _heading_diff(self, h1: float, h2: float) -> float:
        diff = abs(h1 - h2) % 360
        return min(diff, 360 - diff)

    def score_candidates(self, state: NavigationState, segments: List[RoadSegment]) -> List[MapMatchCandidate]:
        candidates = []
        vehicle_heading = (math.degrees(math.atan2(state.velocity_east, state.velocity_north)) + 360) % 360
        speed = state.speed_m_s
        
        # Get connected roads to the last match
        connected_roads = set()
        if self.last_matched_segment_id:
            connected_roads.update(self.provider.get_connected_roads(self.last_matched_segment_id))
            connected_roads.add(self.last_matched_segment_id) # staying on same road is allowed
            
        for seg in segments:
            dist, plat, plon, road_hdg = self._closest_point_on_segment(state.latitude, state.longitude, seg)
            
            # Position Score (closer is better, standard deviation of pos_uncertainty)
            pos_score = math.exp(-0.5 * (dist / max(5.0, state.pos_uncertainty))**2)
            
            # Heading Score
            hdg_diff = self._heading_diff(vehicle_heading, road_hdg)
            if seg.direction == "BIDIRECTIONAL" and hdg_diff > 90:
                hdg_diff = self._heading_diff(vehicle_heading, (road_hdg + 180) % 360)
                road_hdg = (road_hdg + 180) % 360
                
            hdg_score = math.exp(-0.5 * (hdg_diff / 30.0)**2)
            
            # Continuity Score
            cont_score = 1.0 if seg.road_id in connected_roads else 0.0
            
            # Speed constraints
            speed_score = 1.0
            if speed < 1.0 and cont_score == 0.0 and self.last_matched_segment_id:
                # Disincentivize jumping roads when stationary/slow
                speed_score = 0.1
                
            total_score = (
                self.W_DIST * pos_score +
                self.W_HEADING * hdg_score +
                self.W_CONTINUITY * cont_score +
                self.W_SPEED * speed_score
            )
            
            # Base confidence on spatial proximity and heading agreement
            confidence = (pos_score * hdg_score * speed_score)
            if cont_score > 0:
                confidence = min(1.0, confidence * 1.5)
                
            candidates.append(MapMatchCandidate(seg, dist, plat, plon, road_hdg, total_score, confidence))
            
        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates

    def update(self, state: NavigationState) -> Optional[MapMatchCandidate]:
        if not hasattr(state, "map_status"):
            state.map_status = "UNKNOWN"
            
        if not self.provider.is_loaded:
            state.map_status = "MAP_UNAVAILABLE"
            return None
            
        if not self.provider.check_coverage(state.latitude, state.longitude):
            state.map_status = "OUT_OF_COVERAGE"
            self.last_matched_segment_id = None
            return None
            
        state.map_status = "COVERAGE_GOOD"
        
        # Search radius grows with uncertainty
        search_radius = max(50.0, state.pos_uncertainty * 3.0)
        
        nearby = self.provider.query_nearby_roads(state.latitude, state.longitude, search_radius)
        if not nearby:
            self.last_matched_segment_id = None
            return None
            
        candidates = self.score_candidates(state, nearby)
        best = candidates[0]
        
        if best.confidence < 0.2:
            # Low confidence match
            self.last_matched_segment_id = None
            self.consecutive_matches = 0
            return best
            
        self.last_matched_segment_id = best.segment.road_id
        self.consecutive_matches += 1
        return best
