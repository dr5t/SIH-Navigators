#!/usr/bin/env bash
# Navigators Release Packager
# Compiles Android release APK, builds Web app, and packages everything into a zip.

echo "=================================================="
echo "    NAVIGATORS - RELEASE PACKAGER                 "
echo "=================================================="

VERSION="1.0.0-rc1"
RELEASE_DIR="navigators_release_v$VERSION"

mkdir -p $RELEASE_DIR

echo "[INFO] Packaging Android APK..."
cd android || exit
./gradlew assembleRelease
cp app/build/outputs/apk/release/app-release.apk ../$RELEASE_DIR/navigators-v$VERSION.apk
cd ..

echo "[INFO] Packaging Web/Cloud Backend..."
# Mocking a React build process for this demo since we don't have Vite/Webpack initialized in the web dir.
cp -r web $RELEASE_DIR/web_app
cp -r cloud $RELEASE_DIR/cloud_backend
cp requirements.txt $RELEASE_DIR/

echo "[INFO] Packaging Documentation..."
cp -r docs $RELEASE_DIR/docs
cp CHANGELOG.md $RELEASE_DIR/

echo "[INFO] Creating Final Archive..."
zip -r ${RELEASE_DIR}.zip $RELEASE_DIR
rm -rf $RELEASE_DIR

echo "=================================================="
echo "    RELEASE CREATED: ${RELEASE_DIR}.zip           "
echo "=================================================="
