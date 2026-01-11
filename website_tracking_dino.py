#!/usr/bin/env python3

import rumps
import subprocess
import time
import threading
from datetime import datetime, timedelta
import json
import os
import random
import re
from urllib.parse import urlparse

class WebsiteTrackingDino(rumps.App):
    def __init__(self):
        super(WebsiteTrackingDino, self).__init__("🦕", quit_button=None)
        
        # Dino states
        self.states = {
            'idle': '🦕',
            'working': '🦖💼', 
            'coding': '🦕💻',
            'designing': '🦕🎨',
            'browsing_productive': '🦕📖',
            'browsing_social': '🦖📱',
            'browsing_news': '🦖📰',
            'browsing_entertainment': '🦖🍿',
            'browsing_shopping': '🦖🛒',
            'browsing_distraction': '🦖😴',
            'gaming': '🦕🎮',
            'eating': '🦕🍖',
            'excited': '🦖✨',
            'sick': '🦖🤒',
            'dead': '💀'
        }
        
        # Website categories
        self.website_categories = {
            'productive': {
                'domains': ['github.com', 'stackoverflow.com', 'docs.', 'developer.', 'learn.', 'coursera.com', 'udemy.com', 'codecademy.com', 'freecodecamp.org'],
                'keywords': ['documentation', 'tutorial', 'learn', 'course', 'guide'],
                'emoji': '📖',
                'health_modifier': 1.0,
                'happiness_modifier': 1.5
            },
            'work': {
                'domains': ['gmail.com', 'google.com/drive', 'notion.so', 'trello.com', 'asana.com', 'monday.com'],
                'keywords': ['email', 'calendar', 'meeting', 'project'],
                'emoji': '💼', 
                'health_modifier': 0.5,
                'happiness_modifier': 1.0
            },
            'social': {
                'domains': ['twitter.com', 'x.com', 'facebook.com', 'instagram.com', 'linkedin.com', 'tiktok.com', 'reddit.com'],
                'keywords': ['social', 'post', 'feed', 'comment'],
                'emoji': '📱',
                'health_modifier': -1.0,
                'happiness_modifier': 0.5
            },
            'news': {
                'domains': ['news.', 'cnn.com', 'bbc.com', 'nytimes.com', 'techcrunch.com', 'ycombinator.com'],
                'keywords': ['news', 'article', 'breaking'],
                'emoji': '📰',
                'health_modifier': -0.5,
                'happiness_modifier': 0.0
            },
            'entertainment': {
                'domains': ['youtube.com', 'netflix.com', 'twitch.tv', 'spotify.com'],
                'keywords': ['video', 'music', 'stream', 'watch'],
                'emoji': '🍿',
                'health_modifier': -1.5,
                'happiness_modifier': 2.0
            },
            'shopping': {
                'domains': ['amazon.com', 'ebay.com', 'etsy.com', 'shopify.com'],
                'keywords': ['shop', 'buy', 'cart', 'checkout'],
                'emoji': '🛒',
                'health_modifier': -0.5,
                'happiness_modifier': 1.0
            }
        }
        
        # Core stats
        self.current_state = 'idle'
        self.current_website = None
        self.current_website_category = None
        self.happiness = 50
        self.energy = 50
        self.health = 100
        
        # Enhanced time tracking
        self.session_start = datetime.now()
        self.state_start_time = datetime.now()
        self.website_start_time = datetime.now()
        
        self.time_spent = {
            'idle': 0,
            'working': 0,
            'coding': 0,
            'designing': 0,
            'browsing_productive': 0,
            'browsing_work': 0,
            'browsing_social': 0,
            'browsing_news': 0,
            'browsing_entertainment': 0,
            'browsing_shopping': 0,
            'browsing_other': 0,
            'gaming': 0
        }
        
        # Website-specific tracking
        self.website_time = {}  # domain -> total_seconds
        self.daily_websites = []  # list of {domain, duration, category, timestamp}
        
        # Health tracking
        self.browsing_streak = 0
        self.social_media_streak = 0
        self.last_health_warning = None
        self.last_break_reminder = None
        self.last_website_report = None
        
        # Notification settings
        self.notifications_enabled = True
        
        # Load saved data
        self.load_data()
        
        # Create menu
        self.create_static_menu()
        
        # Send welcome notification
        self.send_native_notification("🦕 Website-Tracking Dino Started!", 
                                    f"Now monitoring your browsing habits!",
                                    "Your dino will track specific websites and react accordingly!")
        
        # Start monitoring
        self.start_monitoring()
        self.start_health_monitoring()
        self.start_notification_scheduler()
        
        print("🦕 Website-Tracking Dino Started!")
        print("Now monitoring Chrome tabs and categorizing websites!")
    
    def get_current_browser_url(self):
        """Get the current URL from Chrome using AppleScript"""
        try:
            # Try Chrome first
            chrome_script = '''
            tell application "Google Chrome"
                if exists window 1 then
                    set currentURL to URL of active tab of window 1
                    set currentTitle to title of active tab of window 1
                    return currentURL & "|" & currentTitle
                else
                    return ""
                end if
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', chrome_script], 
                                  capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0 and result.stdout.strip():
                url_and_title = result.stdout.strip()
                if "|" in url_and_title:
                    url, title = url_and_title.split("|", 1)
                    return url.strip(), title.strip()
                else:
                    return url_and_title.strip(), ""
            
            # Fallback to Safari if Chrome fails
            safari_script = '''
            tell application "Safari"
                if exists window 1 then
                    set currentURL to URL of current tab of window 1
                    set currentTitle to name of current tab of window 1
                    return currentURL & "|" & currentTitle
                else
                    return ""
                end if
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', safari_script], 
                                  capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0 and result.stdout.strip():
                url_and_title = result.stdout.strip()
                if "|" in url_and_title:
                    url, title = url_and_title.split("|", 1)
                    return url.strip(), title.strip()
                else:
                    return url_and_title.strip(), ""
            
            return None, None
            
        except Exception as e:
            print(f"Error getting browser URL: {e}")
            return None, None
    
    def categorize_website(self, url, title=""):
        """Categorize a website based on URL and title"""
        if not url:
            return 'other'
        
        try:
            # Parse the domain
            parsed = urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '')
            path = parsed.path.lower()
            full_url = (url + " " + title).lower()
            
            # Check each category
            for category, config in self.website_categories.items():
                # Check domains
                for domain_pattern in config['domains']:
                    if domain_pattern in domain:
                        return category
                
                # Check keywords in URL/title
                for keyword in config['keywords']:
                    if keyword in full_url:
                        return category
            
            # Special cases
            if any(term in full_url for term in ['login', 'auth', 'signin']):
                return 'work'
            
            if any(term in domain for term in ['gov', 'edu']):
                return 'productive'
                
            return 'other'
            
        except Exception as e:
            print(f"Error categorizing website: {e}")
            return 'other'
    
    def get_website_display_info(self, category):
        """Get display info for a website category"""
        if category in self.website_categories:
            return self.website_categories[category]['emoji'], f"browsing_{category}"
        return '🌐', 'browsing_other'
    
    def send_native_notification(self, title, subtitle, message, sound=True):
        """Send a rich native notification"""
        try:
            if not self.notifications_enabled:
                return
                
            rumps.notification(
                title=title,
                subtitle=subtitle, 
                message=message,
                sound=sound
            )
            
            print(f"📱 Notification: {title} - {subtitle} - {message}")
            
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    def create_static_menu(self):
        """Create static menu items"""
        self.status_item = rumps.MenuItem("Status: Just chilling")
        self.website_item = rumps.MenuItem("🌐 Website: None")
        self.health_item = rumps.MenuItem(f"🦕 Health: ❤️❤️❤️❤️❤️ {self.health}%")
        self.happiness_item = rumps.MenuItem(f"😊 Happiness: 😊😊😊😊😊 {self.happiness}%")
        self.energy_item = rumps.MenuItem(f"⚡ Energy: ⚡⚡⚡⚡⚡ {self.energy}%")
        
        self.session_item = rumps.MenuItem("⏰ Session: 0m")
        
        # Enhanced time tracking
        self.productive_item = rumps.MenuItem("  📖 Productive Sites: 0m")
        self.work_item = rumps.MenuItem("  💼 Work Sites: 0m") 
        self.social_item = rumps.MenuItem("  📱 Social Media: 0m")
        self.news_item = rumps.MenuItem("  📰 News Sites: 0m")
        self.entertainment_item = rumps.MenuItem("  🍿 Entertainment: 0m")
        self.shopping_item = rumps.MenuItem("  🛒 Shopping: 0m")
        self.other_browsing_item = rumps.MenuItem("  🌐 Other Browsing: 0m")
        
        self.coding_item = rumps.MenuItem("  💻 Coding: 0m")
        self.designing_item = rumps.MenuItem("  🎨 Designing: 0m")
        
        self.notifications_toggle = rumps.MenuItem("🔔 Notifications: ON", callback=self.toggle_notifications)
        
        # Set the menu
        self.menu = [
            self.status_item,
            self.website_item,
            rumps.separator,
            self.health_item,
            self.happiness_item,
            self.energy_item,
            rumps.separator,
            self.session_item,
            rumps.MenuItem("📊 Time Breakdown:"),
            self.productive_item,
            self.work_item,
            self.social_item,
            self.news_item,
            self.entertainment_item,
            self.shopping_item,
            self.other_browsing_item,
            self.coding_item,
            self.designing_item,
            rumps.separator,
            rumps.MenuItem("Feed 🍖", callback=self.feed),
            rumps.MenuItem("Pet 🫳", callback=self.pet),
            rumps.MenuItem("Take Break 🧘", callback=self.take_break),
            rumps.MenuItem("Website Report 📊", callback=self.show_website_report),
            rumps.separator,
            self.notifications_toggle,
            rumps.MenuItem("Reset Day", callback=self.reset),
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]
        
        # Initial update
        self.update_all_menu_items()
    
    @rumps.clicked("Website Report 📊")
    def show_website_report(self, sender):
        """Show detailed website usage report"""
        top_sites = sorted(self.website_time.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if top_sites:
            report_lines = []
            for domain, seconds in top_sites:
                report_lines.append(f"• {domain}: {self.format_time(seconds)}")
            
            report = "\\n".join(report_lines)
            
            self.send_native_notification(
                "📊 Your Top Websites Today",
                f"Total sites visited: {len(self.website_time)}",
                report
            )
        else:
            self.send_native_notification(
                "📊 Website Report",
                "No website data yet",
                "Start browsing to see your website usage statistics!"
            )
    
    @rumps.clicked("🔔 Notifications: ON")
    def toggle_notifications(self, sender):
        """Toggle notifications on/off"""
        self.notifications_enabled = not self.notifications_enabled
        status = "ON" if self.notifications_enabled else "OFF"
        self.notifications_toggle.title = f"🔔 Notifications: {status}"
        
        if self.notifications_enabled:
            self.send_native_notification("🔔 Notifications Enabled", 
                                        "Website tracking active!", 
                                        "Your dino will now send detailed browsing insights")
    
    def start_notification_scheduler(self):
        """Enhanced notification scheduler with website insights"""
        def notification_scheduler():
            while True:
                try:
                    now = datetime.now()
                    
                    # Website usage report every hour
                    if (not self.last_website_report or 
                        now - self.last_website_report > timedelta(hours=1)):
                        self.send_website_usage_report()
                        self.last_website_report = now
                        
                except Exception as e:
                    print(f"Notification scheduler error: {e}")
                
                time.sleep(600)  # Check every 10 minutes
        
        threading.Thread(target=notification_scheduler, daemon=True).start()
    
    def send_website_usage_report(self):
        """Send hourly website usage report"""
        if not self.daily_websites:
            return
        
        # Calculate category totals
        category_totals = {}
        for entry in self.daily_websites:
            if 'category' in entry:
                cat = entry['category']
                category_totals[cat] = category_totals.get(cat, 0) + entry.get('duration', 0)
        
        if category_totals:
            top_category = max(category_totals.items(), key=lambda x: x[1])
            category_name, total_time = top_category
            
            emoji = self.website_categories.get(category_name, {}).get('emoji', '🌐')
            
            self.send_native_notification(
                "📊 Hourly Website Report",
                f"Top category: {emoji} {category_name.title()} ({self.format_time(total_time)})",
                f"Health impact: {self.health}% | Keep monitoring your digital wellness!"
            )
    
    def update_all_menu_items(self):
        """Update all menu items with current data"""
        try:
            status_text = self.get_current_status()
            self.status_item.title = f"Status: {status_text}"
            
            # Website info
            if self.current_website:
                try:
                    domain = urlparse(self.current_website).netloc.replace('www.', '')
                    category_emoji = self.website_categories.get(self.current_website_category, {}).get('emoji', '🌐')
                    self.website_item.title = f"{category_emoji} Website: {domain}"
                except:
                    self.website_item.title = "🌐 Website: Unknown"
            else:
                self.website_item.title = "🌐 Website: None"
            
            session_time = self.format_time((datetime.now() - self.session_start).total_seconds())
            
            health_bar = self.create_bar(self.health, "❤️", "💔")
            happiness_bar = self.create_bar(self.happiness, "😊", "😢") 
            energy_bar = self.create_bar(self.energy, "⚡", "😴")
            
            self.health_item.title = f"🦕 Health: {health_bar} {self.health}%"
            self.happiness_item.title = f"😊 Happiness: {happiness_bar} {self.happiness}%"
            self.energy_item.title = f"⚡ Energy: {energy_bar} {self.energy}%"
            
            self.session_item.title = f"⏰ Session: {session_time}"
            
            # Enhanced time breakdown
            self.productive_item.title = f"  📖 Productive Sites: {self.format_time(self.time_spent['browsing_productive'])}"
            self.work_item.title = f"  💼 Work Sites: {self.format_time(self.time_spent['browsing_work'])}"
            self.social_item.title = f"  📱 Social Media: {self.format_time(self.time_spent['browsing_social'])}"
            self.news_item.title = f"  📰 News Sites: {self.format_time(self.time_spent['browsing_news'])}"
            self.entertainment_item.title = f"  🍿 Entertainment: {self.format_time(self.time_spent['browsing_entertainment'])}"
            self.shopping_item.title = f"  🛒 Shopping: {self.format_time(self.time_spent['browsing_shopping'])}"
            self.other_browsing_item.title = f"  🌐 Other Browsing: {self.format_time(self.time_spent['browsing_other'])}"
            
            self.coding_item.title = f"  💻 Coding: {self.format_time(self.time_spent['coding'])}"
            self.designing_item.title = f"  🎨 Designing: {self.format_time(self.time_spent['designing'])}"
            
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
        """Get descriptive status text with website info"""
        base_status = {
            'idle': "Just chilling",
            'working': "Working hard on Slack!",
            'coding': "Coding like a pro!",
            'designing': "Designing something beautiful!",
            'browsing_productive': "Learning something new!",
            'browsing_work': "Handling work tasks",
            'browsing_social': "Checking social media",
            'browsing_news': "Reading the news",
            'browsing_entertainment': "Enjoying entertainment",
            'browsing_shopping': "Shopping online",
            'browsing_distraction': "Getting distracted...",
            'gaming': "Gaming time!",
            'sick': "Dino is very sick! 🤒",
            'dead': "Dino has died! 💀"
        }.get(self.current_state, "Unknown state")
        
        # Add website-specific context
        if self.current_website and self.current_state.startswith('browsing_'):
            try:
                domain = urlparse(self.current_website).netloc.replace('www.', '')
                if self.social_media_streak > 300:
                    return f"{base_status} on {domain} (too long!)"
                return f"{base_status} on {domain}"
            except:
                pass
        
        return base_status
    
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
                    self.check_current_activity()
                except Exception as e:
                    print(f"Monitor error: {e}")
                time.sleep(3)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def start_health_monitoring(self):
        """Enhanced health monitoring with website-specific warnings"""
        def health_monitor():
            while True:
                try:
                    now = datetime.now()
                    
                    # Social media addiction warning
                    if self.social_media_streak > 900:  # 15 minutes
                        self.send_native_notification(
                            "📱 Social Media Alert!",
                            f"You've been on social media for {self.format_time(self.social_media_streak)}",
                            "Consider taking a break to protect your mental health!"
                        )
                        self.social_media_streak = 0  # Reset to avoid spam
                    
                    # General health warnings
                    if self.health < 30 and (not self.last_health_warning or 
                       now - self.last_health_warning > timedelta(minutes=10)):
                        self.send_native_notification(
                            "🚨 Health Critical!",
                            f"Health: {self.health}% - Distraction overload!",
                            "Take immediate action: close distracting websites and focus!"
                        )
                        self.last_health_warning = now
                        
                except Exception as e:
                    print(f"Health monitor error: {e}")
                
                time.sleep(30)
        
        threading.Thread(target=health_monitor, daemon=True).start()
    
    def check_current_activity(self):
        """Enhanced activity checking with website monitoring"""
        try:
            # Get current app
            app_script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
                return frontApp
            end tell
            '''
            
            app_result = subprocess.run(['osascript', '-e', app_script], 
                                      capture_output=True, text=True)
            
            if app_result.returncode == 0:
                app_name = app_result.stdout.strip().lower()
                
                # If it's a browser, get the URL
                if any(browser in app_name for browser in ['chrome', 'safari', 'firefox']):
                    url, title = self.get_current_browser_url()
                    self.update_browsing_state(url, title, app_name)
                else:
                    self.update_non_browsing_state(app_name)
                
        except Exception as e:
            print(f"Error checking activity: {e}")
    
    def update_browsing_state(self, url, title, browser):
        """Update state based on current website"""
        # Track time for previous state/website
        self.track_time_spent()
        
        # Update current website
        old_website = self.current_website
        self.current_website = url
        
        if url:
            # Categorize the website
            category = self.categorize_website(url, title)
            self.current_website_category = category
            
            # Update website time tracking
            try:
                domain = urlparse(url).netloc.replace('www.', '')
                if domain not in self.website_time:
                    self.website_time[domain] = 0
                
                # Track daily website entry
                if old_website != url:
                    self.daily_websites.append({
                        'domain': domain,
                        'category': category,
                        'timestamp': datetime.now().isoformat(),
                        'duration': 0
                    })
                    
            except Exception as e:
                print(f"Error tracking website: {e}")
            
            # Determine new state
            emoji, new_state = self.get_website_display_info(category)
            
            # Apply website-specific effects
            self.apply_website_effects(category, url)
            
        else:
            # No URL detected, default browsing
            new_state = 'browsing_other'
            self.current_website_category = 'other'
        
        # Update state
        old_state = self.current_state
        self.current_state = new_state
        
        # Reset website timer
        self.website_start_time = datetime.now()
        
        # Update display
        self.update_all_menu_items()
        
        # Send notification for website changes
        if old_website != url and url:
            try:
                domain = urlparse(url).netloc.replace('www.', '')
                category_emoji = self.website_categories.get(self.current_website_category, {}).get('emoji', '🌐')
                
                if self.current_website_category in ['social', 'entertainment']:
                    subtitle = f"⚠️ Entering distraction zone: {domain}"
                elif self.current_website_category == 'productive':
                    subtitle = f"✅ Great choice: {domain}"
                else:
                    subtitle = f"📍 Now on: {domain}"
                
                self.send_native_notification(
                    f"{category_emoji} Website Change",
                    subtitle,
                    f"Category: {self.current_website_category.title()} | Health: {self.health}%",
                    sound=False
                )
                
            except Exception as e:
                print(f"Error sending website notification: {e}")
        
        self.save_data()
    
    def apply_website_effects(self, category, url):
        """Apply health/happiness effects based on website category"""
        if category in self.website_categories:
            config = self.website_categories[category]
            
            # Apply modifiers
            health_change = config['health_modifier'] * 0.5  # Per check (every 3 seconds)
            happiness_change = config['happiness_modifier'] * 0.3
            
            self.health = max(0, min(100, self.health + health_change))
            self.happiness = max(0, min(100, self.happiness + happiness_change))
            
            # Track social media streak
            if category == 'social':
                self.social_media_streak += 3
            else:
                self.social_media_streak = 0
    
    def update_non_browsing_state(self, app_name):
        """Update state for non-browser applications"""
        # Track time for previous state
        self.track_time_spent()
        
        # Reset website tracking
        self.current_website = None
        self.current_website_category = None
        self.social_media_streak = 0
        
        old_state = self.current_state
        new_state = 'idle'
        
        if 'slack' in app_name:
            new_state = 'working'
            self.happiness = min(100, self.happiness + 1)
            self.health = min(100, self.health + 0.5)
            
        elif any(code_app in app_name for code_app in ['code', 'xcode', 'terminal', 'iterm']):
            new_state = 'coding'
            self.happiness = min(100, self.happiness + 2)
            self.health = min(100, self.health + 1)
            
        elif 'figma' in app_name:
            new_state = 'designing'
            self.happiness = min(100, self.happiness + 2)
            self.health = min(100, self.health + 0.5)
            
        elif 'game' in app_name:
            new_state = 'gaming'
            self.happiness = min(100, self.happiness + 3)
        
        self.current_state = new_state
        
        # Update display
        self.update_all_menu_items()
        
        # Notification for app changes
        if old_state != new_state and new_state != 'idle':
            status = self.get_current_status()
            self.send_native_notification(
                f"🔄 App Change: {self.states[new_state]}",
                f"Health: {self.health}% | Happiness: {self.happiness}%",
                status,
                sound=False
            )
        
        self.save_data()
    
    def track_time_spent(self):
        """Track time spent in current state and website"""
        if hasattr(self, 'state_start_time'):
            time_delta = (datetime.now() - self.state_start_time).total_seconds()
            if self.current_state in self.time_spent:
                self.time_spent[self.current_state] += time_delta
        
        # Track website-specific time
        if hasattr(self, 'website_start_time') and self.current_website:
            try:
                website_delta = (datetime.now() - self.website_start_time).total_seconds()
                domain = urlparse(self.current_website).netloc.replace('www.', '')
                if domain in self.website_time:
                    self.website_time[domain] += website_delta
                
                # Update daily websites duration
                if self.daily_websites:
                    self.daily_websites[-1]['duration'] += website_delta
                    
            except Exception as e:
                print(f"Error tracking website time: {e}")
        
        # Reset timers
        self.state_start_time = datetime.now()
        self.website_start_time = datetime.now()
    
    # ... (keeping all the existing menu callback methods: feed, pet, take_break, reset, etc.)
    
    @rumps.clicked("Feed 🍖")
    def feed(self, sender):
        old_state = self.current_state
        self.current_state = 'eating'
        self.happiness = min(100, self.happiness + 20)
        health_boost = min(100, self.health + 10)
        old_health = self.health
        self.health = health_boost
        
        self.update_all_menu_items()
        
        self.send_native_notification(
            "🍖 Dino Fed Successfully!",
            f"Health: {old_health}% → {self.health}% | Happiness: +20",
            "Your dino is much happier and healthier now!"
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
        
        self.send_native_notification(
            "✨ Dino Petted with Love!",
            f"Your dino is overjoyed! Happiness: +15",
            "Your dino loves the attention and feels more energized!"
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
        self.social_media_streak = 0
        self.last_break_reminder = datetime.now()
        
        self.update_all_menu_items()
        
        self.send_native_notification(
            "🧘 Refreshing Break Taken!",
            f"Health: +{self.health - old_health} | Social media streak reset",
            "Excellent self-care! Your dino feels completely refreshed!"
        )
    
    @rumps.clicked("Reset Day")
    def reset(self, sender):
        self.current_state = 'idle'
        self.current_website = None
        self.current_website_category = None
        self.happiness = 50
        self.energy = 50
        self.health = 100
        self.social_media_streak = 0
        self.session_start = datetime.now()
        
        # Save old data for report
        old_website_time = self.website_time.copy()
        
        # Reset tracking
        self.time_spent = {key: 0 for key in self.time_spent}
        self.website_time = {}
        self.daily_websites = []
        
        self.update_all_menu_items()
        
        # Summary report
        if old_website_time:
            top_site = max(old_website_time.items(), key=lambda x: x[1])
            self.send_native_notification(
                "🔄 Day Reset Complete!",
                f"Most visited: {top_site[0]} ({self.format_time(top_site[1])})",
                "Fresh start with detailed website tracking!"
            )
        else:
            self.send_native_notification(
                "🔄 Day Reset Complete!",
                "Ready for detailed website tracking",
                "Your dino will now monitor and categorize your browsing!"
            )
    
    def save_data(self):
        """Enhanced save with website data"""
        try:
            data = {
                'happiness': self.happiness,
                'energy': self.energy, 
                'health': self.health,
                'time_spent': self.time_spent,
                'website_time': self.website_time,
                'daily_websites': self.daily_websites,
                'session_start': self.session_start.isoformat(),
                'social_media_streak': self.social_media_streak,
                'notifications_enabled': self.notifications_enabled
            }
            
            save_dir = os.path.expanduser("~/.dino_tamagotchi")
            os.makedirs(save_dir, exist_ok=True)
            
            with open(os.path.join(save_dir, "dino_website_data.json"), "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        """Enhanced load with website data"""
        try:
            save_dir = os.path.expanduser("~/.dino_tamagotchi")
            data_file = os.path.join(save_dir, "dino_website_data.json")
            
            if os.path.exists(data_file):
                with open(data_file, "r") as f:
                    data = json.load(f)
                
                self.happiness = data.get('happiness', 50)
                self.energy = data.get('energy', 50)
                self.health = data.get('health', 100)
                self.time_spent = data.get('time_spent', self.time_spent)
                self.website_time = data.get('website_time', {})
                self.daily_websites = data.get('daily_websites', [])
                self.social_media_streak = data.get('social_media_streak', 0)
                self.notifications_enabled = data.get('notifications_enabled', True)
                
                try:
                    saved_start = datetime.fromisoformat(data.get('session_start', datetime.now().isoformat()))
                    if (datetime.now() - saved_start).days > 0:
                        # New day - reset daily data but keep website history
                        self.time_spent = {key: 0 for key in self.time_spent}
                        self.daily_websites = []
                        self.session_start = datetime.now()
                    else:
                        self.session_start = saved_start
                except:
                    self.session_start = datetime.now()
                    
        except Exception as e:
            print(f"Error loading data: {e}")

if __name__ == "__main__":
    print("🦕 Starting Website-Tracking Dino...")
    WebsiteTrackingDino().run()