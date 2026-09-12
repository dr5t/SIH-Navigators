package com.example.navigators.diagnostics

import android.content.Context
import android.os.PowerManager
import android.util.Log

class ThermalMonitor(private val context: Context) {
    private val powerManager: PowerManager? = context.getSystemService(Context.POWER_SERVICE) as? PowerManager

    var onThermalStatusChanged: ((Int) -> Unit)? = null

    private val thermalListener = PowerManager.OnThermalStatusChangedListener { status ->
        Log.w("ThermalMonitor", "Thermal status changed to: $status")
        onThermalStatusChanged?.invoke(status)
        
        when (status) {
            PowerManager.THERMAL_STATUS_SEVERE, 
            PowerManager.THERMAL_STATUS_CRITICAL -> {
                Log.e("ThermalMonitor", "CRITICAL OVERHEAT. Throttling sensors.")
                // In a full implementation, this callback would trigger NavigationEngine
                // to lower camera/ML framerates or reduce GNSS polling frequency.
            }
            PowerManager.THERMAL_STATUS_MODERATE -> {
                Log.w("ThermalMonitor", "Moderate heat. Disabling background heavy sync.")
            }
        }
    }

    fun startMonitoring() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.Q) {
            powerManager?.addThermalStatusListener(thermalListener)
        }
    }

    fun stopMonitoring() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.Q) {
            powerManager?.removeThermalStatusListener(thermalListener)
        }
    }
}
