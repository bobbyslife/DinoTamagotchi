#!/bin/bash

# Create distribution package for Dino Tamagotchi

echo "📦 Creating Dino Tamagotchi distribution package..."

# Create package directory
PACKAGE_DIR="DinoTamagotchi-macOS"
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# Copy necessary files
cp supabase_dino.py "$PACKAGE_DIR/"
cp requirements.txt "$PACKAGE_DIR/"
cp install.sh "$PACKAGE_DIR/"
cp DinoTamagotchi.icns "$PACKAGE_DIR/" 2>/dev/null || echo "No icon file found, skipping..."

# Create a simple README for the package
cat > "$PACKAGE_DIR/README.txt" << 'EOF'
🦕 Dino Tamagotchi for macOS
============================

Thanks for downloading Dino Tamagotchi! This cute productivity app puts a 
virtual dinosaur in your menu bar that reacts to your work habits.

📱 SUPER EASY INSTALLATION:
---------------------------
1. Double-click "install.sh" 
2. Follow the prompts (it will install everything automatically)
3. Your dino will appear in your menu bar!

🎮 HOW IT WORKS:
----------------
- Your dino earns dumplings when you're productive (coding, working, learning)
- Loses dumplings on distracting sites (social media, entertainment)
- Compete with friends in real-time leaderboards!
- Feed and pet your dino to keep it healthy

👥 ADD FRIENDS:
---------------
1. Click your dino in the menu bar
2. Go to "👥 Friends & Multiplayer" 
3. Click "🆔 My Friend Code" to get your code
4. Share with friends so they can add you!

🌐 VISIT OUR COMMUNITY:
-----------------------
See everyone's dinos at: https://dinotamagotchi.com

💝 REQUIREMENTS:
----------------
- macOS 10.15+ (Catalina or later)
- Python 3.7+ (installer will check this)
- Internet connection for multiplayer features

🛠️ MANUAL INSTALLATION (if needed):
------------------------------------
1. Install Python 3: https://www.python.org/downloads/
2. Run: pip3 install rumps supabase
3. Run: python3 supabase_dino.py

🆘 NEED HELP?
-------------
Visit: https://dinotamagotchi.com
Issues: https://github.com/yourusername/DinoTamagotchi/issues

Have fun with your new dino companion! 🦕✨
EOF

# Create enhanced installer that's more user-friendly
cat > "$PACKAGE_DIR/install.sh" << 'EOF'
#!/bin/bash

# Dino Tamagotchi Easy Installer
# Double-click this file to install!

# Make the script work when double-clicked from Finder
cd "$(dirname "$0")"

# Open terminal if run from Finder
if [ "$TERM_PROGRAM" != "Apple_Terminal" ] && [ "$TERM_PROGRAM" != "iTerm.app" ]; then
    osascript -e 'tell application "Terminal" to do script "cd \"'$(pwd)'\" && bash install.sh && echo \"Press any key to close...\" && read -n 1"'
    exit 0
fi

echo "🦕 Welcome to Dino Tamagotchi installer!"
echo "========================================"
echo "This will set up your virtual dinosaur productivity companion."
echo

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This installer is for macOS only."
    echo "Press any key to close..."
    read -n 1
    exit 1
fi

# Check macOS version
macos_version=$(sw_vers -productVersion)
echo "📱 macOS version: $macos_version"

# Check if Python 3 is installed
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1)
    echo "✅ Found: $python_version"
else
    echo "❌ Python 3 is not installed."
    echo ""
    echo "Please install Python 3 first:"
    echo "1. Visit: https://www.python.org/downloads/"
    echo "2. Download Python 3.9 or later"
    echo "3. Install it, then run this installer again"
    echo ""
    echo "Press any key to open Python download page..."
    read -n 1
    open "https://www.python.org/downloads/"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not available."
    echo "Please reinstall Python 3 with pip included."
    echo "Press any key to close..."
    read -n 1
    exit 1
fi

echo "✅ pip3 found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
echo "(This might take a minute...)"
pip3 install --user --quiet rumps supabase urllib3

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    echo "Press any key to close..."
    read -n 1
    exit 1
fi

# Create application directory in user's Applications folder
APP_DIR="$HOME/Applications"
mkdir -p "$APP_DIR"

# Create .app bundle
APP_BUNDLE="$APP_DIR/Dino Tamagotchi.app"
echo "📱 Creating app bundle at: $APP_BUNDLE"

# Remove existing app if present
rm -rf "$APP_BUNDLE"

mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

# Create Info.plist
cat > "$APP_BUNDLE/Contents/Info.plist" << 'PLIST_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>DinoTamagotchi</string>
    <key>CFBundleGetInfoString</key>
    <string>Dino Tamagotchi - Productivity Companion</string>
    <key>CFBundleIconFile</key>
    <string>DinoTamagotchi</string>
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
PLIST_EOF

# Create main executable
cat > "$APP_BUNDLE/Contents/MacOS/DinoTamagotchi" << 'EXEC_EOF'
#!/bin/bash
cd "$(dirname "$0")/../Resources"
export PYTHONPATH="$HOME/.local/lib/python3.10/site-packages:$HOME/.local/lib/python3.9/site-packages:$HOME/.local/lib/python3.8/site-packages:$PYTHONPATH"
python3 supabase_dino.py
EXEC_EOF

chmod +x "$APP_BUNDLE/Contents/MacOS/DinoTamagotchi"

# Copy Python script and icon to Resources
cp supabase_dino.py "$APP_BUNDLE/Contents/Resources/"

# Copy icon if it exists
if [ -f "DinoTamagotchi.icns" ]; then
    cp DinoTamagotchi.icns "$APP_BUNDLE/Contents/Resources/"
fi

echo ""
echo "🎉 Installation Complete!"
echo "========================="
echo ""
echo "Your Dino Tamagotchi has been installed to:"
echo "   📱 ~/Applications/Dino Tamagotchi.app"
echo ""
echo "🚀 TO START YOUR DINO:"
echo "   1. Open Finder"
echo "   2. Go to your Applications folder (in your home directory)"  
echo "   3. Double-click 'Dino Tamagotchi'"
echo "   4. Your dino will appear in the menu bar! 🦕"
echo ""
echo "🌐 VISIT THE COMMUNITY:"
echo "   See everyone's dinos at: https://dinotamagotchi.com"
echo ""
echo "👥 TO ADD FRIENDS:"
echo "   Click your dino → '🆔 My Friend Code' → Share with friends!"
echo ""
echo "Enjoy your productivity companion!"
echo ""
echo "Press any key to finish..."
read -n 1
EOF

chmod +x "$PACKAGE_DIR/install.sh"

# Create ZIP package
echo "🗜️ Creating ZIP package..."
zip -r "DinoTamagotchi-macOS.zip" "$PACKAGE_DIR"

echo ""
echo "✅ Package created: DinoTamagotchi-macOS.zip"
echo "📦 Size: $(du -h DinoTamagotchi-macOS.zip | cut -f1)"
echo ""
echo "Users can now:"
echo "1. Download DinoTamagotchi-macOS.zip"
echo "2. Unzip it"
echo "3. Double-click install.sh"
echo "4. Follow the prompts"
echo "5. Enjoy their dino! 🦕"
EOF