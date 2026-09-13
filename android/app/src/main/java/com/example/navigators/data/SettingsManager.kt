package com.example.navigators.data

import android.content.Context
import android.content.SharedPreferences

class SettingsManager(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("navigators_settings", Context.MODE_PRIVATE)

    var isLocalOnlyMode: Boolean
        get() = prefs.getBoolean("local_only_mode", false)
        set(value) = prefs.edit().putBoolean("local_only_mode", value).apply()

    var lastSuccessfulSync: Long
        get() = prefs.getLong("last_successful_sync", 0L)
        set(value) = prefs.edit().putLong("last_successful_sync", value).apply()
        
    var lastSyncError: String?
        get() = prefs.getString("last_sync_error", null)
        set(value) = prefs.edit().putString("last_sync_error", value).apply()
}
