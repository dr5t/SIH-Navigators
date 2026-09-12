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

@Composable
fun DashboardScreen(navController: NavController) {
    Column(Modifier.padding(16.dp).fillMaxSize()) {
        Text("Dashboard", style = MaterialTheme.typography.titleLarge)
        Text("Real-time navigation and sensor overview.", color = TextMuted)
        
        Spacer(Modifier.height(24.dp))
        
        Card(
            modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
            colors = CardDefaults.cardColors(containerColor = BgSurfaceElevated)
        ) {
            Column(Modifier.padding(16.dp)) {
                Text("Navigation Status", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.height(8.dp))
                Surface(color = StatusSuccess.copy(alpha = 0.2f), shape = MaterialTheme.shapes.small) {
                    Text("GNSS + INS", color = StatusSuccess, modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp))
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
        
        Button(
            onClick = {
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

@Composable
fun SettingsScreen(navController: NavController) {
    val context = androidx.compose.ui.platform.LocalContext.current
    var isUpdating by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    
    Column(Modifier.padding(16.dp)) {
        Text("Settings", style = MaterialTheme.typography.titleLarge)
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
