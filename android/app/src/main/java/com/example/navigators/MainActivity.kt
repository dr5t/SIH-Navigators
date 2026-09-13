package com.example.navigators

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import org.osmdroid.config.Configuration
import com.example.navigators.theme.NavigatorsTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Critical Map fix: Initialize osmdroid configuration
        Configuration.getInstance().load(this, android.preference.PreferenceManager.getDefaultSharedPreferences(this))
        Configuration.getInstance().userAgentValue = packageName
        
        setContent {
            NavigatorsTheme {
                NavigatorsApp()
            }
        }
    }
}
