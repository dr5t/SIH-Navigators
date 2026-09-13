package com.example.navigators

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.util.Log

class SensorRecorder(context: Context) : SensorEventListener {
    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val accel = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
    private val gyro = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)
    
    var onImuData: ((FloatArray, FloatArray, Long) -> Unit)? = null
    
    private var lastAccel: FloatArray? = null
    
    fun start() {
        // Try SENSOR_DELAY_FASTEST first, fall back to SENSOR_DELAY_GAME if
        // the HIGH_SAMPLING_RATE_SENSORS permission is not granted on Android 12+
        try {
            if (accel != null) {
                sensorManager.registerListener(this, accel, SensorManager.SENSOR_DELAY_FASTEST)
            } else {
                Log.w("SensorRecorder", "Accelerometer not available on this device")
            }
            if (gyro != null) {
                sensorManager.registerListener(this, gyro, SensorManager.SENSOR_DELAY_FASTEST)
            } else {
                Log.w("SensorRecorder", "Gyroscope not available on this device")
            }
        } catch (e: SecurityException) {
            // HIGH_SAMPLING_RATE_SENSORS not granted — fall back to SENSOR_DELAY_GAME (~20ms)
            Log.w("SensorRecorder", "SENSOR_DELAY_FASTEST denied, falling back to SENSOR_DELAY_GAME: ${e.message}")
            sensorManager.unregisterListener(this)
            try {
                accel?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_GAME) }
                gyro?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_GAME) }
            } catch (e2: Exception) {
                Log.e("SensorRecorder", "Failed to register sensors even with SENSOR_DELAY_GAME: ${e2.message}")
            }
        } catch (e: Exception) {
            Log.e("SensorRecorder", "Unexpected error registering sensors: ${e.message}")
        }
    }
    
    fun stop() {
        try {
            sensorManager.unregisterListener(this)
        } catch (e: Exception) {
            Log.e("SensorRecorder", "Error unregistering sensors: ${e.message}")
        }
    }

    override fun onSensorChanged(event: SensorEvent) {
        if (event.sensor.type == Sensor.TYPE_ACCELEROMETER) {
            lastAccel = event.values.clone()
        } else if (event.sensor.type == Sensor.TYPE_GYROSCOPE) {
            lastAccel?.let { a ->
                onImuData?.invoke(a, event.values.clone(), event.timestamp)
            }
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
}
