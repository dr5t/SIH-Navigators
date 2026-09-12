package com.example.navigators

import androidx.compose.foundation.layout.padding
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
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = MaterialTheme.colorScheme.surface,
            ) {
                val items = listOf(
                    NavigationItem("Dashboard", Icons.Default.Home, "dashboard"),
                    NavigationItem("Map", Icons.Default.Place, "navigation"),
                    NavigationItem("Health", Icons.Default.Build, "diagnostics"),
                    NavigationItem("Settings", Icons.Default.Settings, "settings")
                )
                items.forEach { item ->
                    NavigationBarItem(
                        icon = { Icon(item.icon, contentDescription = item.title) },
                        label = { Text(item.title) },
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
        NavHost(navController, startDestination = "dashboard", Modifier.padding(innerPadding)) {
            composable("dashboard") { DashboardScreen(navController) }
            composable("summary/{sessionId}") { SummaryScreen(navController) }
            composable("navigation") { NavigationScreen() }
            composable("diagnostics") { DiagnosticsScreen() }
            composable("settings") { SettingsScreen(navController) }
            composable("faq") { FaqScreen() }
            composable("privacy") { LegalScreen("Privacy Policy") }
            composable("terms") { LegalScreen("Terms & Conditions") }
            composable("cookies") { LegalScreen("Cookie Policy") }
        }
    }
}

data class NavigationItem(val title: String, val icon: androidx.compose.ui.graphics.vector.ImageVector, val route: String)
