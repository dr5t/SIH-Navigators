package com.example.navigators.ui.main

import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Path
import android.graphics.ColorFilter
import android.graphics.PixelFormat
import android.graphics.drawable.Drawable
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.view.MotionEvent
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.compose.ui.graphics.toArgb
import com.example.navigators.theme.*
import kotlinx.coroutines.delay
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.CustomZoomButtonsController
import org.osmdroid.views.overlay.Marker
import org.osmdroid.views.overlay.Polyline

/** Retained in the app composition across tabs, released with its Activity. */
@Composable
fun NavigationScreen(viewModel: NavigationViewModel, visible: Boolean) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val lifecycle = LocalLifecycleOwner.current.lifecycle
    var follow by remember { mutableStateOf(true) }
    var online by remember { mutableStateOf(false) }
    var tilesMissing by remember { mutableStateOf(false) }
    val map = remember {
        MapView(context).apply {
            setTileSource(org.osmdroid.tileprovider.tilesource.TileSourceFactory.MAPNIK)
            setMultiTouchControls(true)
            zoomController.setVisibility(CustomZoomButtonsController.Visibility.NEVER)
            controller.setZoom(3.0)
            overlayManager.tilesOverlay.loadingBackgroundColor = BgBase.toArgb()
            overlayManager.tilesOverlay.loadingLineColor = BgSurface.toArgb()
            setOnTouchListener { _, event ->
                if (event.actionMasked == MotionEvent.ACTION_MOVE) follow = false
                false
            }
        }
    }
    val line = remember { Polyline().apply { outlinePaint.color = BrandPrimary.toArgb(); outlinePaint.strokeWidth = 8f; infoWindow = null } }
    val arrow = remember { NavigationMarker(true) }
    val dot = remember { NavigationMarker(false) }
    val marker = remember { Marker(map).apply { setAnchor(0.5f, 0.5f); infoWindow = null; isEnabled = false } }
    var positioned by remember { mutableStateOf(false) }
    var lastPosition by remember { mutableStateOf<Pair<Double, Double>?>(null) }
    var lastCourse by remember { mutableStateOf(Double.NaN) }
    var lastTrajectory by remember { mutableStateOf<List<Pair<Double, Double>>?>(null) }

    DisposableEffect(map) {
        map.overlays.add(line); map.overlays.add(marker)
        onDispose { map.onPause(); map.onDetach() }
    }
    DisposableEffect(lifecycle, map, visible) {
        fun sync() { if (visible && lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED)) map.onResume() else map.onPause() }
        val observer = LifecycleEventObserver { _, _ -> sync() }
        lifecycle.addObserver(observer); sync()
        onDispose { lifecycle.removeObserver(observer); map.onPause() }
    }
    LaunchedEffect(visible, lifecycle) {
        while (visible) {
            val manager = context.getSystemService(ConnectivityManager::class.java)
            online = manager.getNetworkCapabilities(manager.activeNetwork)?.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED) == true
            map.setUseDataConnection(online)
            val tiles = map.overlayManager.tilesOverlay.tileStates
            tilesMissing = tiles.upToDate + tiles.expired + tiles.scaled == 0
            delay(1000)
        }
    }
    LaunchedEffect(state.lat, state.lon, state.course, state.trajectory, follow, visible) {
        if (visible && state.isInitialized) {
            var changed = false
            val position = Pair(state.lat, state.lon)
            if (position != lastPosition || state.course.compareTo(lastCourse) != 0) {
                val point = GeoPoint(state.lat, state.lon)
                marker.position = point
                marker.icon = if (state.course.isFinite()) arrow else dot
                marker.rotation = if (state.course.isFinite()) -state.course.toFloat() else 0f
                marker.isEnabled = true
                if (!positioned) { map.controller.setZoom(17.0); map.controller.setCenter(point); positioned = true }
                else if (follow) map.controller.setCenter(point)
                lastPosition = position; lastCourse = state.course; changed = true
            } else if (follow) map.controller.setCenter(GeoPoint(state.lat, state.lon))
            if (lastTrajectory !== state.trajectory) {
                line.setPoints(state.trajectory.map { GeoPoint(it.first, it.second) })
                lastTrajectory = state.trajectory; changed = true
            }
            if (changed) map.invalidate()
        }
    }
    Box(if (visible) Modifier.fillMaxSize() else Modifier.size(0.dp)) {
        AndroidView(factory = { map }, modifier = Modifier.fillMaxSize())
        if (visible) {
            Surface(Modifier.align(Alignment.TopStart).padding(12.dp), color = BgSurface.copy(alpha = 0.85f), shape = MaterialTheme.shapes.small) {
                Column(Modifier.padding(12.dp)) {
                    Text(if (online) "MAP · ONLINE" else "MAP · OFFLINE", style = MaterialTheme.typography.labelMedium, color = TextSecondary)
                    Text(if (state.isRunning) navigationLabel(state) else "${if (state.isInitialized) "Last position" else "No position yet"} · ${state.gnssStatus}", style = MaterialTheme.typography.titleSmall)
                    Text("${measurement(state.speed * 3.6)} km/h   ·   ${measurement(state.course, 0)}°   ·   ±${measurement(state.posUncertainty)} m", style = MaterialTheme.typography.bodySmall)
                }
            }
            if (!state.isInitialized || tilesMissing) {
                Surface(Modifier.align(Alignment.BottomStart).padding(start = 12.dp, end = 76.dp, bottom = 42.dp), color = BgSurface, shape = MaterialTheme.shapes.small) {
                    Column(Modifier.padding(12.dp)) {
                        Text(if (!state.isInitialized) "Waiting for a position" else "Map tiles unavailable here", style = MaterialTheme.typography.titleSmall)
                        Text(if (!state.isInitialized) "Start navigation to acquire GNSS. The map is available to browse." else if (!online) "Cached coverage is unavailable at this zoom. Your navigation continues." else "Tiles load in the background. Navigation remains available.", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                    }
                }
            }
            Column(Modifier.align(Alignment.BottomEnd).padding(end = 12.dp, bottom = 42.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                MapControl("Zoom in", Icons.Outlined.Add) { map.controller.zoomIn() }
                MapControl("Zoom out", Icons.Outlined.Remove) { map.controller.zoomOut() }
                FilledIconButton(onClick = { follow = true; lastPosition = null }, enabled = state.isInitialized, modifier = Modifier.size(48.dp), shape = MaterialTheme.shapes.small,
                    colors = IconButtonDefaults.filledIconButtonColors(containerColor = if (follow) BrandPrimary else BgSurface)) {
                    Icon(Icons.Outlined.MyLocation, "Follow / re-center")
                }
            }
            Surface(Modifier.align(Alignment.BottomStart), color = BgSurface) {
                Text("© OpenStreetMap contributors", Modifier.padding(horizontal = 8.dp, vertical = 4.dp), style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}
@Composable private fun MapControl(label: String, icon: androidx.compose.ui.graphics.vector.ImageVector, action: () -> Unit) {
    FilledIconButton(onClick = action, modifier = Modifier.size(48.dp), shape = MaterialTheme.shapes.small,
        colors = IconButtonDefaults.filledIconButtonColors(containerColor = BgSurface, contentColor = TextPrimary)) { Icon(icon, label) }
}
private class NavigationMarker(private val heading: Boolean) : Drawable() {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val path = Path()
    override fun getIntrinsicWidth() = 64
    override fun getIntrinsicHeight() = 64
    override fun draw(canvas: Canvas) {
        canvas.save(); canvas.translate(bounds.exactCenterX(), bounds.exactCenterY())
        paint.color = android.graphics.Color.WHITE; paint.style = Paint.Style.FILL
        if (heading) {
            path.reset(); path.moveTo(0f, -27f); path.lineTo(21f, 23f); path.lineTo(0f, 13f); path.lineTo(-21f, 23f); path.close()
            canvas.drawPath(path, paint); canvas.scale(.73f, .73f); paint.color = BrandPrimaryHover.toArgb(); canvas.drawPath(path, paint)
        } else {
            canvas.drawCircle(0f, 0f, 16f, paint); paint.color = BrandPrimaryHover.toArgb(); canvas.drawCircle(0f, 0f, 11f, paint)
        }
        canvas.restore()
    }
    override fun setAlpha(alpha: Int) { paint.alpha = alpha }
    override fun setColorFilter(filter: ColorFilter?) { paint.colorFilter = filter }
    @Deprecated("Deprecated in Java") override fun getOpacity() = PixelFormat.TRANSLUCENT
}
