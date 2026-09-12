from navigation_core.map_matching.offline_map import OfflineMapProvider, RoadSegment
from navigation_core.map_matching.matcher import MapMatcher
from navigation_core.state import NavigationState, NavigationMode

class MockMapProvider(OfflineMapProvider):
    def __init__(self):
        self.segments = [
            RoadSegment("R1", [(0.0, 0.0), (0.001, 0.0)], "BIDIRECTIONAL", "highway"),
            RoadSegment("R2", [(0.001, 0.0), (0.002, 0.0)], "BIDIRECTIONAL", "highway"),
            RoadSegment("R3", [(0.0, 0.001), (0.001, 0.001)], "BIDIRECTIONAL", "highway")
        ]
        self.is_loaded = True
        
    def query_nearby_roads(self, lat, lon, radius_m):
        return self.segments
        
    def get_connected_roads(self, road_id):
        if road_id == "R1":
            return ["R2"]
        if road_id == "R2":
            return ["R1"]
        return []
        
    def check_coverage(self, lat, lon):
        return True

def test_map_matcher_scoring():
    provider = MockMapProvider()
    matcher = MapMatcher(provider)
    
    state = NavigationState(
        timestamp=0.0,
        latitude=0.0005,
        longitude=0.0001, # Close to R1 (which is at lon 0.0)
        altitude=0.0,
        velocity_north=10.0,
        velocity_east=0.0,
        velocity_up=0.0,
        roll=0.0,
        pitch=0.0,
        yaw=0.0,
        mode=NavigationMode.DEAD_RECKONING,
        pos_uncertainty=10.0,
        vel_uncertainty=1.0
    )
    
    candidates = matcher.score_candidates(state, provider.segments)
    
    assert len(candidates) == 3
    assert candidates[0].segment.road_id == "R1"
    
def test_map_matcher_continuity():
    provider = MockMapProvider()
    matcher = MapMatcher(provider)
    matcher.last_matched_segment_id = "R1"
    
    state = NavigationState(
        timestamp=0.0,
        latitude=0.001,
        longitude=0.00005, # Equidistant to R1 and R2 junction, but moving forward
        altitude=0.0,
        velocity_north=10.0,
        velocity_east=0.0,
        velocity_up=0.0,
        roll=0.0,
        pitch=0.0,
        yaw=0.0,
        mode=NavigationMode.DEAD_RECKONING,
        pos_uncertainty=10.0,
        vel_uncertainty=1.0
    )
    
    candidates = matcher.score_candidates(state, provider.segments)
    
    # R2 should score high because it connects to R1
    top_ids = [c.segment.road_id for c in candidates[:2]]
    assert "R1" in top_ids
    assert "R2" in top_ids
