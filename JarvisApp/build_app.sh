#!/usr/bin/env bash

# Build and install Jarvis.app
set -e

echo "🔨 Building Jarvis App..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Build release version
swift build -c release

# Create app bundle structure
APP_NAME="Jarvis"
APP_BUNDLE="/Applications/${APP_NAME}.app"
BUILD_DIR=".build/release"

echo "📦 Creating app bundle..."

# Remove old app if exists
if [ -d "$APP_BUNDLE" ]; then
    echo "🗑️  Removing old app..."
    rm -rf "$APP_BUNDLE"
fi

# Create bundle structure
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

# Copy executable (rename to match CFBundleExecutable in Info.plist)
cp "$BUILD_DIR/JarvisApp" "$APP_BUNDLE/Contents/MacOS/JustJarvis"
chmod +x "$APP_BUNDLE/Contents/MacOS/JustJarvis"

# Copy Info.plist
cp Info.plist "$APP_BUNDLE/Contents/"

# Copy entitlements if needed
if [ -f "JarvisApp.entitlements" ]; then
    cp JarvisApp.entitlements "$APP_BUNDLE/Contents/"
fi

# Copy resources if they exist
if [ -d "Sources/Resources" ]; then
    cp -R Sources/Resources/* "$APP_BUNDLE/Contents/Resources/" 2>/dev/null || true
fi

echo "✅ App bundle created at: $APP_BUNDLE"

# Sign with ad-hoc identity to apply entitlements locally
echo "🔏 Signing app with entitlements..."
codesign --force --deep --sign - --entitlements "JarvisApp.entitlements" "$APP_BUNDLE"

echo "🚀 You can now launch: open $APP_BUNDLE"
