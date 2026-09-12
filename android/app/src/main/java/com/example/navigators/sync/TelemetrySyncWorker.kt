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

class TelemetrySyncWorker(
    private val appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
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
                Result.success()
            } else {
                Log.w("TelemetrySync", "Failed to sync, will retry.")
                Result.retry()
            }
        } catch (e: Exception) {
            Log.e("TelemetrySync", "Error during sync", e)
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
                    put("lat", record.lat)
                    put("lon", record.lon)
                    put("speed", record.speed)
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
