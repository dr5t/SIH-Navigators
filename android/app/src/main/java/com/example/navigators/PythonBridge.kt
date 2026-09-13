package com.example.navigators

import com.chaquo.python.Python
import com.chaquo.python.PyObject

class PythonBridge(private val context: android.content.Context) {
    private val py by lazy { Python.getInstance() }
    
    // Engine is initialized dynamically when first GNSS point arrives to avoid hardcoded reference points
    private var fusionEngine: PyObject? = null

    private fun getOrInitEngine(lat: Double = 0.0, lon: Double = 0.0, alt: Double = 0.0): PyObject {
        if (fusionEngine == null) {
            val module = py.getModule("navigation_core.engine")
            val engine = module.callAttr("NavigationEngine", lat, lon, alt)
            
            val profileManager = com.example.navigators.data.ProfileManager(context)
            val activeId = profileManager.getActiveProfileId()
            val isCalibrated = activeId != null && profileManager.isProfileCalibrated(activeId)
            
            engine.callAttr("load_calibration", isCalibrated, null)
            fusionEngine = engine
        }
        return fusionEngine!!
    }

    fun processImu(accel: FloatArray, gyro: FloatArray, dt: Double, timestamp: Double, isExternal: Boolean = false): Map<String, Any> {
        // If engine isn't initialized by GNSS yet, initialize with 0,0,0 reference. 
        // In a real flow, you might want to wait for GNSS, but for DR-only starts we need an engine.
        val state = getOrInitEngine().callAttr("process_imu", accel, gyro, dt, timestamp, isExternal)
        return state.asMap().mapKeys { it.key.toString() }.mapValues { it.value.toString() }
    }

    fun processGnss(lat: Double, lon: Double, alt: Double, speed: Double, course: Double, hAcc: Double, timestamp: Double): Map<String, Any> {
        // Init with real GNSS location as reference if this is the first point
        val state = getOrInitEngine(lat, lon, alt).callAttr("process_gnss", lat, lon, alt, speed, course, hAcc, timestamp)
        return state.asMap().mapKeys { it.key.toString() }.mapValues { it.value.toString() }
    }
}
