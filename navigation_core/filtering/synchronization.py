import numpy as np
from scipy.interpolate import interp1d
from ml.datasets.io_vnbd import ImuData, GnssData

def synchronize_imu(imu: ImuData, target_freq_hz: float = 100.0) -> ImuData:
    """
    Interpolates IMU data to a uniform target frequency.
    """
    if len(imu.timestamp) < 2:
        return imu
        
    start_time = imu.timestamp[0]
    end_time = imu.timestamp[-1]
    
    # Generate uniform timestamps
    target_timestamps = np.arange(start_time, end_time, 1.0 / target_freq_hz)
    
    # Interpolate accel
    interp_accel = interp1d(imu.timestamp, imu.accel, axis=0, bounds_error=False, fill_value="extrapolate")
    resampled_accel = interp_accel(target_timestamps)
    
    # Interpolate gyro
    interp_gyro = interp1d(imu.timestamp, imu.gyro, axis=0, bounds_error=False, fill_value="extrapolate")
    resampled_gyro = interp_gyro(target_timestamps)
    
    # Interpolate mag if present
    resampled_mag = None
    if imu.mag is not None:
        interp_mag = interp1d(imu.timestamp, imu.mag, axis=0, bounds_error=False, fill_value="extrapolate")
        resampled_mag = interp_mag(target_timestamps)
        
    return ImuData(
        timestamp=target_timestamps,
        accel=resampled_accel,
        gyro=resampled_gyro,
        mag=resampled_mag
    )

def align_gnss_to_imu(gnss: GnssData, imu_timestamps: np.ndarray) -> GnssData:
    """
    Interpolates GNSS data to match IMU timestamps using zero-order hold (previous value)
    for discrete fields and linear interpolation for continuous fields.
    """
    if len(gnss.timestamp) < 2:
        return gnss
        
    # Linear interpolation for continuous values
    interp_lat = interp1d(gnss.timestamp, gnss.lat, bounds_error=False, fill_value="extrapolate")
    interp_lon = interp1d(gnss.timestamp, gnss.lon, bounds_error=False, fill_value="extrapolate")
    interp_alt = interp1d(gnss.timestamp, gnss.alt, bounds_error=False, fill_value="extrapolate")
    
    # Zero-order hold (previous value) for speed, bearing, accuracy
    interp_speed = interp1d(gnss.timestamp, gnss.speed, kind='previous', bounds_error=False, fill_value="extrapolate")
    interp_bearing = interp1d(gnss.timestamp, gnss.bearing, kind='previous', bounds_error=False, fill_value="extrapolate")
    interp_accuracy = interp1d(gnss.timestamp, gnss.accuracy, kind='previous', bounds_error=False, fill_value="extrapolate")

    return GnssData(
        timestamp=imu_timestamps,
        lat=interp_lat(imu_timestamps),
        lon=interp_lon(imu_timestamps),
        alt=interp_alt(imu_timestamps),
        speed=interp_speed(imu_timestamps),
        bearing=interp_bearing(imu_timestamps),
        accuracy=interp_accuracy(imu_timestamps)
    )
