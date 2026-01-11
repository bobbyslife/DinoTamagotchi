#!/usr/bin/env python3

import rumps
import subprocess
import time
import threading
from datetime import datetime, timedelta
import json
import os
import random

class NotificationDino(rumps.App):
    def __init__(self):
        super(NotificationDino, self).__init__("🦕", quit_button=None)
        
        # Configure app for better notifications
        rumps.notification.application = "Dino Tamagotchi"
        
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
        self.last_motivational = None
        self.last_hourly_report = None
        
        # Notification settings
        self.notifications_enabled = True
        
        # Load saved data
        self.load_data()
        
        # Create STATIC menu items
        self.create_static_menu()
        
        # Send welcome notification
        self.send_native_notification("🦕 Dino Tamagotchi Started!", 
                                    f"Your dino is ready! Health: {self.health}% | Happiness: {self.happiness}%",
                                    "Click the dino in your menu bar to see all stats!")
        
        # Start monitoring
        self.start_monitoring()
        self.start_health_monitoring()
        self.start_notification_scheduler()
        
        print("🦕 Dino is starting up with enhanced notifications!")
        print("Check your notification center (top right) for dino updates!")
    
    def send_native_notification(self, title, subtitle, message, sound=True):
        """Send a rich native notification that appears in notification center"""
        try:
            if not self.notifications_enabled:
                return
                
            # Use rumps notification but with enhanced content
            rumps.notification(
                title=title,
                subtitle=subtitle, 
                message=message,
                sound=sound
            )
            
            # Also log to console for debugging
            print(f"📱 Notification: {title} - {subtitle} - {message}")
            
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    def create_static_menu(self):
        """Create static menu items"""
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
        
        self.notifications_toggle = rumps.MenuItem("🔔 Notifications: ON", callback=self.toggle_notifications)
        
        # Set the menu
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
            rumps.MenuItem("Send Test Notification 📱", callback=self.test_notification),
            rumps.separator,
            self.notifications_toggle,
            rumps.MenuItem("Reset Day", callback=self.reset),
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]
        
        # Initial update
        self.update_all_menu_items()
    
    @rumps.clicked("Send Test Notification 📱")
    def test_notification(self, sender):
        """Send a test notification to verify native notifications work"""
        self.send_native_notification(
            "🧪 Test Notification",
            f"Your dino says hi! {self.states[self.current_state]}",
            f"Health: {self.health}% | Happiness: {self.happiness}% | Energy: {self.energy}%"
        )
    
    @rumps.clicked("🔔 Notifications: ON")
    def toggle_notifications(self, sender):
        """Toggle notifications on/off"""
        self.notifications_enabled = not self.notifications_enabled
        status = "ON" if self.notifications_enabled else "OFF"
        self.notifications_toggle.title = f"🔔 Notifications: {status}"
        
        if self.notifications_enabled:
            self.send_native_notification("🔔 Notifications Enabled", 
                                        "You'll now receive dino updates!", 
                                        "Your dino will send you health alerts and productivity tips")
        else:
            print("🔕 Notifications disabled")
    
    def start_notification_scheduler(self):
        """Start background scheduler for periodic notifications"""
        def notification_scheduler():
            while True:
                try:
                    now = datetime.now()
                    
                    # Hourly productivity report
                    if (not self.last_hourly_report or 
                        now - self.last_hourly_report > timedelta(hours=1)):
                        self.send_hourly_report()
                        self.last_hourly_report = now
                    
                    # Random motivational messages
                    if (not self.last_motivational or 
                        now - self.last_motivational > timedelta(minutes=30)):
                        if random.random() < 0.3:  # 30% chance every 30 min
                            self.send_motivational_notification()
                        self.last_motivational = now
                        
                except Exception as e:
                    print(f"Notification scheduler error: {e}")
                
                time.sleep(300)  # Check every 5 minutes
        
        threading.Thread(target=notification_scheduler, daemon=True).start()
    
    def send_hourly_report(self):
        """Send hourly productivity report"""
        total_productive = self.time_spent['working'] + self.time_spent['coding'] + self.time_spent['designing']
        total_unproductive = self.time_spent['browsing']
        
        if total_productive > 0 or total_unproductive > 0:
            productive_percent = int((total_productive / (total_productive + total_unproductive)) * 100) if (total_productive + total_unproductive) > 0 else 0
            
            title = "📊 Hourly Dino Report"
            subtitle = f"Productivity: {productive_percent}% | Health: {self.health}%"
            
            if productive_percent >= 70:
                message = f"Great work! Your dino is thriving! {self.states['excited']}"
            elif productive_percent >= 40:
                message = f"Solid progress! Keep it up! {self.states['working']}"
            else:
                message = f"Time to focus? Your dino needs some productivity! {self.states['browsing']}"
            
            self.send_native_notification(title, subtitle, message)
    
    def send_motivational_notification(self):
        """Send random motivational notification"""
        motivational_messages = [
            ("💪 Stay Strong!", "Your dino believes in you!", "Keep pushing forward with your goals!"),
            ("🎯 Focus Time!", f"Current streak: {self.format_time(sum(self.time_spent.values()))}", "You're building great habits!"),
            ("🌟 Awesome Progress!", f"Health: {self.health}% | Happiness: {self.happiness}%", "Your dino is proud of your dedication!"),
            ("🚀 Keep Going!", "Every line of code counts!", "Your dino is cheering you on!"),
            ("💡 Pro Tip!", "Regular breaks boost productivity!", "Don't forget to take care of yourself!"),
            ("🎉 You're Amazing!", f"Session time: {self.format_time((datetime.now() - self.session_start).total_seconds())}", "Your consistency is paying off!")
        ]
        
        title, subtitle, message = random.choice(motivational_messages)
        self.send_native_notification(title, subtitle, message, sound=False)
    
    def update_all_menu_items(self):
        """Update all menu items with current data"""
        try:
            status_text = self.get_current_status()
            self.status_item.title = f"Status: {status_text}"
            
            session_time = self.format_time((datetime.now() - self.session_start).total_seconds())
            
            health_bar = self.create_bar(self.health, "❤️", "💔")
            happiness_bar = self.create_bar(self.happiness, "😊", "😢") 
            energy_bar = self.create_bar(self.energy, "⚡", "😴")
            
            self.health_item.title = f"🦕 Health: {health_bar} {self.health}%"
            self.happiness_item.title = f"😊 Happiness: {happiness_bar} {self.happiness}%"
            self.energy_item.title = f"⚡ Energy: {energy_bar} {self.energy}%"
            
            self.session_item.title = f"⏰ Session: {session_time}"
            
            self.working_item.title = f"  💼 Working: {self.format_time(self.time_spent['working'])}"
            self.coding_item.title = f"  💻 Coding: {self.format_time(self.time_spent['coding'])}"
            self.designing_item.title = f"  🎨 Designing: {self.format_time(self.time_spent['designing'])}"
            self.browsing_item.title = f"  😴 Browsing: {self.format_time(self.time_spent['browsing'])}"
            self.gaming_item.title = f"  🎮 Gaming: {self.format_time(self.time_spent['gaming'])}"
            
            # Update menu bar icon with health indicators
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
        status_map = {
            'idle': "Just chilling",
            'working': "Working hard on Slack!",
            'coding': "Coding like a pro!",
            'designing': "Designing something beautiful!",
            'browsing': "Browsing too long! Health declining..." if self.browsing_streak > 600 else "Browsing the web...",
            'gaming': "Gaming time!",
            'sick': "Dino is very sick! 🤒",
            'dead': "Dino has died! 💀"
        }
        return status_map.get(self.current_state, "Unknown state")
    
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
        """Enhanced health monitoring with rich notifications"""
        def health_monitor():
            while True:
                try:
                    now = datetime.now()
                    
                    # Critical health warnings
                    if self.health < 20 and (not self.last_health_warning or 
                       now - self.last_health_warning > timedelta(minutes=10)):
                        self.send_native_notification(
                            "🚨 CRITICAL: Dino Health Emergency!",
                            f"Health dropped to {self.health}%!",
                            "Your dino is dying from too much browsing! Take a break immediately!"
                        )
                        self.last_health_warning = now
                    
                    # Regular health warnings
                    elif self.health < 50 and (not self.last_health_warning or 
                         now - self.last_health_warning > timedelta(minutes=15)):
                        self.send_native_notification(
                            "⚠️ Dino Health Warning",
                            f"Health at {self.health}% - Take action!",
                            "Consider taking a break from browsing or feed your dino!"
                        )
                        self.last_health_warning = now
                    
                    # Break reminders with rich context
                    productive_time = self.time_spent['working'] + self.time_spent['coding'] + self.time_spent['designing']
                    if (productive_time > 0 and productive_time % (45 * 60) < 30 and
                       (not self.last_break_reminder or 
                        now - self.last_break_reminder > timedelta(minutes=45))):
                        self.send_native_notification(
                            "💡 Smart Break Reminder",
                            f"You've been productive for {self.format_time(productive_time)}!",
                            "Time to stretch, rest your eyes, and recharge! Your dino recommends a 5-10 minute break."
                        )
                        self.last_break_reminder = now
                        
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
        
        # Enhanced state change notifications
        if new_state != old_state and new_state not in ['eating', 'excited']:
            status = self.get_current_status()
            
            # Add context based on the state
            subtitle = f"Health: {self.health}% | Happiness: {self.happiness}%"
            
            if new_state == 'coding':
                subtitle += " | Great for your dino!"
            elif new_state == 'working':
                subtitle += " | Productive time!"
            elif new_state == 'browsing' and self.browsing_streak > 300:
                subtitle += " | ⚠️ Health declining!"
                
            self.send_native_notification(
                f"🦕 Dino State Change: {self.states[new_state]}", 
                subtitle,
                status,
                sound=False
            )
        
        # Save data
        self.save_data()
    
    @rumps.clicked("Feed 🍖")
    def feed(self, sender):
        old_state = self.current_state
        self.current_state = 'eating'
        self.happiness = min(100, self.happiness + 20)
        health_boost = min(100, self.health + 10)
        old_health = self.health
        self.health = health_boost
        
        self.update_all_menu_items()
        
        # Rich feeding notification
        self.send_native_notification(
            "🍖 Dino Fed Successfully!",
            f"Health: {old_health}% → {self.health}% | Happiness: +20",
            "Your dino is much happier and healthier now! Keep taking good care!"
        )
        
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
        
        # Cute petting notification
        self.send_native_notification(
            "✨ Dino Petted with Love!",
            f"Your dino is overjoyed! Happiness: +15",
            "Your dino loves the attention and feels more energized! 🫳✨"
        )
        
        def reset_after_petting():
            time.sleep(2)
            self.current_state = old_state
            self.update_all_menu_items()
        
        threading.Thread(target=reset_after_petting, daemon=True).start()
    
    @rumps.clicked("Take Break 🧘")
    def take_break(self, sender):
        old_health = self.health
        old_energy = self.energy
        
        self.health = min(100, self.health + 15)
        self.energy = min(100, self.energy + 20)
        self.happiness = min(100, self.happiness + 10)
        self.browsing_streak = 0
        self.last_break_reminder = datetime.now()
        
        self.update_all_menu_items()
        
        # Encouraging break notification
        self.send_native_notification(
            "🧘 Refreshing Break Taken!",
            f"Health: +{self.health - old_health} | Energy: +{self.energy - old_energy}",
            "Excellent self-care! Your dino feels completely refreshed and ready to go!"
        )
    
    @rumps.clicked("Reset Day")
    def reset(self, sender):
        self.current_state = 'idle'
        self.happiness = 50
        self.energy = 50
        self.health = 100
        self.browsing_streak = 0
        self.session_start = datetime.now()
        old_time_spent = self.time_spent.copy()
        self.time_spent = {key: 0 for key in self.time_spent}
        
        self.update_all_menu_items()
        
        # Day reset summary
        total_productive = old_time_spent['working'] + old_time_spent['coding'] + old_time_spent['designing']
        self.send_native_notification(
            "🔄 Dino Day Reset Complete!",
            f"Previous session: {self.format_time(total_productive)} productive time",
            "Fresh start! Your dino is back to full health and ready for new adventures!"
        )
    
    def save_data(self):
        """Save dino state to file"""
        try:
            data = {
                'happiness': self.happiness,
                'energy': self.energy, 
                'health': self.health,
                'time_spent': self.time_spent,
                'session_start': self.session_start.isoformat(),
                'browsing_streak': self.browsing_streak,
                'notifications_enabled': self.notifications_enabled
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
                self.notifications_enabled = data.get('notifications_enabled', True)
                
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
    print("🦕 Starting Dino Tamagotchi with Native Notifications...")
    NotificationDino().run()