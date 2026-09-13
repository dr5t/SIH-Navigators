package com.example.navigators.sync

import android.content.Context
import android.util.Log
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.example.navigators.data.TelemetryDatabase
import com.example.navigators.data.TelemetryEntity
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

import com.example.navigators.data.SettingsManager

class TelemetrySyncWorker(
    private val appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val settingsManager = SettingsManager(appContext)
        if (settingsManager.isLocalOnlyMode) {
            Log.i("TelemetrySync", "Local-Only mode active. Sync skipped.")
            return@withContext Result.success()
        }

        val database = TelemetryDatabase.getDatabase(appContext)
        val dao = database.telemetryDao()

        try {
            // Drain up to 1000 points at a time
            val records = dao.getOldest(1000)
            if (records.isEmpty()) {
                return@withContext Result.success()
            }

            val success = pushToCloud(records)
            if (success) {
                dao.deleteByIds(records.map { it.id })
                Log.i("TelemetrySync", "Successfully synced ${records.size} points.")
                settingsManager.lastSuccessfulSync = System.currentTimeMillis()
                settingsManager.lastSyncError = null
                Result.success()
            } else {
                Log.w("TelemetrySync", "Failed to sync, will retry.")
                settingsManager.lastSyncError = "Network error or server unavailable"
                Result.retry()
            }
        } catch (e: Exception) {
            Log.e("TelemetrySync", "Error during sync", e)
            settingsManager.lastSyncError = e.message ?: "Unknown error"
            Result.retry()
        }
    }

    private fun pushToCloud(records: List<TelemetryEntity>): Boolean {
        // Group by session ID as the backend endpoint expects it
        val grouped = records.groupBy { it.sessionId }
        
        var allSuccess = true
        for ((sessionId, sessionRecords) in grouped) {
            val jsonArray = JSONArray()
            sessionRecords.forEach { record ->
                val obj = JSONObject().apply {
                    put("timestamp", record.timestamp)
                    put("latitude", record.lat)
                    put("longitude", record.lon)
                    put("altitude", record.alt)
                    put("speed", record.speed)
                    put("course", record.course)
                    put("h_acc", record.hAcc)
                    put("v_acc", record.vAcc)
                    put("mode", record.mode)
                }
                jsonArray.put(obj)
            }

            // In real app, URL comes from config
            val url = URL("http://10.0.2.2:8000/telemetry/batch?session_id=$sessionId")
            try {
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json; utf-8")
                conn.setRequestProperty("Accept", "application/json")
                
                // Demo Authentication Token (Group A & B implementation)
                // In production, fetch this from Android EncryptedSharedPreferences
                val dummyToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vX2RldmljZSJ9.this_is_a_mock_signature"
                conn.setRequestProperty("Authorization", "Bearer $dummyToken")
                
                conn.doOutput = true

                OutputStreamWriter(conn.outputStream).use { os ->
                    os.write(jsonArray.toString())
                    os.flush()
                }

                if (conn.responseCode !in 200..299) {
                    allSuccess = false
                }
            } catch (e: Exception) {
                Log.e("TelemetrySync", "Network error", e)
                allSuccess = false
            }
        }
        return allSuccess
    }
}
