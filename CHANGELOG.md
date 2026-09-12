# Navigators Changelog

## [1.0.0-rc1] - 2026-09-12

This is the first Release Candidate for the Navigators intelligent dead-reckoning platform.

### Added
- **AI Speed Estimation Model**: Edge PyTorch model running locally on Android to estimate speed without GNSS.
- **Offline Map Matching**: Road-network snapping using a localized routing graph to prevent unbounded drift.
- **Error-State Kalman Filter (ESKF)**: Robust GNSS + INS fusion for seamless transitions during GNSS outages.
- **Cloud Telemetry Pipeline**: JWT-authenticated telemetry syncing to a centralized backend via Background Worker.
- **End-to-End Demo Framework**: Showcase scripts (`start_demo.sh` and `run_demo_scenario.py`) for presenting a simulated outage and recovery flow.
- **System Health Diagnostics**: New Web UI for checking all system states (Sensors, AI, Map, IMU, Sync) before field deployment.

### Hardened
- **GNSS Outlier Rejection**: Chi-square measurement gating successfully rejects massive multipath errors.
- **Data Integrity**: SQLite data drops only occur upon `200 OK` validation from the Cloud server.
- **OTA Updates**: Secure PyTorch model distribution with SHA-256 validation.

### Deprecated
- Initial simplistic Dead Reckoning engine (`SimpleDeadReckoning`) is now fully retired in favor of the ESKF.
