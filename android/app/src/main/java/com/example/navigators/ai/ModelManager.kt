package com.example.navigators.ai

import android.content.Context
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

class ModelManager(private val context: Context) {
    private val modelDir = File(context.filesDir, "models")
    
    init {
        if (!modelDir.exists()) {
            modelDir.mkdirs()
        }
    }

    suspend fun checkAndUpdateModel(): Boolean = withContext(Dispatchers.IO) {
        try {
            val url = URL("http://10.0.2.2:8000/models/latest")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "GET"
            
            if (conn.responseCode == 200) {
                val response = conn.inputStream.bufferedReader().readText()
                val json = JSONObject(response)
                
                val version = json.getString("version")
                val downloadUrl = json.getString("url")
                val expectedHash = json.getString("checksum")
                
                val modelFile = File(modelDir, "speed_estimator_$version.pt")
                if (modelFile.exists()) {
                    val currentHash = calculateSHA256(modelFile)
                    if (currentHash == expectedHash) {
                        Log.i("ModelManager", "Latest model already installed")
                        return@withContext true
                    }
                }
                
                Log.i("ModelManager", "Downloading new model: $version")
                val downloaded = downloadFile(downloadUrl, modelFile)
                if (downloaded) {
                    val newHash = calculateSHA256(modelFile)
                    if (newHash == expectedHash) {
                        Log.i("ModelManager", "Model validated successfully")
                        // Perform trial inference here (e.g. via Chaquopy)
                        // If it fails, delete modelFile and return false.
                        return@withContext true
                    } else {
                        Log.e("ModelManager", "Model checksum failed. Expected: $expectedHash, Got: $newHash")
                        modelFile.delete()
                    }
                }
            }
        } catch (e: Exception) {
            Log.e("ModelManager", "Failed to check/update model", e)
        }
        return@withContext false
    }
    
    private fun downloadFile(urlStr: String, dest: File): Boolean {
        try {
            val url = URL(urlStr)
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "GET"
            
            if (conn.responseCode == 200) {
                conn.inputStream.use { input ->
                    FileOutputStream(dest).use { output ->
                        input.copyTo(output)
                    }
                }
                return true
            }
        } catch (e: Exception) {
            Log.e("ModelManager", "Failed to download file", e)
        }
        return false
    }
    
    private fun calculateSHA256(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        val fis = file.inputStream()
        val buffer = ByteArray(8192)
        var read = 0
        while (fis.read(buffer).also { read = it } > 0) {
            digest.update(buffer, 0, read)
        }
        fis.close()
        return digest.digest().joinToString("") { "%02x".format(it) }
    }
}
