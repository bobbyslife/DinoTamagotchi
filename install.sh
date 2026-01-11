#!/bin/bash

# Dino Tamagotchi Auto-Installer for macOS
# This script will automatically install dependencies and set up the app

set -e  # Exit on any error

echo "🦕 Welcome to Dino Tamagotchi installer!"
echo "This will set up your virtual dinosaur productivity companion."
echo

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This installer is for macOS only."
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo "Please install Python 3 from: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not available."
    echo "Please install pip3 or reinstall Python 3."
    exit 1
fi

echo "✅ pip3 found"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install --user rumps supabase urllib3

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create application directory
APP_DIR="$HOME/Applications/DinoTamagotchi"
mkdir -p "$APP_DIR"

# Copy files
echo "📋 Copying application files..."
cp supabase_dino.py "$APP_DIR/"
cp requirements.txt "$APP_DIR/"

# Create launcher script
cat > "$APP_DIR/DinoTamagotchi.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 supabase_dino.py
EOF

chmod +x "$APP_DIR/DinoTamagotchi.command"

# Create .app bundle manually (simpler than py2app)
APP_BUNDLE="$HOME/Applications/Dino Tamagotchi.app"
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

# Create Info.plist
cat > "$APP_BUNDLE/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>DinoTamagotchi</string>
    <key>CFBundleGetInfoString</key>
    <string>Dino Tamagotchi - Productivity Companion</string>
    <key>CFBundleIconFile</key>
    <string>icon</string>
    <key>CFBundleIdentifier</key>
    <string>com.dinotamagotchi.app</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Dino Tamagotchi</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Create main executable
cat > "$APP_BUNDLE/Contents/MacOS/DinoTamagotchi" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/../Resources"
python3 supabase_dino.py
EOF

chmod +x "$APP_BUNDLE/Contents/MacOS/DinoTamagotchi"

# Copy Python script to Resources
cp supabase_dino.py "$APP_BUNDLE/Contents/Resources/"

# Create simple icon (text-based)
echo "🦕" > "$APP_BUNDLE/Contents/Resources/icon.txt"

echo
echo "🎉 Installation Complete!"
echo
echo "Your Dino Tamagotchi has been installed to:"
echo "   📱 $APP_BUNDLE"
echo
echo "To start your dino:"
echo "   1. Open Finder"
echo "   2. Go to Applications folder"  
echo "   3. Double-click 'Dino Tamagotchi'"
echo "   4. Your dino will appear in the menu bar! 🦕"
echo
echo "Enjoy your productivity companion!"
EOF