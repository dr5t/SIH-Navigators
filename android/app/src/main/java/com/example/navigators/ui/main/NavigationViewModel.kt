package com.example.navigators.ui.main

import android.annotation.SuppressLint
import android.app.Application
import android.content.Context
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.navigators.PythonBridge
import com.example.navigators.SensorRecorder
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class NavigationUiState(
    val isInitialized: Boolean = false,
    val isRunning: Boolean = false,
    val lat: Double = 0.0,
    val lon: Double = 0.0,
    val alt: Double = 0.0,
    val speed: Double = 0.0,
    val course: Double = 0.0,
    val mode: String = "IDLE",
    val posUncertainty: Double = 0.0,
    val explanation: String = "",
    val trajectory: List<Pair<Double, Double>> = emptyList()
)

class NavigationViewModel(application: Application) : AndroidViewModel(application), LocationListener {
    
    private val pythonBridge = PythonBridge(application)
    private val sensorRecorder = SensorRecorder(application)
    private val locationManager = application.getSystemService(Context.LOCATION_SERVICE) as LocationManager
    
    private val _uiState = MutableStateFlow(NavigationUiState())
    val uiState: StateFlow<NavigationUiState> = _uiState.asStateFlow()
    
    private var lastImuTime: Long = 0

    init {
        sensorRecorder.onImuData = { accel, gyro, timestampNs ->
            val timestampSec = timestampNs / 1_000_000_000.0
            val dt = if (lastImuTime == 0L) 0.01 else (timestampNs - lastImuTime) / 1_000_000_000.0
            lastImuTime = timestampNs
            
            // Only update via IMU if we are running to avoid battery drain
            if (_uiState.value.isRunning) {
                val state = pythonBridge.processImu(accel, gyro, dt, timestampSec)
                updateStateFromMap(state)
            }
        }
    }

    @SuppressLint("MissingPermission")
    fun startNavigation() {
        if (_uiState.value.isRunning) return
        
        _uiState.update { it.copy(isRunning = true) }
        
        // Start Sensors — wrapped in try-catch for device compatibility
        try {
            sensorRecorder.start()
        } catch (e: Exception) {
            android.util.Log.e("NavigationVM", "Failed to start sensors: ${e.message}")
        }
        
        // Start GNSS — wrapped in try-catch for device compatibility
        try {
            locationManager.requestLocationUpdates(
                LocationManager.GPS_PROVIDER,
                1000L,
                0f,
                this
            )
        } catch (e: Exception) {
            android.util.Log.e("NavigationVM", "Failed to start GNSS: ${e.message}")
        }
    }

    fun stopNavigation() {
        if (!_uiState.value.isRunning) return
        
        _uiState.update { it.copy(isRunning = false) }
        sensorRecorder.stop()
        locationManager.removeUpdates(this)
    }

    override fun onLocationChanged(location: Location) {
        val timestampSec = location.time / 1000.0
        val state = pythonBridge.processGnss(
            lat = location.latitude,
            lon = location.longitude,
            alt = location.altitude,
            speed = location.speed.toDouble(),
            course = location.bearing.toDouble(),
            hAcc = location.accuracy.toDouble(),
            timestamp = timestampSec
        )
        updateStateFromMap(state)
    }

    private fun updateStateFromMap(state: Map<String, Any>) {
        try {
            val lat = state["lat"].toString().toDoubleOrNull() ?: return
            val lon = state["lon"].toString().toDoubleOrNull() ?: return
            val alt = state["alt"].toString().toDoubleOrNull() ?: 0.0
            val speed = state["speed"].toString().toDoubleOrNull() ?: 0.0
            val course = state["course"].toString().toDoubleOrNull() ?: 0.0
            val mode = state["mode"].toString()
            val posUnc = state["pos_uncertainty"].toString().toDoubleOrNull() ?: 0.0
            val explanation = state["explanation"].toString()
            
            _uiState.update { current ->
                val newTraj = current.trajectory.toMutableList()
                // Use actual physical distance in meters (Location.distanceBetween)
                if (newTraj.isEmpty() || distanceMeters(newTraj.last(), Pair(lat, lon)) > 10.0) {
                    newTraj.add(Pair(lat, lon))
                }
                
                current.copy(
                    isInitialized = true,
                    lat = lat,
                    lon = lon,
                    alt = alt,
                    speed = speed,
                    course = course,
                    mode = mode,
                    posUncertainty = posUnc,
                    explanation = explanation,
                    trajectory = newTraj
                )
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    
    // Calculate physical distance in meters using Android Location API
    private fun distanceMeters(p1: Pair<Double, Double>, p2: Pair<Double, Double>): Float {
        val results = FloatArray(1)
        Location.distanceBetween(p1.first, p1.second, p2.first, p2.second, results)
        return results[0]
    }

    override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}
    override fun onProviderEnabled(provider: String) {}
    override fun onProviderDisabled(provider: String) {}

    override fun onCleared() {
        super.onCleared()
        stopNavigation()
    }
}
