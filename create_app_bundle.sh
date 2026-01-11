#!/bin/bash

# Create a proper macOS app bundle for Dino Tamagotchi
# This creates a .app that users can just double-click to install

echo "🦕 Creating Dino Tamagotchi.app bundle..."

APP_NAME="Dino Tamagotchi Installer"
APP_BUNDLE="$APP_NAME.app"
CONTENTS_DIR="$APP_BUNDLE/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Clean up any existing bundle
rm -rf "$APP_BUNDLE"

# Create app bundle structure
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>installer</string>
    <key>CFBundleGetInfoString</key>
    <string>Dino Tamagotchi Installer</string>
    <key>CFBundleIconFile</key>
    <string>DinoTamagotchi</string>
    <key>CFBundleIdentifier</key>
    <string>com.dinotamagotchi.installer</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Dino Tamagotchi Installer</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Create the main executable that runs the installer
cat > "$MACOS_DIR/installer" << 'EOF'
#!/bin/bash

# Get the directory where this app bundle is located
BUNDLE_DIR="$(dirname "$(dirname "$(dirname "$0")")")"
cd "$BUNDLE_DIR"

# Show friendly installer dialog
osascript << 'APPLESCRIPT'
display dialog "🦕 Welcome to Dino Tamagotchi!

This will install your virtual dinosaur companion that lives in your menu bar and helps you stay productive.

Ready to install?" buttons {"Cancel", "Install"} default button "Install" with icon note with title "Dino Tamagotchi Installer"

if button returned of result is "Install" then
    display dialog "Installing Dino Tamagotchi...

This may take a minute to download dependencies." buttons {"OK"} default button "OK" with icon note with title "Installing..." giving up after 2
end if
APPLESCRIPT

if [ $? -ne 0 ]; then
    exit 0
fi

# Open terminal to run the installer
osascript -e 'tell application "Terminal" to do script "cd \"'$(pwd)'\" && chmod +x install.sh && ./install.sh"'
EOF

chmod +x "$MACOS_DIR/installer"

# Copy resources
cp DinoTamagotchi.icns "$RESOURCES_DIR/" 2>/dev/null || echo "No icon found"
cp supabase_dino.py "$BUNDLE_DIR/"
cp requirements.txt "$BUNDLE_DIR/"
cp install.sh "$BUNDLE_DIR/"
chmod +x "$BUNDLE_DIR/install.sh"

# Copy README
cp DinoTamagotchi-macOS/README.txt "$BUNDLE_DIR/"

echo "✅ Created: $APP_BUNDLE"
echo "📱 Users can now double-click the .app to install!"

# Create ZIP with the app bundle
zip -r "DinoTamagotchi-Installer.zip" "$APP_BUNDLE" supabase_dino.py requirements.txt install.sh README.txt

echo "📦 Created: DinoTamagotchi-Installer.zip"
echo "📏 Size: $(du -h DinoTamagotchi-Installer.zip | cut -f1)"