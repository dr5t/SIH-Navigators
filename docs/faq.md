# Navigators Frequently Asked Questions (FAQ)

### 1. How does Navigators estimate my speed without GPS?
Navigators utilizes a localized PyTorch deep-learning model (`speed_model.pt`) that runs entirely on your device. It processes high-frequency vibrations and motion patterns from the phone's built-in accelerometer and gyroscope to accurately estimate your forward vehicle velocity, even when deep underground or in a tunnel.

### 2. Do I need an internet connection to navigate?
**No.** The core navigation engine—including the IMU processing, AI speed inference, Error-State Kalman Filter (ESKF), and Offline Map Matching—runs 100% locally on your edge device. Internet is only required for syncing your encrypted session telemetry to the cloud *after* the trip has concluded.

### 3. What is Map Matching?
Map Matching is a constraint algorithm. We bundle a lightweight graph of the road network (derived from OpenStreetMap) locally on your device. During a GPS outage, our system uses a Hidden Markov Model (HMM) to map your "dead reckoned" trajectory to the most probable roads, drastically limiting inertial drift.

### 4. Can I hold the phone in my hand?
**No.** The system relies on the assumption that the phone is rigidly attached to the vehicle. If you hold the phone, the accelerometer will register your hand movements rather than the vehicle's dynamics, causing the AI speed model to fail and the navigation filter to drift. Always use a rigid dashboard or windshield mount.

### 5. Why does the system need to calibrate?
Because phones are mounted at arbitrary angles, the app doesn't immediately know which way is "forward" for the vehicle. Calibration algorithms mathematically rotate the phone's internal sensor axes (X, Y, Z) to align perfectly with the vehicle's physical axes (Forward, Right, Down).

### 6. Will this work on iOS?
Currently, Navigators v1.0 is an Android-exclusive application. The deep coupling with hardware sensors and the PyTorch Mobile edge engine are optimized specifically for the Android ecosystem.

### 7. How much battery does the app consume?
Running high-frequency sensor acquisition (100Hz+) and continuous Neural Network inference requires processing power. While the model is heavily quantized to preserve battery, prolonged navigation sessions will consume more power than standard GPS navigation. We recommend plugging your device into the vehicle's charger during use.
