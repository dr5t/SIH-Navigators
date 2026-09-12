import numpy as np

# WGS-84 ellipsoid parameters
A = 6378137.0  # semi-major axis in meters
F = 1.0 / 298.257223563
B = A * (1.0 - F)  # semi-minor axis
E2 = 1.0 - (B / A) ** 2  # first eccentricity squared

def lla_to_ecef(lat_deg: float, lon_deg: float, alt_m: float) -> np.ndarray:
    """Convert Latitude, Longitude, Altitude to ECEF coordinates."""
    lat_rad = np.radians(lat_deg)
    lon_rad = np.radians(lon_deg)
    
    sin_lat = np.sin(lat_rad)
    cos_lat = np.cos(lat_rad)
    sin_lon = np.sin(lon_rad)
    cos_lon = np.cos(lon_rad)
    
    # Prime vertical radius of curvature
    N = A / np.sqrt(1.0 - E2 * sin_lat ** 2)
    
    x = (N + alt_m) * cos_lat * cos_lon
    y = (N + alt_m) * cos_lat * sin_lon
    z = (N * (1.0 - E2) + alt_m) * sin_lat
    
    return np.array([x, y, z])

def ecef_to_enu(x: float, y: float, z: float, ref_lat_deg: float, ref_lon_deg: float, ref_alt_m: float) -> np.ndarray:
    """Convert ECEF coordinates to local ENU given a reference LLA point."""
    ref_ecef = lla_to_ecef(ref_lat_deg, ref_lon_deg, ref_alt_m)
    
    dx = x - ref_ecef[0]
    dy = y - ref_ecef[1]
    dz = z - ref_ecef[2]
    
    lat_rad = np.radians(ref_lat_deg)
    lon_rad = np.radians(ref_lon_deg)
    
    sin_lat = np.sin(lat_rad)
    cos_lat = np.cos(lat_rad)
    sin_lon = np.sin(lon_rad)
    cos_lon = np.cos(lon_rad)
    
    # Rotation matrix from ECEF to ENU
    R = np.array([
        [-sin_lon, cos_lon, 0],
        [-sin_lat * cos_lon, -sin_lat * sin_lon, cos_lat],
        [cos_lat * cos_lon, cos_lat * sin_lon, sin_lat]
    ])
    
    enu = R @ np.array([dx, dy, dz])
    return enu

def lla_to_enu(lat_deg: float, lon_deg: float, alt_m: float, ref_lat_deg: float, ref_lon_deg: float, ref_alt_m: float) -> np.ndarray:
    """Directly convert LLA to local ENU."""
    ecef = lla_to_ecef(lat_deg, lon_deg, alt_m)
    return ecef_to_enu(ecef[0], ecef[1], ecef[2], ref_lat_deg, ref_lon_deg, ref_alt_m)

def enu_to_ecef(e: float, n: float, u: float, ref_lat_deg: float, ref_lon_deg: float, ref_alt_m: float) -> np.ndarray:
    """Convert local ENU coordinates to ECEF."""
    lat_rad = np.radians(ref_lat_deg)
    lon_rad = np.radians(ref_lon_deg)
    
    sin_lat = np.sin(lat_rad)
    cos_lat = np.cos(lat_rad)
    sin_lon = np.sin(lon_rad)
    cos_lon = np.cos(lon_rad)
    
    # Rotation matrix from ENU to ECEF (transpose of ECEF to ENU)
    R_inv = np.array([
        [-sin_lon, -sin_lat * cos_lon, cos_lat * cos_lon],
        [cos_lon, -sin_lat * sin_lon, cos_lat * sin_lon],
        [0, cos_lat, sin_lat]
    ])
    
    d_ecef = R_inv @ np.array([e, n, u])
    ref_ecef = lla_to_ecef(ref_lat_deg, ref_lon_deg, ref_alt_m)
    
    return ref_ecef + d_ecef
