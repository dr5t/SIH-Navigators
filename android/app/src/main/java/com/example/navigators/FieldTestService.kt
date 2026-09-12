package com.example.navigators

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import java.util.UUID

class FieldTestService : Service() {
    companion object {
        const val ACTION_START = "com.example.navigators.START_FIELD_TEST"
        const val ACTION_STOP = "com.example.navigators.STOP_FIELD_TEST"
        private const val CHANNEL_ID = "field_test_channel"
        private const val NOTIFICATION_ID = 101
        
        var currentSessionId: String? = null
            private set
            
        var isRunning: Boolean = false
            private set
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> {
                if (!isRunning) {
                    currentSessionId = "SESSION_" + UUID.randomUUID().toString()
                    isRunning = true
                    val notification = buildNotification()
                    startForeground(NOTIFICATION_ID, notification)
                    
                    // Trigger Navigation Engine or Data Logger to use this sessionId
                    // This could be a broadcast or a singleton update
                }
            }
            ACTION_STOP -> {
                isRunning = false
                currentSessionId = null
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }
        return START_STICKY
    }

    private fun buildNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Navigators Field Test Active")
            .setContentText("Recording telemetry in background (Session: ${currentSessionId?.takeLast(8)})")
            .setSmallIcon(R.mipmap.ic_launcher)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .build()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Field Test Recording",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Keeps navigation engine alive during field testing"
            }
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
