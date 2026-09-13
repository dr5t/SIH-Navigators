package com.example.navigators

import com.chaquo.python.Python
import com.chaquo.python.PyObject

class PythonBridge(private val context: android.content.Context) {
    private val py by lazy { Python.getInstance() }
    
    // Engine is initialized dynamically when first GNSS point arrives to avoid hardcoded reference points
    private var fusionEngine: PyObject? = null

    private fun getOrInitEngine(lat: Double, lon: Double, alt: Double): PyObject {
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

    fun reset() { fusionEngine = null }

    fun processImu(accel: FloatArray, gyro: FloatArray, dt: Double, timestamp: Double, isExternal: Boolean = false): Map<String, Any> {
        // Dead reckoning needs a real geodetic origin. Wait for GNSS on a cold start.
        val engine = fusionEngine ?: return emptyMap()
        val state = engine.callAttr("process_imu", accel, gyro, dt, timestamp)
        return state.asMap().mapKeys { it.key.toString() }.mapValues { it.value.toString() }
    }

    fun processGnss(lat: Double, lon: Double, alt: Double, speed: Double, course: Double, hAcc: Double, timestamp: Double): Map<String, Any> {
        // Init with real GNSS location as reference if this is the first point
        val state = getOrInitEngine(lat, lon, alt).callAttr("process_gnss", lat, lon, alt, speed, course, hAcc, timestamp)
        return state.asMap().mapKeys { it.key.toString() }.mapValues { it.value.toString() }
    }
}
