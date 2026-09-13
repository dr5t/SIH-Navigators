package com.example.navigators.sync

import android.content.Context
import android.util.Log
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.example.navigators.data.FeedbackDatabase
import com.example.navigators.data.FeedbackEntity
import com.example.navigators.data.SettingsManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.io.OutputStreamWriter

class FeedbackSyncWorker(
    private val appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val settingsManager = SettingsManager(appContext)
        if (settingsManager.isLocalOnlyMode) {
            Log.i("FeedbackSync", "Local-Only mode active. Sync skipped.")
            return@withContext Result.success()
        }

        val database = FeedbackDatabase.getDatabase(appContext)
        val dao = database.feedbackDao()

        try {
            val records = dao.getAll()
            if (records.isEmpty()) {
                return@withContext Result.success()
            }
            
            val successfullyUploaded = mutableListOf<Int>()
            for (record in records) {
                if (pushToCloud(record)) {
                    successfullyUploaded.add(record.id)
                }
            }

            if (successfullyUploaded.isNotEmpty()) {
                dao.deleteByIds(successfullyUploaded)
                Log.i("FeedbackSync", "Successfully synced ${successfullyUploaded.size} reports.")
                Result.success()
            } else {
                Log.w("FeedbackSync", "Failed to sync, will retry.")
                Result.retry()
            }
        } catch (e: Exception) {
            Log.e("FeedbackSync", "Error during sync", e)
            Result.retry()
        }
    }

    private fun pushToCloud(record: FeedbackEntity): Boolean {
        return try {
            val url = URL("http://10.0.2.2:8000/feedback")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json")
            conn.setRequestProperty("Authorization", "Bearer MOCK_TOKEN_DEMO_DEVICE")
            conn.doOutput = true

            val json = JSONObject().apply {
                put("category", record.category)
                put("description", record.description)
                put("severity", record.severity)
                if (record.sessionId != null) put("session_id", record.sessionId)
                if (record.rating != null) put("rating", record.rating)
                if (record.technicalContextJson != null) {
                    put("technical_context", JSONObject(record.technicalContextJson))
                }
            }

            OutputStreamWriter(conn.outputStream).use { it.write(json.toString()) }

            val code = conn.responseCode
            conn.disconnect()
            code in 200..299
        } catch (e: Exception) {
            Log.e("FeedbackSync", "Failed to push feedback to cloud", e)
            false
        }
    }
}
