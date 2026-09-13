package com.example.navigators.ui.main

import android.os.Build
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.example.navigators.data.FeedbackDatabase
import com.example.navigators.data.FeedbackEntity
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FeedbackCenterScreen(navController: NavController) {
    Column(Modifier.padding(16.dp).fillMaxSize()) {
        Text("Feedback & Support", style = MaterialTheme.typography.titleLarge)
        Text("Help us improve Navigators.", color = MaterialTheme.colorScheme.onSurfaceVariant)
        
        Spacer(Modifier.height(24.dp))
        
        Card(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp), onClick = { navController.navigate("feedback_form/bug") }) {
            Column(Modifier.padding(16.dp)) {
                Text("Report a Problem", fontWeight = FontWeight.Bold)
                Text("Let us know if something isn't working right.", style = MaterialTheme.typography.bodySmall)
            }
        }
        
        Card(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp), onClick = { navController.navigate("feedback_form/feature") }) {
            Column(Modifier.padding(16.dp)) {
                Text("Suggest an Improvement", fontWeight = FontWeight.Bold)
                Text("Have an idea for a new feature?", style = MaterialTheme.typography.bodySmall)
            }
        }
        
        Card(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp), onClick = { navController.navigate("support_center") }) {
            Column(Modifier.padding(16.dp)) {
                Text("Help & Troubleshooting", fontWeight = FontWeight.Bold)
                Text("Find answers to common questions and issues.", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FeedbackFormScreen(navController: NavController, type: String = "bug") {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    
    var category by remember { mutableStateOf("Navigation") }
    var description by remember { mutableStateOf("") }
    var severity by remember { mutableStateOf("Medium") }
    var attachSession by remember { mutableStateOf(false) }
    var showPrivacyConfirm by remember { mutableStateOf(false) }
    var submitted by remember { mutableStateOf(false) }

    val categories = listOf("Navigation", "GNSS", "Sensors", "AI Speed", "Map", "External IMU", "Synchronization", "Account", "Performance", "UI", "Other")
    var categoryExpanded by remember { mutableStateOf(false) }

    val severities = listOf("Low", "Medium", "High", "Critical")
    var severityExpanded by remember { mutableStateOf(false) }

    if (submitted) {
        Column(Modifier.padding(16.dp).fillMaxSize(), verticalArrangement = Arrangement.Center, horizontalAlignment = androidx.compose.ui.Alignment.CenterHorizontally) {
            Text("Saved locally. It will be submitted when you're online.", style = MaterialTheme.typography.titleMedium)
            Spacer(Modifier.height(16.dp))
            Button(onClick = { navController.popBackStack() }) { Text("Done") }
        }
        return
    }

    if (showPrivacyConfirm) {
        Column(Modifier.padding(16.dp).fillMaxSize()) {
            Text("Privacy Confirmation", style = MaterialTheme.typography.titleLarge)
            Spacer(Modifier.height(16.dp))
            Text("Your report will include:")
            Text("• Technical diagnostics (App version, Android version, Sensor flags)")
            Text("• App/device information")
            if (attachSession) {
                Text("• Recent session IDs and metadata")
            } else {
                Text("• No session data")
            }
            Spacer(Modifier.height(24.dp))
            
            Row(horizontalArrangement = Arrangement.SpaceEvenly, modifier = Modifier.fillMaxWidth()) {
                Button(onClick = { showPrivacyConfirm = false }) { Text("Cancel") }
                Button(onClick = {
                    scope.launch {
                        val techContext = JSONObject().apply {
                            put("app_version", "1.0.0")
                            put("android_version", Build.VERSION.RELEASE)
                            put("device_model", Build.MODEL)
                            put("device_manufacturer", Build.MANUFACTURER)
                        }.toString()
                        
                        val entity = FeedbackEntity(
                            category = category,
                            description = description,
                            severity = severity,
                            sessionId = if (attachSession) "SESSION-LAST" else null,
                            technicalContextJson = techContext,
                            rating = null
                        )
                        withContext(Dispatchers.IO) {
                            FeedbackDatabase.getDatabase(context).feedbackDao().insert(entity)
                        }
                        submitted = true
                    }
                }) { Text("Submit Report") }
            }
        }
        return
    }

    Column(Modifier.padding(16.dp).fillMaxSize().verticalScroll(rememberScrollState())) {
        Text(if (type == "bug") "Report a Problem" else "Suggest an Improvement", style = MaterialTheme.typography.titleLarge)
        Spacer(Modifier.height(16.dp))

        ExposedDropdownMenuBox(
            expanded = categoryExpanded,
            onExpandedChange = { categoryExpanded = !categoryExpanded }
        ) {
            OutlinedTextField(
                value = category,
                onValueChange = {},
                readOnly = true,
                label = { Text("Category") },
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = categoryExpanded) },
                modifier = Modifier.menuAnchor().fillMaxWidth()
            )
            ExposedDropdownMenu(
                expanded = categoryExpanded,
                onDismissRequest = { categoryExpanded = false }
            ) {
                categories.forEach { selectionOption ->
                    DropdownMenuItem(
                        text = { Text(selectionOption) },
                        onClick = {
                            category = selectionOption
                            categoryExpanded = false
                        }
                    )
                }
            }
        }
        
        Spacer(Modifier.height(16.dp))
        OutlinedTextField(
            value = description,
            onValueChange = { description = it },
            label = { Text("Tell us what happened") },
            modifier = Modifier.fillMaxWidth().height(120.dp),
            maxLines = 5
        )

        Spacer(Modifier.height(16.dp))
        ExposedDropdownMenuBox(
            expanded = severityExpanded,
            onExpandedChange = { severityExpanded = !severityExpanded }
        ) {
            OutlinedTextField(
                value = severity,
                onValueChange = {},
                readOnly = true,
                label = { Text("How serious was the problem?") },
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = severityExpanded) },
                modifier = Modifier.menuAnchor().fillMaxWidth()
            )
            ExposedDropdownMenu(
                expanded = severityExpanded,
                onDismissRequest = { severityExpanded = false }
            ) {
                severities.forEach { selectionOption ->
                    DropdownMenuItem(
                        text = { Text(selectionOption) },
                        onClick = {
                            severity = selectionOption
                            severityExpanded = false
                        }
                    )
                }
            }
        }

        Spacer(Modifier.height(16.dp))
        Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
            Column {
                Text("Attach session data", fontWeight = FontWeight.Medium)
                Text("Includes recent session diagnostic info", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            Switch(checked = attachSession, onCheckedChange = { attachSession = it })
        }

        Spacer(Modifier.height(24.dp))
        Button(
            onClick = { showPrivacyConfirm = true }, 
            modifier = Modifier.fillMaxWidth(),
            enabled = description.isNotBlank()
        ) {
            Text("Review & Submit")
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SupportCenterScreen(navController: NavController) {
    val topics = listOf(
        Pair("Getting Started", "Learn the basics of offline navigation."),
        Pair("Sensor Diagnostics", "Troubleshoot gyroscope, accelerometer, and compass issues."),
        Pair("GNSS Problems", "What to do when GPS signal is weak or lost."),
        Pair("Offline Navigation", "Managing local maps and routing without internet.")
    )

    Column(Modifier.padding(16.dp).fillMaxSize()) {
        Text("Help & Troubleshooting", style = MaterialTheme.typography.titleLarge)
        Spacer(Modifier.height(16.dp))

        LazyColumn {
            items(topics) { topic ->
                Card(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                    Column(Modifier.padding(16.dp)) {
                        Text(topic.first, fontWeight = FontWeight.Bold)
                        Text(topic.second, style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
    }
}
