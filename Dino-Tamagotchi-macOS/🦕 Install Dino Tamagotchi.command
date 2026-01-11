#!/bin/bash

# Get script directory
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "🦕 Dino Tamagotchi Installer"
echo "============================"
echo ""

# Check macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This installer is for macOS only."
    echo "Press Enter to close..."
    read
    exit 1
fi

echo "📱 Detected macOS $(sw_vers -productVersion)"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found."
    echo ""
    echo "Please install Python 3 first:"
    echo "1. Visit: https://www.python.org/downloads/"
    echo "2. Download Python 3.9 or later"
    echo "3. Install it, then run this installer again"
    echo ""
    echo "Press Enter to open Python download page..."
    read
    open "https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Found Python: $(python3 --version)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install --user --quiet rumps supabase urllib3

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies."
    echo "Press Enter to close..."
    read
    exit 1
fi

echo "✅ Dependencies installed!"

# Create Applications directory
APP_DIR="$HOME/Applications"
mkdir -p "$APP_DIR"

# Create app bundle
APP_BUNDLE="$APP_DIR/Dino Tamagotchi.app"
echo ""
echo "📱 Creating app at: $APP_BUNDLE"

rm -rf "$APP_BUNDLE"
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

# Create Info.plist
cat > "$APP_BUNDLE/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>DinoTamagotchi</string>
    <key>CFBundleIdentifier</key>
    <string>com.dinotamagotchi.app</string>
    <key>CFBundleName</key>
    <string>Dino Tamagotchi</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>
PLIST

# Create executable
cat > "$APP_BUNDLE/Contents/MacOS/DinoTamagotchi" << 'EXEC'
#!/bin/bash
cd "$(dirname "$0")/../Resources"
export PYTHONPATH="$HOME/.local/lib/python3.10/site-packages:$HOME/.local/lib/python3.9/site-packages:$HOME/.local/lib/python3.8/site-packages:$PYTHONPATH"
python3 supabase_dino.py
EXEC

chmod +x "$APP_BUNDLE/Contents/MacOS/DinoTamagotchi"

# Copy resources
cp supabase_dino.py "$APP_BUNDLE/Contents/Resources/"
if [ -f "DinoTamagotchi.icns" ]; then
    cp DinoTamagotchi.icns "$APP_BUNDLE/Contents/Resources/"
fi

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "🚀 TO START YOUR DINO:"
echo "   1. Open Finder"
echo "   2. Go to Applications in your home folder"
echo "   3. Double-click 'Dino Tamagotchi'"
echo "   4. Your dino will appear in the menu bar! 🦕"
echo ""
echo "🌐 VISIT THE COMMUNITY:"
echo "   https://dino.rest"
echo ""
echo "Enjoy your productivity companion!"
echo ""
echo "Press Enter to finish..."
read
