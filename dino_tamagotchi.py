#!/usr/bin/env python3

import rumps
import subprocess
import time
import threading

class DinoTamagotchi(rumps.App):
    def __init__(self):
        super(DinoTamagotchi, self).__init__("🦕", quit_button=None)
        
        # Dino states
        self.states = {
            'idle': '🦕',
            'working': '🦖💼', 
            'coding': '🦕💻',
            'browsing': '🦖😴',
            'gaming': '🦕🎮',
            'eating': '🦕🍖',
            'excited': '🦖✨'
        }
        
        self.current_state = 'idle'
        self.happiness = 50
        self.energy = 50
        
        # Menu items
        self.menu = [
            rumps.MenuItem("Status: Just chilling", callback=None),
            rumps.separator,
            rumps.MenuItem("Feed 🍖", callback=self.feed),
            rumps.MenuItem("Pet 🫳", callback=self.pet), 
            rumps.MenuItem("Reset", callback=self.reset),
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        def monitor():
            while True:
                self.check_active_app()
                time.sleep(3)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def check_active_app(self):
        try:
            # Get frontmost application
            script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
                return frontApp
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                app_name = result.stdout.strip().lower()
                self.update_state_from_app(app_name)
                
        except Exception as e:
            print(f"Error checking app: {e}")
    
    def update_state_from_app(self, app_name):
        new_state = 'idle'
        status = "Just chilling"
        
        if 'slack' in app_name:
            new_state = 'working'
            status = "Working hard on Slack!"
            self.happiness = min(100, self.happiness + 1)
            
        elif any(code_app in app_name for code_app in ['code', 'xcode', 'terminal', 'iterm']):
            new_state = 'coding' 
            status = "Coding like a pro!"
            self.happiness = min(100, self.happiness + 2)
            
        elif any(browser in app_name for browser in ['safari', 'chrome', 'firefox']):
            new_state = 'browsing'
            status = "Browsing the web..."
            self.happiness = max(0, self.happiness - 1)
            
        elif 'game' in app_name:
            new_state = 'gaming'
            status = "Gaming time!"
            self.happiness = min(100, self.happiness + 3)
        
        if new_state != self.current_state:
            self.current_state = new_state
            rumps.notification("Dino Update", "", f"Your dino is now {status}")
        
        # Update menu bar
        self.title = self.states[self.current_state]
        
        # Update status in menu
        if hasattr(self, 'menu') and len(self.menu) > 0:
            self.menu[0].title = f"Status: {status}"
    
    @rumps.clicked("Feed 🍖")
    def feed(self, sender):
        self.title = self.states['eating']
        self.happiness = min(100, self.happiness + 20)
        rumps.notification("Dino Fed!", "", "Your dino is happy! 🍖")
        
        # Return to normal after 3 seconds
        def reset_after_eating():
            time.sleep(3)
            self.title = self.states[self.current_state]
        
        threading.Thread(target=reset_after_eating, daemon=True).start()
    
    @rumps.clicked("Pet 🫳") 
    def pet(self, sender):
        self.title = self.states['excited']
        self.happiness = min(100, self.happiness + 15)
        rumps.notification("Dino Petted!", "", "Your dino loves you! ✨")
        
        # Return to normal after 2 seconds
        def reset_after_petting():
            time.sleep(2)
            self.title = self.states[self.current_state]
        
        threading.Thread(target=reset_after_petting, daemon=True).start()
    
    @rumps.clicked("Reset")
    def reset(self, sender):
        self.current_state = 'idle'
        self.happiness = 50
        self.energy = 50
        self.title = self.states['idle']
        rumps.notification("Dino Reset!", "", "Your dino is back to normal")

if __name__ == "__main__":
    DinoTamagotchi().run()