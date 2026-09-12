# Android Application Setup

This guide explains how to build and install the Navigators Android Application.

## Requirements
- Android Studio Iguana (or newer).
- Android SDK 34+.
- A physical Android device (emulators lack real IMU sensors, which are required for the AI speed model).

## Building the APK
1. Clone the repository and open the `android/` directory in Android Studio.
2. Wait for Gradle sync to complete. Ensure you have the Chaquopy plugin installed if prompted.
3. Build the project:
   - For a debug build, simply click **Run**.
   - For a release build, select **Build > Generate Signed Bundle / APK**. The build is configured to minify and shrink resources via R8 (`isMinifyEnabled = true`).

## Device Setup
1. Transfer the `.apk` to your physical device and install it.
2. On first launch, the app will request **Location** (Fine) and **Activity Recognition** permissions. These are required.
3. Ensure battery optimization is disabled for the Navigators app. The `FieldTestService` runs as a foreground service, but aggressive OEM battery managers may still throttle sensor polling rates.
