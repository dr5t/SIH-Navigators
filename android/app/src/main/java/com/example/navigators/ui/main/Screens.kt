package com.example.navigators.ui.main

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.example.navigators.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(navController: NavController) {
    val context = androidx.compose.ui.platform.LocalContext.current
    val settingsManager = remember { com.example.navigators.data.SettingsManager(context) }
    
    Column(Modifier.padding(16.dp).fillMaxSize()) {
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
            Column {
                Text("Dashboard", style = MaterialTheme.typography.titleLarge)
                Text("Real-time navigation and sensor overview.", color = TextMuted)
            }
            if (settingsManager.isLocalOnlyMode) {
                Surface(
                    color = StatusWarning.copy(alpha = 0.2f), 
                    shape = MaterialTheme.shapes.small
                ) {
                    Text("Cloud Sync Disabled", color = StatusWarning, modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp), style = MaterialTheme.typography.labelSmall)
                }
            }
        }
        
        Spacer(Modifier.height(24.dp))
        
        var showExplanation by remember { mutableStateOf(false) }
        val mockExplanation = mapOf(
            "confidence" to "LOW",
            "reasons" to listOf("GNSS unavailable or rejected", "Position uncertainty increased to 31 m"),
            "mitigations" to listOf("AI speed active", "Vehicle constraints active"),
            "actions" to listOf("Run Diagnostics", "Check GNSS", "Recalibrate")
        )

        Card(
            modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
            colors = CardDefaults.cardColors(containerColor = BgSurfaceElevated)
        ) {
            Column(Modifier.padding(16.dp)) {
                Text("Navigation Status", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.height(8.dp))
                Surface(
                    onClick = { showExplanation = true },
                    color = StatusError.copy(alpha = 0.2f), 
                    shape = MaterialTheme.shapes.small
                ) {
                    Text("Confidence: LOW", color = StatusError, modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp))
                }
            }
        }

        if (showExplanation) {
            ModalBottomSheet(onDismissRequest = { showExplanation = false }) {
                Column(Modifier.padding(16.dp).padding(bottom = 32.dp)) {
                    Text("Navigation Status", style = MaterialTheme.typography.titleLarge)
                    Text("Confidence: ${mockExplanation["confidence"]}", color = StatusError, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 16.dp))
                    
                    Text("Reasons:", fontWeight = FontWeight.SemiBold)
                    (mockExplanation["reasons"] as List<String>).forEach {
                        Text("• $it", color = TextSecondary, modifier = Modifier.padding(start = 8.dp, bottom = 4.dp))
                    }
                    
                    Spacer(Modifier.height(16.dp))
                    Text("Current Mitigation:", fontWeight = FontWeight.SemiBold)
                    (mockExplanation["mitigations"] as List<String>).forEach {
                        Text("✓ $it", color = StatusSuccess, modifier = Modifier.padding(start = 8.dp, bottom = 4.dp))
                    }
                    
                    Spacer(Modifier.height(24.dp))
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        (mockExplanation["actions"] as List<String>).forEach { action ->
                            Button(onClick = { showExplanation = false }, modifier = Modifier.weight(1f)) {
                                Text(action)
                            }
                        }
                    }
                }
            }
        }
        
        Card(
            modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
            colors = CardDefaults.cardColors(containerColor = BgSurfaceElevated)
        ) {
            Column(Modifier.padding(16.dp)) {
                Text("Current Telemetry", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.height(8.dp))
                Text("45 km/h", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                Text("Heading: 270° (W)", color = TextSecondary)
            }
        }
        
        Card(
            modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
            colors = CardDefaults.cardColors(containerColor = BgSurfaceElevated)
        ) {
            Column(Modifier.padding(16.dp)) {
                Text("Sensor Health", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.height(8.dp))
                Surface(color = StatusWarning.copy(alpha = 0.2f), shape = MaterialTheme.shapes.small) {
                    Text("Diagnostics Required", color = StatusWarning, modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp))
                }
            }
        }
        
        Spacer(Modifier.weight(1f))
        
        // Field Test Controls
        var isTesting by remember { mutableStateOf(false) }
        val context = androidx.compose.ui.platform.LocalContext.current
        var showCalibrationWarning by remember { mutableStateOf(false) }
        
        if (showCalibrationWarning) {
            AlertDialog(
                onDismissRequest = { showCalibrationWarning = false },
                title = { Text("Calibration Required") },
                text = { Text("The currently selected vehicle profile is not calibrated or missing. Please calibrate your device first or select a calibrated profile before starting navigation.") },
                confirmButton = {
                    Button(onClick = { showCalibrationWarning = false }) {
                        Text("OK")
                    }
                }
            )
        }
        
        Button(
            onClick = {
                val profileManager = com.example.navigators.data.ProfileManager(context)
                val activeProfileId = profileManager.getActiveProfileId()
                
                if (!isTesting && (activeProfileId == null || !profileManager.isProfileCalibrated(activeProfileId))) {
                    showCalibrationWarning = true
                    return@Button
                }

                val intent = android.content.Intent(context, Class.forName("com.example.navigators.FieldTestService"))
                if (isTesting) {
                    intent.action = "com.example.navigators.STOP_FIELD_TEST"
                    context.startService(intent)
                    isTesting = false
                    navController.navigate("summary/latest")
                } else {
                    intent.action = "com.example.navigators.START_FIELD_TEST"
                    if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                        context.startForegroundService(intent)
                    } else {
                        context.startService(intent)
                    }
                    isTesting = true
                }
            },
            modifier = Modifier.fillMaxWidth().height(56.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = if (isTesting) MaterialTheme.colorScheme.error else BrandPrimary
            )
        ) {
            Text(
                if (isTesting) "STOP FIELD TEST" else "START FIELD TEST",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@Composable
fun NavigationScreen() {
    Column(Modifier.fillMaxSize()) {
        Column(Modifier.padding(16.dp)) {
            Text("Navigation", style = MaterialTheme.typography.titleLarge)
            Text("Live vehicle telemetry and map view.", color = TextMuted)
        }
        
        Box(Modifier.fillMaxSize().weight(1f)) {
            // Placeholder for real map (e.g., osmdroid or Google Maps)
            Surface(color = BgSurfaceElevated, modifier = Modifier.fillMaxSize()) {
                Box(contentAlignment = androidx.compose.ui.Alignment.Center) {
                    Text("Map Rendering Engine", color = TextSecondary)
                }
            }
            
            // HUD
            Surface(
                color = BgSurfaceElevated,
                shape = MaterialTheme.shapes.medium,
                modifier = Modifier.padding(16.dp).align(androidx.compose.ui.Alignment.BottomStart)
            ) {
                Row(Modifier.padding(16.dp)) {
                    Column {
                        Text("Current Speed", color = TextMuted, style = MaterialTheme.typography.labelSmall)
                        Text("45 km/h", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
                    }
                    Spacer(Modifier.width(24.dp))
                    Column {
                        Text("Map Matching", color = TextMuted, style = MaterialTheme.typography.labelSmall)
                        Text("Active (92%)", color = StatusSuccess, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                        Text("Road: Main St", color = TextMuted, style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
    }
}

@Composable
fun DiagnosticsScreen() {
    var isRunning by remember { mutableStateOf(false) }
    
    Column(Modifier.padding(16.dp).fillMaxSize()) {
        Text("System Diagnostics", style = MaterialTheme.typography.titleLarge)
        Text("Validate sensor hardware.", color = TextMuted)
        
        Spacer(Modifier.height(24.dp))
        
        Button(
            onClick = { isRunning = true },
            modifier = Modifier.fillMaxWidth(),
            enabled = !isRunning
        ) {
            Text(if (isRunning) "Running..." else "Run Diagnostics")
        }
        
        Spacer(Modifier.height(24.dp))
        
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = BgSurfaceElevated)
        ) {
            Column(Modifier.padding(16.dp)) {
                Text("Hardware Status", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.height(16.dp))
                
                DiagnosticRow("Accelerometer (INS)", "Optimal", true)
                DiagnosticRow("Gyroscope (INS)", "Optimal", true)
                DiagnosticRow("Magnetometer", "Calibrating...", false)
                DiagnosticRow("GNSS Receiver", "Optimal", true)
            }
        }
    }
}

@Composable
fun DiagnosticRow(name: String, status: String, isSuccess: Boolean) {
    Row(
        Modifier.fillMaxWidth().padding(vertical = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = androidx.compose.ui.Alignment.CenterVertically
    ) {
        Text(name, fontWeight = FontWeight.Medium)
        Surface(
            color = if (isSuccess) StatusSuccess.copy(alpha = 0.2f) else StatusWarning.copy(alpha = 0.2f),
            shape = MaterialTheme.shapes.small
        ) {
            Text(
                text = status,
                color = if (isSuccess) StatusSuccess else StatusWarning,
                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                style = MaterialTheme.typography.labelSmall
            )
        }
    }
}

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
    
    Column(Modifier.padding(16.dp)) {
        Text("Settings", style = MaterialTheme.typography.titleLarge)
        Spacer(Modifier.height(16.dp))
        
        Text("Vehicle & Sensor Profiles", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        Card(
            modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
            colors = CardDefaults.cardColors(containerColor = BgSurfaceElevated)
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
        
        Text("AI Navigation Models", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        Card(
            modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
            colors = CardDefaults.cardColors(containerColor = BgSurfaceElevated)
        ) {
            Column(Modifier.padding(16.dp)) {
                Text("Current Version: v1.0-base")
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
        
        Text("Data & Privacy Controls", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        Card(
            modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
            colors = CardDefaults.cardColors(containerColor = BgSurfaceElevated)
        ) {
            val settingsManager = remember { com.example.navigators.data.SettingsManager(context) }
            var isLocalOnly by remember { mutableStateOf(settingsManager.isLocalOnlyMode) }
            var pendingCount by remember { mutableStateOf(0) }
            var showClearDialog by remember { mutableStateOf(false) }
            
            LaunchedEffect(Unit) {
                kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
                    val db = com.example.navigators.data.TelemetryDatabase.getDatabase(context)
                    pendingCount = db.telemetryDao().count()
                }
            }

            Column(Modifier.padding(16.dp)) {
                Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically, modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Column {
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
                                        val db = com.example.navigators.data.TelemetryDatabase.getDatabase(context)
                                        db.telemetryDao().clearAll()
                                        pendingCount = 0
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
