import numpy as np
from typing import Tuple
from ml.datasets.io_vnbd import GnssData

def inject_gnss_blackout(gnss: GnssData, start_time: float, duration: float) -> Tuple[GnssData, GnssData]:
    """
    Simulates a GNSS blackout by splitting the GNSS data into 'available' 
    and 'blackout' (ground truth) segments.
    
    Args:
        gnss: The original GNSS data
        start_time: Start time of the blackout (relative to start of session or absolute)
        duration: Duration of the blackout in seconds
        
    Returns:
        available_gnss: GNSS data with the blackout region removed
        ground_truth: GNSS data ONLY from the blackout region
    """
    end_time = start_time + duration
    
    # Create masks
    blackout_mask = (gnss.timestamp >= start_time) & (gnss.timestamp <= end_time)
    available_mask = ~blackout_mask
    
    # Create available GNSS
    available_gnss = GnssData(
        timestamp=gnss.timestamp[available_mask],
        lat=gnss.lat[available_mask],
        lon=gnss.lon[available_mask],
        alt=gnss.alt[available_mask],
        speed=gnss.speed[available_mask],
        bearing=gnss.bearing[available_mask],
        accuracy=gnss.accuracy[available_mask]
    )
    
    # Create ground truth GNSS
    ground_truth = GnssData(
        timestamp=gnss.timestamp[blackout_mask],
        lat=gnss.lat[blackout_mask],
        lon=gnss.lon[blackout_mask],
        alt=gnss.alt[blackout_mask],
        speed=gnss.speed[blackout_mask],
        bearing=gnss.bearing[blackout_mask],
        accuracy=gnss.accuracy[blackout_mask]
    )
    
    return available_gnss, ground_truth
