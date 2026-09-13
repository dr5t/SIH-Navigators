package com.example.navigators.data

import kotlin.math.*

data class TripSummary(
    val durationSec: Long,
    val totalDistanceMeters: Double,
    val gnssTimeSec: Long,
    val drTimeSec: Long,
    val outages: Int,
    val drDistanceMeters: Double,
    val avgSpeedMps: Double,
    val maxSpeedMps: Double,
    val maxUncertaintyMeters: Double,
    val avgUncertaintyMeters: Double,
    val quality: TripQuality,
    val events: List<TripEvent>
)

data class TripQuality(
    val unavailable: Boolean,
    val overallScore: Int,
    val gnssScore: Int,
    val drScore: Int,
    val interruptionsScore: Int,
    val completenessScore: Int,
    val explanation: List<String>
)

data class TripEvent(
    val type: String,
    val category: String,
    val timestamp: Long,
    val severity: String,
    val description: String,
    val measurements: Map<String, String>? = null
)

object SummaryGenerator {

    private fun haversine(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
        val r = 6371000.0 // radius in meters
        val p1 = Math.toRadians(lat1)
        val p2 = Math.toRadians(lat2)
        val dp = Math.toRadians(lat2 - lat1)
        val dl = Math.toRadians(lon2 - lon1)
        val a = sin(dp / 2) * sin(dp / 2) + cos(p1) * cos(p2) * sin(dl / 2) * sin(dl / 2)
        return 2 * r * atan2(sqrt(a), sqrt(1 - a))
    }

    fun generateSummary(points: List<TelemetryEntity>): TripSummary {
        if (points.isEmpty()) {
            return TripSummary(0, 0.0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, emptyList())
        }

        var totalDistance = 0.0
        var drDistance = 0.0
        var maxSpeed = 0.0
        var sumSpeed = 0.0
        var gnssTime = 0L
        var drTime = 0L
        var outages = 0
        var maxUncertainty = 0.0
        var sumUncertainty = 0.0
        
        var gnssPointsCount = 0
        var sumGnssUncertainty = 0.0
        var drPointsCount = 0
        var maxDrUncertainty = 0.0
        
        val events = mutableListOf<TripEvent>()

        val startTime = points.first().timestamp
        val endTime = points.last().timestamp
        val duration = max(0L, (endTime - startTime) / 1000)

        events.add(TripEvent("SESSION_STARTED", "System", startTime, "INFO", "Session Started"))

        var prevPoint: TelemetryEntity? = null
        var prevMode: String? = null
        var prevMapMatched = false
        var prevLowConfidence = false

        for (p in points) {
            val mode = p.mode
            val speed = p.speed
            val hAcc = p.hAcc
            val ts = p.timestamp
            val conf = p.mapMatchConfidence ?: 0.0

            maxSpeed = max(maxSpeed, speed)
            sumSpeed += speed
            maxUncertainty = max(maxUncertainty, hAcc)
            sumUncertainty += hAcc

            if (mode.contains("GNSS")) {
                gnssPointsCount++
                sumGnssUncertainty += hAcc
            } else if (mode.contains("DEAD_RECKONING")) {
                drPointsCount++
                maxDrUncertainty = max(maxDrUncertainty, hAcc)
            }

            if (prevMode != mode) {
                if (mode.contains("DEAD_RECKONING") && prevMode?.contains("GNSS") == true) {
                    outages++
                    events.add(TripEvent("GNSS_LOST", "GNSS", ts, "ERROR", "GNSS lost", mapOf("accuracy" to String.format("%.1fm", hAcc))))
                    events.add(TripEvent("DR_STARTED", "DR", ts, "WARNING", "DR started", mapOf("speed" to String.format("%.1fm/s", speed))))
                } else if (mode.contains("GNSS") && prevMode?.contains("DEAD_RECKONING") == true) {
                    events.add(TripEvent("GNSS_RECOVERED", "GNSS", ts, "SUCCESS", "GNSS recovered", mapOf("accuracy" to String.format("%.1fm", hAcc))))
                    events.add(TripEvent("FUSION_COMPLETED", "Fusion", ts + 3000, "SUCCESS", "Fusion completed"))
                } else if (mode.contains("GNSS_DEGRADED") && prevMode?.contains("GNSS_GOOD") == true) {
                    events.add(TripEvent("GNSS_DEGRADED", "GNSS", ts, "WARNING", "GNSS degraded", mapOf("accuracy" to String.format("%.1fm", hAcc))))
                } else if (mode.contains("GNSS_GOOD") && (prevMode == "INITIALIZING" || prevMode == null)) {
                    events.add(TripEvent("GNSS_ACQUIRED", "GNSS", ts, "SUCCESS", "GNSS acquired", mapOf("accuracy" to String.format("%.1fm", hAcc))))
                }
                prevMode = mode
            }

            val isMapMatched = conf > 0.3
            if (isMapMatched && !prevMapMatched) {
                events.add(TripEvent("MAP_MATCHED", "Map", ts, "INFO", "Map matched", mapOf("confidence" to String.format("%.2f", conf))))
            }
            prevMapMatched = isMapMatched

            val isLowConfidence = hAcc > 20.0 || (mode.contains("DEGRADED") && mode.contains("DEAD_RECKONING"))
            if (isLowConfidence && !prevLowConfidence) {
                events.add(TripEvent("LOW_CONFIDENCE", "Errors", ts, "WARNING", "Low confidence", mapOf("accuracy" to String.format("%.1fm", hAcc))))
            }
            prevLowConfidence = isLowConfidence

            if (prevPoint != null) {
                val dt = max(0L, (ts - prevPoint.timestamp) / 1000)
                if (mode.contains("GNSS")) {
                    gnssTime += dt
                } else {
                    drTime += dt
                }

                val dist = haversine(prevPoint.lat, prevPoint.lon, p.lat, p.lon)
                totalDistance += dist
                if (mode.contains("DEAD_RECKONING")) {
                    drDistance += dist
                }
            }

            prevPoint = p
        }

        events.add(TripEvent("SESSION_ENDED", "System", endTime, "INFO", "Session Ended"))

        val n = points.size
        
        var scoreUnavailable = false
        if (duration < 10 || n < 5) {
            scoreUnavailable = true
        }

        var overallScore = 0
        var gnssScore = 0
        var drScore = 0
        var interruptionsScore = 0
        var completenessScore = 0
        val explanation = mutableListOf<String>()

        if (!scoreUnavailable) {
            var weights = 0.0
            var totalScoreVal = 0.0

            if (gnssPointsCount > 0) {
                val avgGnss = sumGnssUncertainty / gnssPointsCount
                gnssScore = max(0.0, min(100.0, 100.0 - (avgGnss - 3.0) * 5.0)).toInt()
                totalScoreVal += gnssScore * 0.35
                weights += 0.35
                if (gnssScore < 60) explanation.add(String.format("Low GNSS Quality (Avg accuracy %.1fm)", avgGnss))
                else if (gnssScore > 90) explanation.add("Excellent GNSS Quality")
            }

            if (drPointsCount > 0) {
                drScore = max(0.0, min(100.0, 100.0 - (maxDrUncertainty - 10.0) * 2.0)).toInt()
                totalScoreVal += drScore * 0.35
                weights += 0.35
                if (drScore < 60) explanation.add(String.format("Poor DR Stability (Max drift %.1fm)", maxDrUncertainty))
                else if (drScore > 90) explanation.add("Excellent DR Stability")
            }

            interruptionsScore = max(0, 100 - (outages * 10))
            totalScoreVal += interruptionsScore * 0.15
            weights += 0.15
            if (outages >= 3) explanation.add("Frequent GNSS Outages ($outages)")

            val expectedPoints = duration.toDouble()
            completenessScore = max(0.0, min(100.0, (n / max(1.0, expectedPoints)) * 100.0)).toInt()
            totalScoreVal += completenessScore * 0.15
            weights += 0.15
            if (completenessScore < 80) explanation.add("Incomplete data collection ($completenessScore%)")

            if (weights > 0) {
                overallScore = Math.round(totalScoreVal / weights).toInt()
            } else {
                scoreUnavailable = true
            }
        }

        val qualityData = TripQuality(
            scoreUnavailable, overallScore, gnssScore, drScore, interruptionsScore, completenessScore, explanation
        )

        return TripSummary(
            durationSec = duration,
            totalDistanceMeters = totalDistance,
            gnssTimeSec = gnssTime,
            drTimeSec = drTime,
            outages = outages,
            drDistanceMeters = drDistance,
            avgSpeedMps = if (n > 0) sumSpeed / n else 0.0,
            maxSpeedMps = maxSpeed,
            maxUncertaintyMeters = maxUncertainty,
            avgUncertaintyMeters = if (n > 0) sumUncertainty / n else 0.0,
            quality = qualityData,
            events = events
        )
    }
}
