#!/usr/bin/env python3

import rumps
import subprocess
import time
import threading
from datetime import datetime, timedelta
import json
import os

class WorkingDino(rumps.App):
    def __init__(self):
        super(WorkingDino, self).__init__("🦕", quit_button=None)
        
        # Dino states
        self.states = {
            'idle': '🦕',
            'working': '🦖💼', 
            'coding': '🦕💻',
            'designing': '🦕🎨',
            'browsing': '🦖😴',
            'gaming': '🦕🎮',
            'eating': '🦕🍖',
            'excited': '🦖✨',
            'sick': '🦖🤒',
            'dead': '💀'
        }
        
        # Core stats
        self.current_state = 'idle'
        self.happiness = 50
        self.energy = 50
        self.health = 100
        
        # Time tracking
        self.session_start = datetime.now()
        self.state_start_time = datetime.now()
        self.time_spent = {
            'idle': 0,
            'working': 0,
            'coding': 0,
            'designing': 0,
            'browsing': 0,
            'gaming': 0
        }
        
        # Health tracking
        self.browsing_streak = 0
        self.last_health_warning = None
        self.last_break_reminder = None
        
        # Load saved data
        self.load_data()
        
        # Create STATIC menu items to prevent infinite loops
        self.create_static_menu()
        
        # Start monitoring
        self.start_monitoring()
        self.start_health_monitoring()
        
        print("🦕 Dino is starting up!")
        print("Look for the dino emoji in your menu bar!")
    
    def create_static_menu(self):
        """Create static menu items that we'll update in place"""
        # Create menu items as instance variables so we can update them
        self.status_item = rumps.MenuItem(f"Status: Just chilling")
        self.health_item = rumps.MenuItem(f"🦕 Health: ❤️❤️❤️❤️❤️ {self.health}%")
        self.happiness_item = rumps.MenuItem(f"😊 Happiness: 😊😊😊😊😊 {self.happiness}%")
        self.energy_item = rumps.MenuItem(f"⚡ Energy: ⚡⚡⚡⚡⚡ {self.energy}%")
        
        self.session_item = rumps.MenuItem("⏰ Session: 0m")
        
        self.working_item = rumps.MenuItem("  💼 Working: 0m")
        self.coding_item = rumps.MenuItem("  💻 Coding: 0m")
        self.designing_item = rumps.MenuItem("  🎨 Designing: 0m")
        self.browsing_item = rumps.MenuItem("  😴 Browsing: 0m")
        self.gaming_item = rumps.MenuItem("  🎮 Gaming: 0m")
        
        # Set the menu once and don't recreate it
        self.menu = [
            self.status_item,
            rumps.separator,
            self.health_item,
            self.happiness_item,
            self.energy_item,
            rumps.separator,
            self.session_item,
            rumps.MenuItem("📊 Time Breakdown:"),
            self.working_item,
            self.coding_item,
            self.designing_item,
            self.browsing_item,
            self.gaming_item,
            rumps.separator,
            rumps.MenuItem("Feed 🍖", callback=self.feed),
            rumps.MenuItem("Pet 🫳", callback=self.pet),
            rumps.MenuItem("Take Break 🧘", callback=self.take_break),
            rumps.MenuItem("Reset Day", callback=self.reset),
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]
        
        # Initial update
        self.update_all_menu_items()
    
    def update_all_menu_items(self):
        """Update all menu items with current data"""
        try:
            # Update status
            status_text = self.get_current_status()
            self.status_item.title = f"Status: {status_text}"
            
            # Calculate session time  
            session_time = self.format_time((datetime.now() - self.session_start).total_seconds())
            
            # Create bars
            health_bar = self.create_bar(self.health, "❤️", "💔")
            happiness_bar = self.create_bar(self.happiness, "😊", "😢") 
            energy_bar = self.create_bar(self.energy, "⚡", "😴")
            
            # Update all items
            self.health_item.title = f"🦕 Health: {health_bar} {self.health}%"
            self.happiness_item.title = f"😊 Happiness: {happiness_bar} {self.happiness}%"
            self.energy_item.title = f"⚡ Energy: {energy_bar} {self.energy}%"
            
            self.session_item.title = f"⏰ Session: {session_time}"
            
            self.working_item.title = f"  💼 Working: {self.format_time(self.time_spent['working'])}"
            self.coding_item.title = f"  💻 Coding: {self.format_time(self.time_spent['coding'])}"
            self.designing_item.title = f"  🎨 Designing: {self.format_time(self.time_spent['designing'])}"
            self.browsing_item.title = f"  😴 Browsing: {self.format_time(self.time_spent['browsing'])}"
            self.gaming_item.title = f"  🎮 Gaming: {self.format_time(self.time_spent['gaming'])}"
            
            # Update menu bar icon
            health_indicator = ""
            if self.health < 30:
                health_indicator = "🚨"
            elif self.health < 60:
                health_indicator = "⚠️"
            
            self.title = f"{self.states[self.current_state]}{health_indicator}"
            
        except Exception as e:
            print(f"Error updating menu: {e}")
    
    def get_current_status(self):
        """Get descriptive status text"""
        if self.current_state == 'idle':
            return "Just chilling"
        elif self.current_state == 'working':
            return "Working hard on Slack!"
        elif self.current_state == 'coding':
            return "Coding like a pro!"
        elif self.current_state == 'designing':
            return "Designing something beautiful!"
        elif self.current_state == 'browsing':
            if self.browsing_streak > 600:
                return "Browsing too long! Health declining..."
            return "Browsing the web..."
        elif self.current_state == 'gaming':
            return "Gaming time!"
        elif self.current_state == 'sick':
            return "Dino is very sick! 🤒"
        elif self.current_state == 'dead':
            return "Dino has died! 💀"
        else:
            return "Unknown state"
    
    def create_bar(self, value, full_emoji, empty_emoji):
        """Create a visual bar representation"""
        bars = 5
        filled = int(value / 100 * bars)
        return (full_emoji * filled) + (empty_emoji * (bars - filled))
    
    def format_time(self, seconds):
        """Format seconds into readable time"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds/60)}m"
        else:
            hours = int(seconds/3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    def start_monitoring(self):
        def monitor():
            while True:
                try:
                    self.check_active_app()
                except Exception as e:
                    print(f"Monitor error: {e}")
                time.sleep(3)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def start_health_monitoring(self):
        """Monitor health and send reminders"""
        def health_monitor():
            while True:
                try:
                    # Check for health warnings
                    if self.health < 30 and (not self.last_health_warning or 
                       datetime.now() - self.last_health_warning > timedelta(minutes=10)):
                        rumps.notification("🚨 Dino Health Critical!", 
                                         "Your dino is getting sick!", 
                                         "Take a break from browsing!")
                        self.last_health_warning = datetime.now()
                    
                    # Check for break reminders
                    productive_time = self.time_spent['working'] + self.time_spent['coding'] + self.time_spent['designing']
                    if (productive_time > 0 and productive_time % (45 * 60) < 3 and
                       (not self.last_break_reminder or 
                        datetime.now() - self.last_break_reminder > timedelta(minutes=45))):
                        rumps.notification("💡 Break Time!", 
                                         "You've been productive for 45+ minutes", 
                                         "Time to rest your eyes and stretch!")
                        self.last_break_reminder = datetime.now()
                        
                except Exception as e:
                    print(f"Health monitor error: {e}")
                
                time.sleep(30)
        
        threading.Thread(target=health_monitor, daemon=True).start()
    
    def check_active_app(self):
        try:
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
        # Track time in previous state
        if hasattr(self, 'current_state'):
            time_delta = (datetime.now() - self.state_start_time).total_seconds()
            if self.current_state in self.time_spent:
                self.time_spent[self.current_state] += time_delta
        
        self.state_start_time = datetime.now()
        
        old_state = self.current_state
        new_state = 'idle'
        
        if 'slack' in app_name:
            new_state = 'working'
            self.happiness = min(100, self.happiness + 1)
            self.health = min(100, self.health + 0.5)
            self.browsing_streak = 0
            
        elif any(code_app in app_name for code_app in ['code', 'xcode', 'terminal', 'iterm']):
            new_state = 'coding' 
            self.happiness = min(100, self.happiness + 2)
            self.health = min(100, self.health + 1)
            self.browsing_streak = 0
            
        elif 'figma' in app_name:
            new_state = 'designing'
            self.happiness = min(100, self.happiness + 2)
            self.health = min(100, self.health + 0.5)
            self.browsing_streak = 0
            
        elif any(browser in app_name for browser in ['safari', 'chrome', 'firefox']):
            new_state = 'browsing'
            self.happiness = max(0, self.happiness - 1)
            
            self.browsing_streak += 3
            if self.browsing_streak > 300:  # 5 minutes
                health_decline = min(5, self.browsing_streak / 60)
                self.health = max(0, self.health - health_decline)
            
        elif 'game' in app_name:
            new_state = 'gaming'
            self.happiness = min(100, self.happiness + 3)
            self.browsing_streak = 0
        
        else:
            self.browsing_streak = 0
        
        # Check for sick/dead states
        if self.health < 20:
            new_state = 'dead' if self.health == 0 else 'sick'
        
        self.current_state = new_state
        
        # Update menu items
        self.update_all_menu_items()
        
        # Notification for state changes
        if new_state != old_state and new_state not in ['eating', 'excited']:
            status = self.get_current_status()
            rumps.notification("Dino Update", "", status)
        
        # Save data
        self.save_data()
    
    @rumps.clicked("Feed 🍖")
    def feed(self, sender):
        old_state = self.current_state
        self.current_state = 'eating'
        self.happiness = min(100, self.happiness + 20)
        self.health = min(100, self.health + 10)
        self.update_all_menu_items()
        rumps.notification("Dino Fed!", "", "Your dino is happy and healthier! 🍖")
        
        def reset_after_eating():
            time.sleep(3)
            self.current_state = old_state
            self.update_all_menu_items()
        
        threading.Thread(target=reset_after_eating, daemon=True).start()
    
    @rumps.clicked("Pet 🫳") 
    def pet(self, sender):
        old_state = self.current_state
        self.current_state = 'excited'
        self.happiness = min(100, self.happiness + 15)
        self.health = min(100, self.health + 5)
        self.update_all_menu_items()
        rumps.notification("Dino Petted!", "", "Your dino loves you! ✨")
        
        def reset_after_petting():
            time.sleep(2)
            self.current_state = old_state
            self.update_all_menu_items()
        
        threading.Thread(target=reset_after_petting, daemon=True).start()
    
    @rumps.clicked("Take Break 🧘")
    def take_break(self, sender):
        self.health = min(100, self.health + 15)
        self.energy = min(100, self.energy + 20)
        self.happiness = min(100, self.happiness + 10)
        self.browsing_streak = 0
        self.last_break_reminder = datetime.now()
        
        rumps.notification("Break Taken! 🧘", "", "Your dino feels refreshed!")
        self.update_all_menu_items()
    
    @rumps.clicked("Reset Day")
    def reset(self, sender):
        self.current_state = 'idle'
        self.happiness = 50
        self.energy = 50
        self.health = 100
        self.browsing_streak = 0
        self.session_start = datetime.now()
        self.time_spent = {key: 0 for key in self.time_spent}
        
        self.update_all_menu_items()
        rumps.notification("Day Reset!", "", "Your dino is back to normal")
    
    def save_data(self):
        """Save dino state to file"""
        try:
            data = {
                'happiness': self.happiness,
                'energy': self.energy, 
                'health': self.health,
                'time_spent': self.time_spent,
                'session_start': self.session_start.isoformat(),
                'browsing_streak': self.browsing_streak
            }
            
            save_dir = os.path.expanduser("~/.dino_tamagotchi")
            os.makedirs(save_dir, exist_ok=True)
            
            with open(os.path.join(save_dir, "dino_data.json"), "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        """Load dino state from file"""
        try:
            save_dir = os.path.expanduser("~/.dino_tamagotchi")
            data_file = os.path.join(save_dir, "dino_data.json")
            
            if os.path.exists(data_file):
                with open(data_file, "r") as f:
                    data = json.load(f)
                
                self.happiness = data.get('happiness', 50)
                self.energy = data.get('energy', 50)
                self.health = data.get('health', 100)
                self.time_spent = data.get('time_spent', self.time_spent)
                self.browsing_streak = data.get('browsing_streak', 0)
                
                try:
                    saved_start = datetime.fromisoformat(data.get('session_start', datetime.now().isoformat()))
                    if (datetime.now() - saved_start).days > 0:
                        self.time_spent = {key: 0 for key in self.time_spent}
                        self.session_start = datetime.now()
                    else:
                        self.session_start = saved_start
                except:
                    self.session_start = datetime.now()
                    
        except Exception as e:
            print(f"Error loading data: {e}")

if __name__ == "__main__":
    print("🦕 Starting Dino Tamagotchi...")
    WorkingDino().run()