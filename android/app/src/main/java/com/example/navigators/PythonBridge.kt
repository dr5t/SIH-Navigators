package com.example.navigators

import com.chaquo.python.Python
import com.chaquo.python.PyObject

class PythonBridge {
    private val py: Python = Python.getInstance()
    private val fusionEngine: PyObject

    init {
        val module = py.getModule("navigation_core.engine")
        // Initialize with dummy reference LLA
        fusionEngine = module.callAttr("NavigationEngine", 37.7749, -122.4194, 10.0)
    }

    fun processImu(accel: FloatArray, gyro: FloatArray, dt: Double, timestamp: Double): Map<String, Any> {
        val state = fusionEngine.callAttr("process_imu", accel, gyro, dt, timestamp)
        return state.asMap().mapKeys { it.key.toString() }.mapValues { it.value.toString() }
    }

    fun processGnss(lat: Double, lon: Double, alt: Double, speed: Double, course: Double, hAcc: Double, timestamp: Double): Map<String, Any> {
        val state = fusionEngine.callAttr("process_gnss", lat, lon, alt, speed, course, hAcc, timestamp)
        return state.asMap().mapKeys { it.key.toString() }.mapValues { it.value.toString() }
    }
}
