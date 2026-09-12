# Navigators Installation Guide

Welcome to Navigators! This guide covers the setup process for the v1.0 Android application and backend deployment.

## Android Application (Client)

### Prerequisites
- An Android device running Android 9.0 (API level 28) or higher.
- A stable mount for the device in your vehicle (e.g., windshield or dashboard mount). The device must not move relative to the vehicle during navigation.

### Installation
1. Download the `app-release.apk` provided by the development team.
2. Transfer the APK to your Android device.
3. Open a file manager on your device, tap the APK, and select **Install**. You may need to grant permission to "Install unknown apps" if prompted.
4. Open the Navigators app.

### Initial Setup & Permissions
Upon first launch, the app will request the following permissions:
- **Location (Fine/Background):** Required for GNSS fusion and ground-truth benchmarking. Background permission is essential for uninterrupted tracking when the screen is off.
- **Sensors/Activity Recognition:** Required to access the IMU at high frequencies and determine vehicle motion states.
- **Storage:** Required to save local offline telemetry data before cloud syncing.

### Sensor Calibration
1. Mount the phone securely in the vehicle.
2. Start the vehicle and ensure you are on a level surface.
3. In the app, navigate to **Diagnostics $\rightarrow$ Calibration**.
4. Press **Calibrate Alignment**. The system will establish the phone-to-vehicle transformation matrix (Roll/Pitch/Yaw) and calculate IMU biases.
5. You are now ready to begin a navigation session!

---

## Production Deployment (Server)

If you are hosting the Navigators Telemetry Cloud and Web Dashboard yourself, follow these steps:

### Prerequisites
- A VPS or server with Docker and Docker-Compose installed.
- Domain name(s) pointing to your server.

### Deployment Steps
1. Clone the Navigators repository to your server.
2. Navigate to the root directory.
3. Copy `.env.production.example` to `.env.production`:
   ```bash
   cp .env.production.example .env.production
   ```
4. Edit `.env.production` to set a secure `JWT_SECRET`, update `CORS_ORIGINS`, and configure your `DATABASE_URL` (SQLite is default, Postgres recommended for scale).
5. Build and launch the containers:
   ```bash
   docker-compose -f docker/docker-compose.prod.yml up -d --build
   ```
6. The Backend API will be available on port `8000`, and the Web Dashboard will be available on port `80`. Configure a reverse proxy (e.g., Nginx, Traefik, or Caddy) to terminate SSL/TLS (HTTPS) for these ports.
