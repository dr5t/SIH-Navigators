package com.example.navigators.ui.main
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.example.navigators.theme.*
import kotlinx.coroutines.launch
import com.example.navigators.data.ProfileManager
import com.example.navigators.data.VehicleProfile

@Composable
fun SettingsScreen(navController: NavController) {
    val context = androidx.compose.ui.platform.LocalContext.current
    var isUpdating by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    
    val profileManager = remember { ProfileManager(context) }
    var profiles by remember { mutableStateOf<List<VehicleProfile>>(emptyList()) }
    var activeProfileId by remember { mutableStateOf(profileManager.getActiveProfileId()) }
    var isLoadingProfiles by remember { mutableStateOf(true) }

    LaunchedEffect(Unit) {
        profiles = profileManager.fetchProfiles()
        isLoadingProfiles = false
    }
    
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp)) {
        Text("Settings", style = MaterialTheme.typography.titleLarge)
        Spacer(Modifier.height(16.dp))
        
        Text("Navigation & Sensors", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        Surface(
            modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
            color = BgSurfaceElevated,
            shape = MaterialTheme.shapes.small
        ) {
            Column(Modifier.padding(16.dp)) {
                if (isLoadingProfiles) {
                    Text("Loading profiles...")
                } else if (profiles.isEmpty()) {
                    Text("No profiles found. Create one in the Web Dashboard.")
                } else {
                    profiles.forEach { profile ->
                        Row(
                            verticalAlignment = androidx.compose.ui.Alignment.CenterVertically,
                            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)
                        ) {
                            RadioButton(
                                selected = (profile.id == activeProfileId),
                                onClick = { 
                                    activeProfileId = profile.id
                                    profileManager.setActiveProfileId(profile.id)
                                    profileManager.setProfileCalibrated(profile.id, profile.isCalibrated)
                                }
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Column {
                                Text(profile.name, fontWeight = FontWeight.Medium)
                                Text("${profile.vehicleType} • ${if(profile.isCalibrated) "Calibrated" else "Uncalibrated"}", style = MaterialTheme.typography.bodySmall, color = TextMuted)
                            }
                        }
                    }
                }
            }
        }

        Spacer(Modifier.height(16.dp))
        
        Text("AI", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        Surface(
            modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
            color = BgSurfaceElevated,
            shape = MaterialTheme.shapes.small
        ) {
            Column(Modifier.padding(16.dp)) {
                Text("Model updates", fontWeight = FontWeight.Medium)
                Text("Inference availability is reported in Diagnostics.", color = TextSecondary)
                Spacer(Modifier.height(8.dp))
                Button(
                    onClick = {
                        scope.launch {
                            isUpdating = true
                            val manager = com.example.navigators.ai.ModelManager(context)
                            val success = manager.checkAndUpdateModel()
                            isUpdating = false
                            if (success) {
                                android.widget.Toast.makeText(context, "Model updated successfully", android.widget.Toast.LENGTH_SHORT).show()
                            } else {
                                android.widget.Toast.makeText(context, "Failed to update model", android.widget.Toast.LENGTH_SHORT).show()
                            }
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !isUpdating
                ) {
                    Text(if (isUpdating) "Downloading..." else "Check for Updates")
                }
            }
        }
        
        Spacer(Modifier.height(16.dp))
        
        Text("Data & Privacy", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        Surface(
            modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
            color = BgSurfaceElevated,
            shape = MaterialTheme.shapes.small
        ) {
            val settingsManager = remember { com.example.navigators.data.SettingsManager(context) }
            var isLocalOnly by remember { mutableStateOf(settingsManager.isLocalOnlyMode) }
            var pendingCount by remember { mutableStateOf(0) }
            var showClearDialog by remember { mutableStateOf(false) }
            
            LaunchedEffect(Unit) {
                try {
                    kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
                        val db = com.example.navigators.data.TelemetryDatabase.getDatabase(context)
                        pendingCount = db.telemetryDao().count()
                    }
                } catch (e: Exception) {
                    android.util.Log.e("SettingsScreen", "Failed to access TelemetryDatabase: ${e.message}")
                    pendingCount = -1
                }
            }

            Column(Modifier.padding(16.dp)) {
                Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically, modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Column(Modifier.weight(1f)) {
                        Text("Cloud Sync (Local-Only Mode)", fontWeight = FontWeight.Medium)
                        Text(if (isLocalOnly) "OFF - Data remains local" else "ON - Data syncs to cloud", color = TextMuted, style = MaterialTheme.typography.bodySmall)
                    }
                    Switch(
                        checked = !isLocalOnly,
                        onCheckedChange = { 
                            isLocalOnly = !it
                            settingsManager.isLocalOnlyMode = isLocalOnly
                        }
                    )
                }
                Spacer(Modifier.height(16.dp))
                
                Text("Pending Uploads: $pendingCount", style = MaterialTheme.typography.bodyMedium)
                val lastSyncStr = if (settingsManager.lastSuccessfulSync > 0) java.text.SimpleDateFormat("MMM dd, HH:mm", java.util.Locale.getDefault()).format(java.util.Date(settingsManager.lastSuccessfulSync)) else "Never"
                Text("Last Successful Sync: $lastSyncStr", style = MaterialTheme.typography.bodyMedium)
                settingsManager.lastSyncError?.let {
                    Text("Sync Error: $it", color = StatusError, style = MaterialTheme.typography.bodyMedium)
                }
                
                Spacer(Modifier.height(16.dp))
                Button(
                    onClick = { showClearDialog = true },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = StatusError)
                ) {
                    Text("Clear Local Data")
                }
                
                if (showClearDialog) {
                    AlertDialog(
                        onDismissRequest = { showClearDialog = false },
                        title = { Text("Delete local data?") },
                        text = { Text("Clear all pending local telemetry data? This cannot be undone.") },
                        confirmButton = {
                            Button(
                                onClick = { 
                                    scope.launch(kotlinx.coroutines.Dispatchers.IO) {
                                        try {
                                            val db = com.example.navigators.data.TelemetryDatabase.getDatabase(context)
                                            db.telemetryDao().clearAll()
                                            pendingCount = 0
                                        } catch (e: Exception) {
                                            android.util.Log.e("SettingsScreen", "Failed to clear DB: ${e.message}")
                                        }
                                    }
                                    showClearDialog = false 
                                },
                                colors = ButtonDefaults.buttonColors(containerColor = StatusError)
                            ) {
                                Text("Delete")
                            }
                        },
                        dismissButton = {
                            Button(onClick = { showClearDialog = false }) {
                                Text("Cancel")
                            }
                        }
                    )
                }
            }
        }
        
        Spacer(Modifier.height(16.dp))
        Text("Maps", style = MaterialTheme.typography.titleMedium)
        Text("Viewed map tiles are stored on this device. Offline coverage depends on the areas and zoom levels you have visited. Cache limit: 128 MB.", color = TextSecondary, modifier = Modifier.padding(vertical = 12.dp))
        Text("Appearance", style = MaterialTheme.typography.titleMedium)
        Text("Night instruments · high contrast", color = TextSecondary, modifier = Modifier.padding(vertical = 12.dp))
        Text("About", style = MaterialTheme.typography.titleMedium)
        Text("NAVIGATORS · Developed by Navigators", color = TextSecondary, modifier = Modifier.padding(vertical = 12.dp))
        Button(onClick = { navController.navigate("feedback_center") }, modifier = Modifier.fillMaxWidth()) { Text("Feedback & Support") }
        Spacer(Modifier.height(8.dp))
        Button(onClick = { navController.navigate("faq") }, modifier = Modifier.fillMaxWidth()) { Text("FAQ") }
        Spacer(Modifier.height(8.dp))
        Button(onClick = { navController.navigate("privacy") }, modifier = Modifier.fillMaxWidth()) { Text("Privacy Policy") }
        Spacer(Modifier.height(8.dp))
        Button(onClick = { navController.navigate("terms") }, modifier = Modifier.fillMaxWidth()) { Text("Terms & Conditions") }
        Spacer(Modifier.height(8.dp))
        Button(onClick = { navController.navigate("cookies") }, modifier = Modifier.fillMaxWidth()) { Text("Cookie Policy") }
    }
}

@Composable
fun FaqScreen() {
    Column(Modifier.padding(16.dp)) {
        Text("FAQ", style = MaterialTheme.typography.titleLarge)
        Text("Help and questions.", color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
fun LegalScreen(title: String) {
    Column(Modifier.padding(16.dp)) {
        Text(title, style = MaterialTheme.typography.titleLarge)
        Text("Legal terms.", color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}
