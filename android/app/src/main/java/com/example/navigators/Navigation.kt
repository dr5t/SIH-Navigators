package com.example.navigators

import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.example.navigators.ui.main.*

@Composable
fun NavigatorsApp() {
    val navController = rememberNavController()
    val navigationViewModel: NavigationViewModel = androidx.lifecycle.viewmodel.compose.viewModel()
    var mapVisited by remember { mutableStateOf(false) }
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    LaunchedEffect(currentRoute) { if (currentRoute == "navigation") mapVisited = true }
    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = MaterialTheme.colorScheme.surface,
            ) {
                val items = listOf(
                    NavigationItem("Navigate", Icons.Outlined.Navigation, "dashboard"),
                    NavigationItem("Map", Icons.Outlined.Map, "navigation"),
                    NavigationItem("Trips", Icons.Outlined.Route, "trips"),
                    NavigationItem("Diagnostics", Icons.Outlined.Tune, "diagnostics"),
                    NavigationItem("Settings", Icons.Outlined.Settings, "settings")
                )
                items.forEach { item ->
                    NavigationBarItem(
                        icon = { Icon(item.icon, contentDescription = item.title) },
                        label = { Text(item.title, maxLines = 1, style = MaterialTheme.typography.labelSmall) },
                        selected = currentRoute == item.route,
                        onClick = {
                            navController.navigate(item.route) {
                                popUpTo(navController.graph.startDestinationId) { saveState = true }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        Box(Modifier.padding(innerPadding).fillMaxSize()) {
        if (mapVisited) NavigationScreen(navigationViewModel, currentRoute == "navigation")
        NavHost(navController, startDestination = "dashboard") {
            composable("dashboard") { DashboardScreen(navController, navigationViewModel) }
            composable("summary/{sessionId}") { SummaryScreen(navController) }
            composable("navigation") {}
            composable("trips") { TripsScreen(navController) }
            composable("diagnostics") { DiagnosticsScreen(navigationViewModel) }
            composable("settings") { SettingsScreen(navController) }
            composable("feedback_center") { FeedbackCenterScreen(navController) }
            composable("feedback_form/{type}") { FeedbackFormScreen(navController, it.arguments?.getString("type") ?: "bug") }
            composable("support_center") { SupportCenterScreen(navController) }
            composable("faq") { FaqScreen() }
            composable("privacy") { LegalScreen("Privacy Policy") }
            composable("terms") { LegalScreen("Terms & Conditions") }
            composable("cookies") { LegalScreen("Cookie Policy") }
        }
        }
    }
}

data class NavigationItem(val title: String, val icon: androidx.compose.ui.graphics.vector.ImageVector, val route: String)
