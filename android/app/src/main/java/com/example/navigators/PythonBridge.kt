package com.example.navigators

import com.chaquo.python.Python
import com.chaquo.python.PyObject

class PythonBridge(private val context: android.content.Context) {
    private val py by lazy { Python.getInstance() }
    private val fusionEngine by lazy {
        val module = py.getModule("navigation_core.engine")
        val engine = module.callAttr("NavigationEngine", 37.7749, -122.4194, 10.0)
        
        // Load active profile calibration
        val profileManager = com.example.navigators.data.ProfileManager(context)
        val activeId = profileManager.getActiveProfileId()
        val isCalibrated = activeId != null && profileManager.isProfileCalibrated(activeId)
        
        // We could pass alignment params here if we had them saved in SharedPreferences. 
        // For now, we pass the calibration boolean.
        engine.callAttr("load_calibration", isCalibrated, null)
        
        engine
    }

    fun processImu(accel: FloatArray, gyro: FloatArray, dt: Double, timestamp: Double, isExternal: Boolean = false): Map<String, Any> {
        val state = fusionEngine.callAttr("process_imu", accel, gyro, dt, timestamp, isExternal)
        return state.asMap().mapKeys { it.key.toString() }.mapValues { it.value.toString() }
    }

    fun processGnss(lat: Double, lon: Double, alt: Double, speed: Double, course: Double, hAcc: Double, timestamp: Double): Map<String, Any> {
        val state = fusionEngine.callAttr("process_gnss", lat, lon, alt, speed, course, hAcc, timestamp)
        return state.asMap().mapKeys { it.key.toString() }.mapValues { it.value.toString() }
    }
}
