package com.example.navigators.ui.main

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.example.navigators.data.SummaryGenerator
import com.example.navigators.data.TelemetryDatabase
import com.example.navigators.data.TripSummary
import com.example.navigators.theme.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SummaryScreen(navController: NavController) {
    val context = androidx.compose.ui.platform.LocalContext.current
    val scope = rememberCoroutineScope()
    var summary by remember { mutableStateOf<TripSummary?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    var selectedCategory by remember { mutableStateOf<String?>(null) }
    val categories = listOf("GNSS", "DR", "AI", "Sensors", "Map", "Fusion", "Errors")

    LaunchedEffect(Unit) {
        scope.launch {
            val db = TelemetryDatabase.getDatabase(context).telemetryDao()
            // We just grab the latest session's points, or all points if session ID isn't strictly filtered for demo
            val points = withContext(Dispatchers.IO) {
                db.getOldest(10000) 
            }
            summary = SummaryGenerator.generateSummary(points)
            isLoading = false
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Smart Trip Summary") },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        if (isLoading) {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else if (summary != null) {
            LazyColumn(
                Modifier.padding(innerPadding).padding(16.dp).fillMaxSize(),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                item {
                    val quality = summary!!.quality
                    if (quality.unavailable) {
                        Text("Trip Quality", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                        Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = BgSurfaceElevated)) {
                            Column(Modifier.padding(16.dp)) {
                                Text("Quality score unavailable — insufficient session data.", color = TextMuted)
                            }
                        }
                    } else {
                        Text("Navigation Quality", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                        Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = BgSurfaceElevated)) {
                            Column(Modifier.padding(16.dp)) {
                                val scoreColor = when {
                                    quality.overallScore >= 90 -> StatusSuccess
                                    quality.overallScore >= 60 -> StatusWarning
                                    else -> MaterialTheme.colorScheme.error
                                }
                                Text("${quality.overallScore} / 100", style = MaterialTheme.typography.headlineMedium, color = scoreColor, fontWeight = FontWeight.Bold)
                                Spacer(Modifier.height(16.dp))
                                
                                SummaryRow("GNSS Quality", "${quality.gnssScore}")
                                SummaryRow("DR Stability", "${quality.drScore}")
                                SummaryRow("Data Completeness", "${quality.completenessScore}")
                                SummaryRow("System Interruptions", "${quality.interruptionsScore}")
                                
                                Spacer(Modifier.height(16.dp))
                                quality.explanation.forEach { msg ->
                                    Text("• $msg", style = MaterialTheme.typography.bodySmall, color = TextMuted)
                                }
                            }
                        }
                    }
                }

                item {
                    Text("Overview", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                    Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = BgSurfaceElevated)) {
                        Column(Modifier.padding(16.dp)) {
                            SummaryRow("Distance", String.format("%.2f km", summary!!.totalDistanceMeters / 1000))
                            SummaryRow("Duration", "${summary!!.durationSec / 60} min")
                        }
                    }
                }

                item {
                    Text("Navigation", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                    Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = BgSurfaceElevated)) {
                        Column(Modifier.padding(16.dp)) {
                            SummaryRow("GNSS Outages", "${summary!!.outages}")
                            SummaryRow("GNSS Time", "${summary!!.gnssTimeSec / 60} min")
                            SummaryRow("DR Distance", String.format("%.2f km", summary!!.drDistanceMeters / 1000))
                        }
                    }
                }

                item {
                    Text("Performance", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                    Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = BgSurfaceElevated)) {
                        Column(Modifier.padding(16.dp)) {
                            SummaryRow("Avg Speed", String.format("%.1f km/h", summary!!.avgSpeedMps * 3.6))
                            SummaryRow("Max Speed", String.format("%.1f km/h", summary!!.maxSpeedMps * 3.6))
                            SummaryRow("Max Uncertainty", String.format("%.1f m", summary!!.maxUncertaintyMeters))
                        }
                    }
                }
                
                item {
                    Text("System", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                    Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = BgSurfaceElevated)) {
                        Column(Modifier.padding(16.dp)) {
                            SummaryRow("Sensors", "Optimal", isStatus = true, statusColor = StatusSuccess)
                            SummaryRow("Sync", "Pending", isStatus = true, statusColor = StatusWarning)
                        }
                    }
                }

                item {
                    Column {
                        Text("Navigation Event Timeline", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                        Spacer(Modifier.height(8.dp))
                        androidx.compose.foundation.lazy.LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            item {
                                FilterChip(
                                    selected = selectedCategory == null,
                                    onClick = { selectedCategory = null },
                                    label = { Text("All") }
                                )
                            }
                            items(categories) { cat ->
                                FilterChip(
                                    selected = selectedCategory == cat,
                                    onClick = { selectedCategory = cat },
                                    label = { Text(cat) }
                                )
                            }
                        }
                        Spacer(Modifier.height(8.dp))
                    }
                }

                val filteredEvents = summary!!.events.filter { selectedCategory == null || it.category == selectedCategory }
                
                items(filteredEvents) { event ->
                    val color = when (event.severity) {
                        "ERROR" -> MaterialTheme.colorScheme.error
                        "WARNING" -> StatusWarning
                        "SUCCESS" -> StatusSuccess
                        else -> BrandPrimary
                    }
                    val time = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date(event.timestamp))
                    
                    Row(Modifier.fillMaxWidth().padding(vertical = 4.dp), verticalAlignment = Alignment.Top) {
                        Box(Modifier.padding(top = 6.dp, end = 12.dp).size(10.dp).background(color, CircleShape))
                        Column {
                            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text(event.description, fontWeight = FontWeight.Medium)
                                Text(time, style = MaterialTheme.typography.bodySmall, color = TextMuted)
                            }
                            event.measurements?.forEach { (k, v) ->
                                Text("$k: $v", style = MaterialTheme.typography.bodySmall, color = TextMuted)
                            }
                        }
                    }
                }
                
                item {
                    Spacer(Modifier.height(24.dp))
                    Button(onClick = { }, modifier = Modifier.fillMaxWidth()) {
                        Text("View Full Trajectory")
                    }
                    Spacer(Modifier.height(8.dp))
                    OutlinedButton(onClick = { navController.popBackStack() }, modifier = Modifier.fillMaxWidth()) {
                        Text("Close Summary")
                    }
                }
            }
        }
    }
}

@Composable
fun SummaryRow(label: String, value: String, isStatus: Boolean = false, statusColor: androidx.compose.ui.graphics.Color = BrandPrimary) {
    Row(
        Modifier.fillMaxWidth().padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(label, color = TextMuted)
        if (isStatus) {
            Text(value, color = statusColor, fontWeight = FontWeight.Bold)
        } else {
            Text(value, fontWeight = FontWeight.Bold)
        }
    }
}
