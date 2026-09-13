package com.example.navigators.ui.main

import android.Manifest
import android.hardware.Sensor
import android.hardware.SensorManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavController
import com.example.navigators.R
import com.example.navigators.theme.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

fun measurement(value: Double, decimals: Int = 1): String = if (value.isFinite()) String.format(Locale.getDefault(), "%.${decimals}f", value) else "—"
fun navigationLabel(state: NavigationUiState): String = when {
    !state.isRunning -> if (state.error != null) "Unavailable" else "Ready to navigate"
    !state.isInitialized -> "Acquiring position"
    state.mode.contains("DEAD_RECKONING") -> "Dead reckoning"
    state.mode == "GNSS_GOOD" -> "GNSS + INS"
    state.mode == "GNSS_DEGRADED" -> "GNSS degraded"
    else -> state.mode.replace('_', ' ')
}
@Composable
fun InstrumentRow(label: String, value: String, color: androidx.compose.ui.graphics.Color = TextPrimary) {
    Row(Modifier.fillMaxWidth().padding(vertical = 13.dp), verticalAlignment = Alignment.CenterVertically) {
        Text(label, color = TextSecondary, modifier = Modifier.weight(1f), style = MaterialTheme.typography.bodyMedium)
        Text(value, color = color, style = MaterialTheme.typography.bodyMedium, fontFamily = FontFamily.Monospace, modifier = Modifier.weight(1f))
    }
    HorizontalDivider(color = BorderLight)
}
@Composable
fun DashboardScreen(navController: NavController, viewModel: NavigationViewModel) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    var denied by remember { mutableStateOf(false) }
    val permission = rememberLauncherForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { result ->
        if (result[Manifest.permission.ACCESS_FINE_LOCATION] == true) { denied = false; viewModel.startNavigation() } else denied = true
    }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Image(painterResource(R.mipmap.ic_launcher), "Navigators mark", Modifier.size(32.dp))
            Text("NAVIGATORS", style = MaterialTheme.typography.labelLarge, letterSpacing = 3.sp)
        }
        Spacer(Modifier.height(28.dp))
        Text("NAVIGATION", style = MaterialTheme.typography.labelSmall, letterSpacing = 2.sp)
        Text(navigationLabel(state), style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Medium, modifier = Modifier.padding(top = 6.dp))
        Text(if (state.isRunning) "${state.gnssStatus} · ${state.confidence} CONFIDENCE" else "Position and instruments become available with a valid fix.", color = if (state.isRunning) BrandPrimary else TextSecondary, style = MaterialTheme.typography.bodySmall)
        Row(Modifier.fillMaxWidth().padding(vertical = 28.dp), verticalAlignment = Alignment.Bottom, horizontalArrangement = Arrangement.SpaceBetween) {
            Column(Modifier.weight(1f)) {
                Text(measurement(state.speed * 3.6, 0), fontSize = 76.sp, lineHeight = 84.sp, fontWeight = FontWeight.Light, fontFamily = FontFamily.Monospace)
                Text("SPEED / km/h", style = MaterialTheme.typography.labelSmall)
            }
            Column(Modifier.weight(1f).padding(bottom = 6.dp), horizontalAlignment = Alignment.End) {
                Text("${measurement(state.course, 0)}°", fontSize = 32.sp, fontFamily = FontFamily.Monospace)
                Text("TRUE COURSE", style = MaterialTheme.typography.labelSmall)
            }
        }
        HorizontalDivider(color = BrandPrimary.copy(alpha = if (state.isRunning) 1f else .3f), thickness = 2.dp)
        InstrumentRow("Latitude", measurement(state.lat, 6))
        InstrumentRow("Longitude", measurement(state.lon, 6))
        InstrumentRow("Position uncertainty", if (state.isInitialized) "±${measurement(state.posUncertainty)} m" else "UNAVAILABLE")
        InstrumentRow("GNSS", state.gnssStatus, if (state.gnssStatus == "FIXED") StatusSuccess else TextSecondary)
        InstrumentRow("Inertial sensors", if (state.isRunning && state.lastSensorMs > 0) "${measurement(state.sensorHz, 0)} Hz" else "IDLE")
        InstrumentRow("AI speed", state.aiStatus)
        state.error?.let { Text(it, color = StatusError, modifier = Modifier.padding(vertical = 12.dp)) }
        if (denied) Text("Precise location permission is required to start GNSS navigation. Maps can still be browsed.", color = StatusWarning, modifier = Modifier.padding(vertical = 12.dp))
        Spacer(Modifier.height(20.dp))
        Button(onClick = {
            if (state.isRunning) viewModel.stopNavigation()
            else if (androidx.core.content.ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) == android.content.pm.PackageManager.PERMISSION_GRANTED) viewModel.startNavigation()
            else permission.launch(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION))
        }, modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp), colors = ButtonDefaults.buttonColors(containerColor = if (state.isRunning) BgSurfaceElevated else BrandPrimary, contentColor = if (state.isRunning) TextPrimary else BgBase)) {
            Text(if (state.isRunning) "Stop navigation" else "Start navigation")
        }
        OutlinedButton(onClick = { navController.navigate("navigation") { launchSingleTop = true } }, modifier = Modifier.fillMaxWidth().padding(top = 8.dp).heightIn(min = 48.dp)) { Text("Open map") }
    }
}
@Composable
fun DiagnosticsScreen(viewModel: NavigationViewModel) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val manager = remember { context.getSystemService(SensorManager::class.java) }
    var now by remember { mutableLongStateOf(android.os.SystemClock.elapsedRealtime()) }
    LaunchedEffect(Unit) { while (true) { now = android.os.SystemClock.elapsedRealtime(); kotlinx.coroutines.delay(1000) } }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp)) {
        Text("Diagnostics", style = MaterialTheme.typography.headlineSmall)
        Text("Sensor and navigation health", color = TextSecondary, modifier = Modifier.padding(top = 4.dp, bottom = 24.dp))
        Text("SENSORS", style = MaterialTheme.typography.labelSmall)
        listOf("Accelerometer" to Sensor.TYPE_ACCELEROMETER, "Gyroscope" to Sensor.TYPE_GYROSCOPE, "Magnetometer" to Sensor.TYPE_MAGNETIC_FIELD).forEach { (label, type) ->
            val sensor = remember(type) { manager.getDefaultSensor(type) }
            InstrumentRow(label, if (sensor == null) "UNAVAILABLE" else if (type != Sensor.TYPE_MAGNETIC_FIELD && state.isRunning && state.lastSensorMs > 0 && now - state.lastSensorMs < 2000) "RECEIVING" else "PRESENT")
        }
        InstrumentRow("Paired IMU rate", if (state.isRunning) "${measurement(state.sensorHz)} Hz" else "—")
        InstrumentRow("Last IMU sample", if (state.lastSensorMs > 0) "${(now - state.lastSensorMs) / 1000}s ago" else "NONE")
        Spacer(Modifier.height(24.dp)); Text("POSITIONING", style = MaterialTheme.typography.labelSmall)
        InstrumentRow("GNSS", state.gnssStatus)
        InstrumentRow("Last fix", if (state.lastFixMs > 0) "${(now - state.lastFixMs) / 1000}s ago" else "NONE")
        InstrumentRow("Navigation", navigationLabel(state))
        InstrumentRow("Confidence", state.confidence)
        InstrumentRow("AI inference", state.aiStatus)
        InstrumentRow("Map matching", "UNAVAILABLE")
        Spacer(Modifier.height(16.dp))
        Text(state.error ?: if (!state.isInitialized) "Start navigation outdoors with location enabled to acquire the initial GNSS fix." else "Uncertainty is the engine's position estimate in metres. Heading is hidden when course is not valid.", color = TextSecondary)
    }
}
@Composable
fun TripsScreen(navController: NavController) {
    val context = LocalContext.current
    var trips by remember { mutableStateOf<List<JSONObject>>(emptyList()) }
    var error by remember { mutableStateOf<String?>(null) }
    LaunchedEffect(Unit) {
        withContext(Dispatchers.IO) {
            runCatching {
                val file = File(context.filesDir, "trips.json")
                if (file.exists()) { val data = JSONArray(file.readText()); trips = (0 until data.length()).map { data.getJSONObject(it) }.reversed() }
            }.onFailure { error = "Unable to read the local trip log." }
        }
    }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp)) {
        Text("Trips", style = MaterialTheme.typography.headlineSmall)
        Text("Your navigation log · stored on this device", color = TextSecondary, modifier = Modifier.padding(top = 4.dp, bottom = 24.dp))
        if (trips.isEmpty()) {
            Text(error ?: "No completed trips", style = MaterialTheme.typography.titleMedium)
            Text("Start and stop navigation to record a trip. Sessions without a position are marked No fix.", color = TextSecondary, modifier = Modifier.padding(vertical = 12.dp))
        }
        trips.forEach { trip ->
            Text(SimpleDateFormat("dd MMM yyyy · HH:mm", Locale.getDefault()).format(Date(trip.getLong("started"))), style = MaterialTheme.typography.titleMedium, modifier = Modifier.padding(top = 16.dp))
            Text("${trip.getLong("duration")} s  ·  ${measurement(trip.getDouble("distance") / 1000, 2)} km", fontFamily = FontFamily.Monospace, modifier = Modifier.padding(vertical = 8.dp))
            Text("GNSS ${trip.getLong("gnss")} s  /  DR ${trip.getLong("dr")} s  ·  ${trip.getString("quality")}", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
            TextButton(onClick = { navController.navigate("summary/${trip.getString("id")}") }) { Text("View session events") }
            HorizontalDivider(color = BorderLight)
        }
        TextButton(onClick = { navController.navigate("summary/latest") }) { Text("View recorded telemetry") }
    }
}
