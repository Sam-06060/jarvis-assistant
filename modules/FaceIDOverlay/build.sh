#!/bin/bash

# Face ID Overlay - Swift Compilation Script
# This builds the native macOS application

echo "🔨 Building Face ID Overlay..."
echo ""

# Clean previous builds
rm -rf FaceIDOverlay.app
rm -f FaceIDOverlay

# Compile Swift files
echo "📦 Compiling Swift code..."
swiftc -o FaceIDOverlay \
    NotchDetector.swift \
    AnimationEngine.swift \
    FaceIDOverlay.swift \
    -framework Cocoa \
    -framework QuartzCore \
    -framework CoreVideo \
    -framework CoreImage \
    -O

# Check if compilation succeeded
if [ ! -f FaceIDOverlay ]; then
    echo "❌ Compilation failed!"
    exit 1
fi

echo "✅ Compilation successful!"
echo ""

# Create .app bundle structure
echo "📦 Creating application bundle..."
mkdir -p FaceIDOverlay.app/Contents/MacOS
mkdir -p FaceIDOverlay.app/Contents/Resources

# Move binary
mv FaceIDOverlay FaceIDOverlay.app/Contents/MacOS/

# Create Info.plist
cat > FaceIDOverlay.app/Contents/Info.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>FaceIDOverlay</string>
    <key>CFBundleIdentifier</key>
    <string>com.jarvis.faceid</string>
    <key>CFBundleName</key>
    <string>FaceIDOverlay</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

echo "✅ Application bundle created!"
echo ""
echo "✨ Build complete!"
echo ""
echo "📍 Binary location: $(pwd)/FaceIDOverlay.app/Contents/MacOS/FaceIDOverlay"
echo ""
echo "🧪 Test it by running:"
echo "   ./FaceIDOverlay.app/Contents/MacOS/FaceIDOverlay"
echo ""
echo "   Then type 'SUCCESS' or 'FAIL' in the terminal to test animations"
echo ""
