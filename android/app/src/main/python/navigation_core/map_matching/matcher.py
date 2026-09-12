import numpy as np

def snap_to_road(pos: np.ndarray, road_segments: np.ndarray) -> np.ndarray:
    """
    Snaps a 2D position (E, N) to the nearest road segment.
    
    Args:
        pos: (2,) array [x, y]
        road_segments: (N, 2, 2) array of N segments. Each segment has start and end [x, y].
        
    Returns:
        Snapped position (2,) array [x, y]
    """
    if len(road_segments) == 0:
        return pos
        
    p1 = road_segments[:, 0, :]
    p2 = road_segments[:, 1, :]
    
    # Vector from p1 to p2
    v = p2 - p1
    # Vector from p1 to pos
    w = pos - p1
    
    c1 = np.sum(w * v, axis=1)
    c2 = np.sum(v * v, axis=1)
    
    # Projection scale
    b = c1 / np.maximum(c2, 1e-8)
    # Clip to [0, 1] to stay within the segment
    b = np.clip(b, 0.0, 1.0)
    
    # Projected points
    proj = p1 + b[:, np.newaxis] * v
    
    # Find closest segment
    dists = np.linalg.norm(pos - proj, axis=1)
    idx = np.argmin(dists)
    
    return proj[idx]
