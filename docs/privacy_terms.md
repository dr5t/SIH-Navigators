# Privacy Policy & Terms of Service

**Last Updated:** September 13, 2026

## Privacy Policy

Navigators is built with a privacy-first, offline-first architecture. We believe that your movement data is highly sensitive and should be treated with the utmost security.

### Data We Collect
- **Sensor Telemetry:** High-frequency IMU (Accelerometer, Gyroscope, Magnetometer) data is processed locally to calculate your trajectory.
- **Location Data:** GPS/GNSS data is collected to fuse with our inertial sensors and establish ground truth.
- **Application Diagnostics:** System health, model inference latency, and crash reports.

### How We Use Your Data
- **Offline First:** All navigation processing (AI inference, filtering, map matching) occurs entirely on your device. Your live location is **never** streamed to our servers during active navigation.
- **Session Syncing:** When a session concludes, the anonymous telemetry package is placed in a secure local queue. Once an internet connection is established, it syncs to the Navigators Cloud. This data is exclusively used to retrain our AI models and improve the system's accuracy for future updates.
- **Anonymization:** All sessions are decoupled from personal identifying information (PII) before transmission. Your data is tagged only with an anonymous session ID and an anonymous device hardware ID.

### Third-Party Sharing
We **do not** sell, trade, or otherwise transfer your location data, sensor data, or telemetry to outside parties. 

## Terms of Service

### Assumption of Risk
Navigators is an experimental navigation technology designed to operate in challenging environments (e.g., tunnels, urban canyons). While our models strive for high accuracy, Dead Reckoning systems are subject to physics-based drift.
- **No Guarantee:** You acknowledge that Navigators may occasionally provide inaccurate routing, speed, or location estimations.
- **Safe Operation:** You agree to operate your vehicle safely, obey all local traffic laws, and never rely solely on Navigators in life-or-death situations. Do not interact with the application while driving.

### Intellectual Property
The Navigators software, including the PyTorch models, Android application, Cloud API, and Web Dashboard, are proprietary. You may not decompile, reverse engineer, or redistribute the software without explicit authorization.
