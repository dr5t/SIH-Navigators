# Navigators User Guide

Welcome to Navigators! This system provides robust vehicle navigation in GNSS-denied environments (e.g., long tunnels, dense urban canyons, or severe multipath areas).

## Overview
Navigators blends:
1. Standard GNSS (GPS, GLONASS, Galileo) when available.
2. AI-driven kinematics (speed estimation from smartphone IMU).
3. Offline Map Matching to constrain lateral drift.
4. An Error-State Kalman Filter (ESKF) for seamless fusion and drift correction.

## Quick Start
1. **Install the Android Application** on a supported device (Android 7.0+).
2. **Mount the Device Firmly** in your vehicle. Do not hold the device in your hand while driving, as the AI speed estimation model assumes a fixed vehicle frame.
3. **Open the App** and grant Location and Sensor permissions.
4. **Start a Field Test Session**. The app will record telemetry and run the navigation engine in the background.
5. **View Live Telemetry** via the Web Dashboard, or sync the session later for detailed analysis.

## Core Features
- **Intelligent Dead Reckoning (DR):** When GNSS is lost, the system automatically transitions to DR using the local AI speed model and gyroscope heading.
- **Auto-Recovery:** When GNSS returns, the ESKF smoothly corrects any accumulated drift and re-calibrates the inertial biases without jarring position jumps.
- **Offline Maps:** Navigation continues smoothly even without an internet connection using local road network graphs.
