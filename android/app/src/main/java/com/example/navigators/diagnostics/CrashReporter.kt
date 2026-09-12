package com.example.navigators.diagnostics

import android.content.Context
import android.util.Log
import com.example.navigators.data.TelemetryDatabase
import com.example.navigators.data.TelemetryEntity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlin.system.exitProcess

class CrashReporter(private val context: Context) : Thread.UncaughtExceptionHandler {
    private val defaultHandler = Thread.getDefaultUncaughtExceptionHandler()

    init {
        Thread.setDefaultUncaughtExceptionHandler(this)
    }

    override fun uncaughtException(thread: Thread, exception: Throwable) {
        Log.e("CrashReporter", "FATAL CRASH on thread ${thread.name}", exception)
        
        // Log crash as a telemetry event for syncing on next restart
        val db = TelemetryDatabase.getDatabase(context).telemetryDao()
        
        val crashData = TelemetryEntity(
            sessionId = "CRASH",
            timestamp = System.currentTimeMillis(),
            lat = 0.0,
            lon = 0.0,
            alt = 0.0,
            speed = 0.0,
            course = 0.0,
            hAcc = 0.0,
            vAcc = 0.0,
            mode = "CRASH: ${exception.message?.take(50)}"
        )
        
        // Use global scope because app is crashing
        CoroutineScope(Dispatchers.IO).launch {
            try {
                db.insert(crashData)
                Log.i("CrashReporter", "Crash event queued for cloud sync")
            } catch (e: Exception) {
                Log.e("CrashReporter", "Failed to queue crash event", e)
            } finally {
                // Let the default handler crash the app gracefully
                defaultHandler?.uncaughtException(thread, exception)
                exitProcess(1)
            }
        }
        
        // Block until coroutine finishes or times out (simplified for demo)
        Thread.sleep(1000)
        defaultHandler?.uncaughtException(thread, exception)
        exitProcess(1)
    }
}
