#!/usr/bin/env python3

import rumps
import time

class NotificationTest(rumps.App):
    def __init__(self):
        super(NotificationTest, self).__init__("🧪")
        
        self.menu = [
            rumps.MenuItem("Test Basic Notification", callback=self.test_basic),
            rumps.MenuItem("Test Rumps Notification", callback=self.test_rumps),
            rumps.MenuItem("Test osascript Notification", callback=self.test_osascript),
            rumps.MenuItem("Check Notification Settings", callback=self.check_settings),
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]
        
        print("🧪 Notification Test App Started")
        print("Click the test tube icon in your menu bar to test notifications")
    
    @rumps.clicked("Test Basic Notification")
    def test_basic(self, sender):
        print("📱 Sending basic notification...")
        try:
            rumps.notification("Test Title", "Test Subtitle", "Test Message")
            print("✅ Basic notification sent successfully")
        except Exception as e:
            print(f"❌ Basic notification failed: {e}")
    
    @rumps.clicked("Test Rumps Notification") 
    def test_rumps(self, sender):
        print("📱 Sending rumps notification...")
        try:
            rumps.notification(
                title="🦕 Dino Test",
                subtitle="This is a test notification", 
                message="If you see this, notifications are working!",
                sound=True
            )
            print("✅ Rumps notification sent successfully")
        except Exception as e:
            print(f"❌ Rumps notification failed: {e}")
    
    @rumps.clicked("Test osascript Notification")
    def test_osascript(self, sender):
        print("📱 Sending osascript notification...")
        import subprocess
        try:
            script = '''
            display notification "Direct macOS notification test" with title "🧪 Test" subtitle "Via osascript"
            '''
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ osascript notification sent successfully")
            else:
                print(f"❌ osascript notification failed: {result.stderr}")
        except Exception as e:
            print(f"❌ osascript notification failed: {e}")
    
    @rumps.clicked("Check Notification Settings")
    def check_settings(self, sender):
        print("🔍 Checking notification settings...")
        import subprocess
        try:
            # Check if notifications are enabled for Python/Terminal
            result = subprocess.run([
                'sqlite3', 
                os.path.expanduser('~/Library/Application Support/com.apple.notificationcenterui/db2/db'),
                "SELECT app_id, flags FROM app_info WHERE app_id LIKE '%python%' OR app_id LIKE '%terminal%';"
            ], capture_output=True, text=True)
            
            print("🔍 Current notification permissions:")
            print(result.stdout if result.stdout else "No Python/Terminal entries found")
            
        except Exception as e:
            print(f"❌ Could not check settings: {e}")
            
        print("\n💡 Manual steps to check:")
        print("1. Go to System Preferences → Notifications & Focus")
        print("2. Look for Python or Terminal in the app list")
        print("3. Make sure notifications are enabled")
        print("4. Try running: python3 -c \"import rumps; rumps.notification('Test', '', 'Hello')\"")

if __name__ == "__main__":
    import os
    NotificationTest().run()