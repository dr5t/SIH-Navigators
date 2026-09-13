package com.example.navigators.ui.main

import android.annotation.SuppressLint
import android.app.Application
import android.content.Context
import android.content.Intent
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Handler
import android.os.HandlerThread
import android.os.SystemClock
import androidx.lifecycle.AndroidViewModel
import com.example.navigators.FieldTestService
import com.example.navigators.PythonBridge
import com.example.navigators.SensorRecorder
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.util.UUID

data class NavigationUiState(
    val isInitialized: Boolean = false, val isRunning: Boolean = false,
    val lat: Double = Double.NaN, val lon: Double = Double.NaN,
    val alt: Double = Double.NaN, val speed: Double = Double.NaN,
    val course: Double = Double.NaN, val mode: String = "IDLE",
    val posUncertainty: Double = Double.NaN, val explanation: String = "",
    val confidence: String = "UNAVAILABLE", val aiStatus: String = "UNAVAILABLE",
    val gnssStatus: String = "NO FIX", val sensorHz: Double = 0.0,
    val lastSensorMs: Long = 0, val lastFixMs: Long = 0,
    val error: String? = null, val trajectory: List<Pair<Double, Double>> = emptyList()
)

/** One activity-scoped engine; map visibility never starts or stops sensors. */
class NavigationViewModel(application: Application) : AndroidViewModel(application), LocationListener {
    private val bridge = PythonBridge(application)
    private val thread = HandlerThread("NavigationEngine").apply { start() }
    private val handler = Handler(thread.looper)
    private val recorder = SensorRecorder(application)
    private val locationManager = application.getSystemService(Context.LOCATION_SERVICE) as LocationManager
    private val _uiState = MutableStateFlow(NavigationUiState())
    val uiState = _uiState.asStateFlow()
    private var lastImuNs = 0L
    private var lastPublishMs = 0L
    private var lastFixMs = 0L
    private var fixAccuracy = Double.NaN
    private var bearingValid = false
    private var sensorCount = 0
    private var rateStart = 0L
    private var sensorHz = 0.0
    private val distanceBuffer = FloatArray(1)
    private var sessionId = ""
    private var startWallMs = 0L
    private var distance = 0.0
    private var gnssMs = 0L
    private var drMs = 0L
    private var lastLogMs = 0L
    private var latest = NavigationUiState()

    init {
        recorder.onImuData = { accel, gyro, time ->
            if (_uiState.value.isRunning) {
                val now = SystemClock.elapsedRealtime()
                sensorCount++
                if (now - rateStart >= 1000) {
                    sensorHz = sensorCount * 1000.0 / (now - rateStart)
                    rateStart = now; sensorCount = 0
                }
                val dt = if (lastImuNs == 0L) 0.0 else (time - lastImuNs) / 1e9
                lastImuNs = time
                try {
                    if (dt > 0 && dt < 0.5) accept(bridge.processImu(accel, gyro, dt, time / 1e9))
                    publish(now)
                } catch (e: Exception) { fail(e) }
            }
        }
    }

    @SuppressLint("MissingPermission")
    fun startNavigation() {
        if (_uiState.value.isRunning) return
        try {
            val app = getApplication<Application>()
            androidx.core.content.ContextCompat.startForegroundService(app, Intent(app, FieldTestService::class.java).setAction(FieldTestService.ACTION_START))
            _uiState.value = NavigationUiState(isRunning = true, mode = "WAITING FOR FIX")
            handler.post {
                bridge.reset(); latest = _uiState.value
                lastImuNs = 0; lastFixMs = 0; lastPublishMs = 0; lastLogMs = 0
                bearingValid = false; sensorCount = 0; sensorHz = 0.0
                rateStart = SystemClock.elapsedRealtime(); startWallMs = System.currentTimeMillis()
                sessionId = UUID.randomUUID().toString(); distance = 0.0; gnssMs = 0; drMs = 0
                try {
                    recorder.start(handler)
                    locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1000L, 0f, this, thread.looper)
                } catch (e: Exception) { fail(e) }
            }
        } catch (e: Exception) { fail(e) }
    }

    fun stopNavigation() {
        if (!_uiState.value.isRunning) return
        _uiState.update { it.copy(isRunning = false, mode = "STOPPED", gnssStatus = "STOPPED") }
        handler.post {
            recorder.stop(); locationManager.removeUpdates(this)
            saveTrip()
            bridge.reset(); lastImuNs = 0
        }
        getApplication<Application>().stopService(Intent(getApplication(), FieldTestService::class.java))
    }

    override fun onLocationChanged(location: Location) {
        if (!_uiState.value.isRunning || !location.hasAccuracy() || location.accuracy <= 0 ||
            !location.latitude.isFinite() || location.latitude !in -90.0..90.0 ||
            !location.longitude.isFinite() || location.longitude !in -180.0..180.0 ||
            SystemClock.elapsedRealtimeNanos() - location.elapsedRealtimeNanos > 10_000_000_000L) return
        try {
            lastFixMs = SystemClock.elapsedRealtime()
            fixAccuracy = location.accuracy.toDouble()
            bearingValid = location.hasBearing() && location.hasSpeed() && location.speed > 0.5f
            accept(bridge.processGnss(location.latitude, location.longitude,
                if (location.hasAltitude()) location.altitude else 0.0,
                if (location.hasSpeed()) location.speed.toDouble() else 0.0,
                if (location.hasBearing()) location.bearing.toDouble() else 0.0,
                fixAccuracy, location.elapsedRealtimeNanos / 1e9))
            publish(lastFixMs, true)
        } catch (e: Exception) { fail(e) }
    }

    private fun accept(state: Map<String, Any>) {
        fun number(key: String) = state[key]?.toString()?.toDoubleOrNull()?.takeIf { it.isFinite() } ?: Double.NaN
        val lat = number("lat"); val lon = number("lon")
        if (lat !in -90.0..90.0 || lon !in -180.0..180.0) return
        latest = latest.copy(isInitialized = true, lat = lat, lon = lon, alt = number("alt"),
            speed = number("speed"), course = if (bearingValid && state["heading_valid"].toString() == "True") (number("course") + 360) % 360 else Double.NaN,
            mode = state["mode"].toString(), posUncertainty = number("pos_uncertainty"),
            confidence = state["confidence"]?.toString() ?: "UNAVAILABLE",
            aiStatus = state["ai_status"]?.toString() ?: "UNAVAILABLE", error = null)
    }

    private fun publish(now: Long, force: Boolean = false) {
        if (!force && now - lastPublishMs < 250) return
        val delta = if (lastPublishMs == 0L) 0L else now - lastPublishMs
        lastPublishMs = now
        val gnss = when {
            lastFixMs == 0L -> "NO FIX"
            now - lastFixMs > 2000 -> "LOST"
            fixAccuracy < 10 -> "FIXED"
            else -> "DEGRADED"
        }
        if (latest.isInitialized) {
            if (gnss == "LOST") drMs += delta else gnssMs += delta
            val last = latest.trajectory.lastOrNull()
            if (last != null) Location.distanceBetween(last.first, last.second, latest.lat, latest.lon, distanceBuffer)
            if (last == null || distanceBuffer[0] >= 5f) {
                if (last != null) distance += distanceBuffer[0]
                latest = latest.copy(trajectory = (latest.trajectory.takeLast(1999) + Pair(latest.lat, latest.lon)))
            }
            if (now - lastLogMs >= 1000) {
                lastLogMs = now
                try {
                    com.example.navigators.data.TelemetryDatabase.getDatabase(getApplication()).telemetryDao().insert(
                        com.example.navigators.data.TelemetryEntity(sessionId = sessionId, timestamp = System.currentTimeMillis(), lat = latest.lat, lon = latest.lon,
                            alt = latest.alt, speed = latest.speed, course = latest.course, hAcc = latest.posUncertainty, vAcc = Double.NaN, mode = latest.mode))
                } catch (e: Exception) { android.util.Log.e("NavigationEngine", "Telemetry write failed", e) }
            }
        }
        latest = latest.copy(isRunning = _uiState.value.isRunning, gnssStatus = gnss, sensorHz = sensorHz,
            lastSensorMs = if (lastImuNs > 0) lastImuNs / 1_000_000 else 0, lastFixMs = lastFixMs)
        if (_uiState.value.isRunning) _uiState.value = latest
    }

    private fun fail(e: Exception) {
        android.util.Log.e("NavigationEngine", "Navigation error", e)
        recorder.stop(); runCatching { locationManager.removeUpdates(this) }
        latest = latest.copy(error = e.message ?: "Navigation unavailable", isRunning = false, mode = "UNAVAILABLE")
        _uiState.value = latest
        getApplication<Application>().stopService(Intent(getApplication(), FieldTestService::class.java))
    }

    private fun saveTrip() {
        if (startWallMs == 0L) return
        runCatching {
            val file = File(getApplication<Application>().filesDir, "trips.json")
            val trips = if (file.exists()) JSONArray(file.readText()) else JSONArray()
            trips.put(JSONObject().put("id", sessionId).put("started", startWallMs)
                .put("duration", (System.currentTimeMillis() - startWallMs) / 1000).put("distance", distance)
                .put("gnss", gnssMs / 1000).put("dr", drMs / 1000).put("points", latest.trajectory.size)
                .put("quality", if (latest.isInitialized) latest.confidence else "NO FIX"))
            val atomic = android.util.AtomicFile(file)
            val stream = atomic.startWrite()
            try { stream.write(trips.toString().toByteArray()); atomic.finishWrite(stream) }
            catch (e: Exception) { atomic.failWrite(stream); throw e }
        }.onFailure { android.util.Log.e("NavigationEngine", "Trip save failed", it) }
        startWallMs = 0
    }
    override fun onProviderDisabled(provider: String) { lastFixMs = 0; latest = latest.copy(gnssStatus = "OFF") }
    override fun onProviderEnabled(provider: String) {}
    override fun onCleared() { stopNavigation(); handler.post { thread.quitSafely() } }
}
