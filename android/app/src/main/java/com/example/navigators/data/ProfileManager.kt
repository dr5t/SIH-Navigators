package com.example.navigators.data

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL

data class VehicleProfile(
    val id: String,
    val name: String,
    val vehicleType: String,
    val phoneMounting: String,
    val isCalibrated: Boolean,
    val externalImu: Boolean
)

class ProfileManager(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("profiles_prefs", Context.MODE_PRIVATE)

    suspend fun fetchProfiles(): List<VehicleProfile> = withContext(Dispatchers.IO) {
        val list = mutableListOf<VehicleProfile>()
        try {
            // Note: 10.0.2.2 points to localhost of the host machine in Android Emulator
            val url = URL("http://10.0.2.2:8000/profiles")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "GET"
            // Use dummy token for demo
            val dummyToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vX2RldmljZSJ9.this_is_a_mock_signature"
            conn.setRequestProperty("Authorization", "Bearer $dummyToken")

            if (conn.responseCode == 200) {
                val response = InputStreamReader(conn.inputStream).readText()
                val jsonArray = JSONArray(response)
                for (i in 0 until jsonArray.length()) {
                    val obj = jsonArray.getJSONObject(i)
                    list.add(
                        VehicleProfile(
                            id = obj.getString("id"),
                            name = obj.getString("name"),
                            vehicleType = obj.getString("vehicle_type"),
                            phoneMounting = obj.getString("phone_mounting"),
                            isCalibrated = obj.getBoolean("is_calibrated"),
                            externalImu = obj.getBoolean("external_imu")
                        )
                    )
                }
            } else {
                Log.e("ProfileManager", "Failed to fetch profiles. Code: ${conn.responseCode}")
            }
        } catch (e: Exception) {
            Log.e("ProfileManager", "Network error", e)
        }
        return@withContext list
    }

    fun setActiveProfileId(id: String) {
        prefs.edit().putString("active_profile_id", id).apply()
    }

    fun getActiveProfileId(): String? {
        return prefs.getString("active_profile_id", null)
    }
    
    fun setProfileCalibrated(id: String, isCalibrated: Boolean) {
        prefs.edit().putBoolean("profile_calibrated_$id", isCalibrated).apply()
    }
    
    fun isProfileCalibrated(id: String): Boolean {
        return prefs.getBoolean("profile_calibrated_$id", false)
    }
}
