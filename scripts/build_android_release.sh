#!/usr/bin/env bash

# Build script for Navigators Android Production Release (APK)
echo "========================================================="
echo "   Navigators: Generating Production Android Release     "
echo "========================================================="

cd android

if [ ! -f "local.properties" ]; then
    echo "[ERROR] local.properties not found in android/ directory."
    echo "Please configure your keystore paths in local.properties before building:"
    echo ""
    echo "RELEASE_STORE_FILE=/path/to/your/keystore.jks"
    echo "RELEASE_STORE_PASSWORD=your_keystore_password"
    echo "RELEASE_KEY_ALIAS=your_key_alias"
    echo "RELEASE_KEY_PASSWORD=your_key_password"
    echo ""
    echo "To generate a new keystore:"
    echo "keytool -genkey -v -keystore release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias"
    exit 1
fi

echo "[INFO] Cleaning previous builds..."
./gradlew clean

echo "[INFO] Building Release APK..."
./gradlew assembleRelease

if [ $? -eq 0 ]; then
    echo "========================================================="
    echo "   [SUCCESS] Release APK generated!                      "
    echo "   Location: android/app/build/outputs/apk/release/app-release.apk"
    echo "========================================================="
else
    echo "========================================================="
    echo "   [FAILED] Gradle build encountered an error.           "
    echo "========================================================="
    exit 1
fi
