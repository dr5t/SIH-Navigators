package com.isro.navigators

import com.chaquo.python.Python
import com.chaquo.python.PyObject

class PythonBridge {
    private val py: Python = Python.getInstance()
    private val fusionEngine: PyObject

    init {
        val module = py.getModule("navigation_core.fusion.gnss_fusion")
        // Initialize with dummy reference LLA
        fusionEngine = module.callAttr("GNSSFusionEngine", 37.7749, -122.4194, 10.0)
    }

    fun processImu(accel: FloatArray, gyro: FloatArray, dt: Double) {
        fusionEngine.callAttr("process_imu", accel, gyro, dt)
    }

    fun getPosition(): FloatArray {
        val state = fusionEngine.callAttr("get_state")
        val pos = state.asMap()[py.builtins.callAttr("str", "pos")]
        return pos?.toJava(FloatArray::class.java) ?: FloatArray(3)
    }
}
