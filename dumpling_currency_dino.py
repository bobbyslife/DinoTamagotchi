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

class DumplingDino(rumps.App):
    def __init__(self):
        super(DumplingDino, self).__init__("🦕", quit_button=None)
        
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
                'happiness_modifier': 1.5,
                'dumpling_rate': 1.0  # dumplings per minute
            },
            'work': {
                'domains': ['gmail.com', 'google.com/drive', 'notion.so', 'trello.com', 'asana.com', 'monday.com'],
                'keywords': ['email', 'calendar', 'meeting', 'project'],
                'emoji': '💼', 
                'health_modifier': 0.5,
                'happiness_modifier': 1.0,
                'dumpling_rate': 0.8
            },
            'social': {
                'domains': ['twitter.com', 'x.com', 'facebook.com', 'instagram.com', 'linkedin.com', 'tiktok.com', 'reddit.com'],
                'keywords': ['social', 'post', 'feed', 'comment'],
                'emoji': '📱',
                'health_modifier': -1.0,
                'happiness_modifier': 0.5,
                'dumpling_rate': -0.2  # lose dumplings
            },
            'news': {
                'domains': ['news.', 'cnn.com', 'bbc.com', 'nytimes.com', 'techcrunch.com', 'ycombinator.com'],
                'keywords': ['news', 'article', 'breaking'],
                'emoji': '📰',
                'health_modifier': -0.5,
                'happiness_modifier': 0.0,
                'dumpling_rate': 0.1
            },
            'entertainment': {
                'domains': ['youtube.com', 'netflix.com', 'twitch.tv', 'spotify.com'],
                'keywords': ['video', 'music', 'stream', 'watch'],
                'emoji': '🍿',
                'health_modifier': -1.5,
                'happiness_modifier': 2.0,
                'dumpling_rate': -0.1
            },
            'shopping': {
                'domains': ['amazon.com', 'ebay.com', 'etsy.com', 'shopify.com'],
                'keywords': ['shop', 'buy', 'cart', 'checkout'],
                'emoji': '🛒',
                'health_modifier': -0.5,
                'happiness_modifier': 1.0,
                'dumpling_rate': 0.0
            }
        }
        
        # Core stats
        self.current_state = 'idle'
        self.current_website = None
        self.current_website_category = None
        self.happiness = 50
        self.energy = 50
        self.health = 100
        
        # DUMPLING SYSTEM! 🥟
        self.dumplings = 0
        self.total_dumplings_earned = 0
        self.dumpling_earning_session = 0  # dumplings earned this session
        self.last_dumpling_time = datetime.now()
        self.dumpling_streaks = {
            'coding': 0,
            'productive_browsing': 0,
            'daily_goal': 0
        }
        
        # Enhanced time tracking
        self.session_start = datetime.now()
        self.state_start_time = datetime.now()
        self.website_start_time = datetime.now()
        self.productive_time_today = 0  # for daily goals
        
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
        self.website_time = {}
        self.daily_websites = []
        
        # Health tracking
        self.browsing_streak = 0
        self.social_media_streak = 0
        self.last_health_warning = None
        self.last_break_reminder = None
        self.last_website_report = None
        self.last_dumpling_celebration = None
        
        # Notification settings
        self.notifications_enabled = True
        
        # Load saved data
        self.load_data()
        
        # Create menu
        self.create_static_menu()
        
        # Send welcome notification with dumplings
        self.send_native_notification("🦕 Dumpling Dino Started!", 
                                    f"Current balance: 🥟 {self.dumplings} dumplings",
                                    "Earn dumplings by being productive! Check the store (coming soon)!")
        
        # Start monitoring
        self.start_monitoring()
        self.start_health_monitoring()
        self.start_dumpling_monitoring()
        self.start_notification_scheduler()
        
        print(f"🦕 Dumpling Dino Started! Current balance: 🥟 {self.dumplings}")
        print("🥟 Earn dumplings by coding, learning, and being productive!")
    
    def start_dumpling_monitoring(self):
        """Monitor and award dumplings based on activity"""
        def dumpling_monitor():
            while True:
                try:
                    self.calculate_dumpling_earnings()
                    self.check_dumpling_milestones()
                except Exception as e:
                    print(f"Dumpling monitor error: {e}")
                time.sleep(60)  # Check every minute
        
        threading.Thread(target=dumpling_monitor, daemon=True).start()
    
    def calculate_dumpling_earnings(self):
        """Calculate and award dumplings based on current activity"""
        now = datetime.now()
        time_since_last = (now - self.last_dumpling_time).total_seconds() / 60.0  # minutes
        
        if time_since_last < 1:
            return  # Don't award more than once per minute
        
        dumplings_earned = 0
        
        # Base earning rates by activity
        if self.current_state == 'coding':
            dumplings_earned = 2.0 * time_since_last  # 2 dumplings per minute coding
            self.dumpling_streaks['coding'] += time_since_last
        elif self.current_state == 'working':
            dumplings_earned = 1.0 * time_since_last  # 1 dumpling per minute working
        elif self.current_state == 'designing':
            dumplings_earned = 1.5 * time_since_last  # 1.5 dumplings per minute designing
        elif self.current_state.startswith('browsing_'):
            # Website-specific rates
            if self.current_website_category in self.website_categories:
                rate = self.website_categories[self.current_website_category]['dumpling_rate']
                dumplings_earned = rate * time_since_last
                
                if self.current_website_category == 'productive':
                    self.dumpling_streaks['productive_browsing'] += time_since_last
        
        # Bonus multipliers
        # Coding streak bonus
        if self.dumpling_streaks['coding'] > 30:  # 30+ minutes coding
            dumplings_earned *= 1.5
        
        # Health bonus
        if self.health > 80:
            dumplings_earned *= 1.2
        elif self.health < 30:
            dumplings_earned *= 0.5
        
        # Round and apply
        if dumplings_earned > 0:
            final_dumplings = round(dumplings_earned, 1)
            self.award_dumplings(final_dumplings, f"{self.get_current_status()}")
        elif dumplings_earned < 0:
            # Lose dumplings for distracting activities
            final_loss = round(abs(dumplings_earned), 1)
            self.lose_dumplings(final_loss, "Distracting activity")
        
        self.last_dumpling_time = now
    
    def award_dumplings(self, amount, reason):
        """Award dumplings and send notification"""
        self.dumplings += amount
        self.total_dumplings_earned += amount
        self.dumpling_earning_session += amount
        
        # Celebration notification for significant earnings
        if (not self.last_dumpling_celebration or 
            datetime.now() - self.last_dumpling_celebration > timedelta(minutes=5)):
            
            if amount >= 5:
                self.send_native_notification(
                    f"🥟 +{amount} Dumplings Earned!",
                    f"Total: 🥟 {self.dumplings} dumplings",
                    f"Great work! Reason: {reason}"
                )
                self.last_dumpling_celebration = datetime.now()
        
        print(f"🥟 +{amount} dumplings! Total: {self.dumplings} | Reason: {reason}")
    
    def lose_dumplings(self, amount, reason):
        """Lose dumplings for distracting activities"""
        if self.dumplings > 0:
            lost = min(amount, self.dumplings)
            self.dumplings -= lost
            print(f"🥟 -{lost} dumplings lost. Total: {self.dumplings} | Reason: {reason}")
    
    def check_dumpling_milestones(self):
        """Check and celebrate dumpling milestones"""
        milestones = [10, 25, 50, 100, 200, 500, 1000]
        
        for milestone in milestones:
            if (self.total_dumplings_earned >= milestone and 
                not hasattr(self, f'milestone_{milestone}_reached')):
                
                setattr(self, f'milestone_{milestone}_reached', True)
                
                self.send_native_notification(
                    f"🎉 Milestone Reached!",
                    f"🥟 {milestone} total dumplings earned!",
                    "Your productivity is paying off! Keep up the great work!"
                )
                break
    
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
        """Create static menu items with dumpling display"""
        self.status_item = rumps.MenuItem("Status: Just chilling")
        self.website_item = rumps.MenuItem("🌐 Website: None")
        
        # DUMPLING DISPLAY! 🥟
        self.dumplings_item = rumps.MenuItem(f"🥟 Dumplings: {self.dumplings}")
        self.session_earnings_item = rumps.MenuItem(f"📈 Session Earned: +{self.dumpling_earning_session}")
        
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
            self.dumplings_item,
            self.session_earnings_item,
            rumps.MenuItem("🏪 Dumpling Store (Coming Soon!)", callback=self.show_store_preview),
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
            rumps.MenuItem("Dumpling Stats 🥟", callback=self.show_dumpling_stats),
            rumps.separator,
            self.notifications_toggle,
            rumps.MenuItem("Reset Day", callback=self.reset),
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]
        
        # Initial update
        self.update_all_menu_items()
    
    @rumps.clicked("🏪 Dumpling Store (Coming Soon!)")
    def show_store_preview(self, sender):
        """Show store preview with future features"""
        self.send_native_notification(
            "🏪 Dumpling Store Preview",
            "Coming Soon! Here's what you'll be able to buy:",
            "🎨 Dino skins • ⚡ Power-ups • 📊 Analytics • 🎮 Mini-games • 🏆 Achievements"
        )
    
    @rumps.clicked("Dumpling Stats 🥟")
    def show_dumpling_stats(self, sender):
        """Show detailed dumpling statistics"""
        earning_rate = self.dumpling_earning_session / max(1, (datetime.now() - self.session_start).total_seconds() / 3600)  # per hour
        
        self.send_native_notification(
            "🥟 Your Dumpling Stats",
            f"Balance: {self.dumplings} | Total Earned: {self.total_dumplings_earned}",
            f"Session: +{self.dumpling_earning_session} | Rate: {earning_rate:.1f}/hour"
        )
    
    @rumps.clicked("🔔 Notifications: ON")
    def toggle_notifications(self, sender):
        """Toggle notifications on/off"""
        self.notifications_enabled = not self.notifications_enabled
        status = "ON" if self.notifications_enabled else "OFF"
        self.notifications_toggle.title = f"🔔 Notifications: {status}"
        
        if self.notifications_enabled:
            self.send_native_notification("🔔 Notifications Enabled", 
                                        "Dumpling earning alerts active!", 
                                        "You'll now receive dumpling notifications for productivity!")
    
    def start_notification_scheduler(self):
        """Enhanced notification scheduler with dumpling insights"""
        def notification_scheduler():
            while True:
                try:
                    now = datetime.now()
                    
                    # Daily dumpling goal check
                    if now.hour == 17 and now.minute < 5:  # 5 PM reminder
                        daily_goal = 50  # 50 dumplings per day
                        if self.dumpling_earning_session < daily_goal:
                            remaining = daily_goal - self.dumpling_earning_session
                            self.send_native_notification(
                                "🎯 Daily Dumpling Goal",
                                f"🥟 {remaining} more dumplings to hit daily goal!",
                                "Keep coding and learning to reach your target!"
                            )
                    
                    # Streak celebrations
                    if self.dumpling_streaks['coding'] >= 60:  # 1 hour coding streak
                        self.send_native_notification(
                            "🔥 Coding Streak!",
                            f"🥟 Bonus earnings activated!",
                            f"{self.dumpling_streaks['coding']:.0f} minutes of coding - you're on fire!"
                        )
                        self.dumpling_streaks['coding'] = 0  # Reset to avoid spam
                        
                except Exception as e:
                    print(f"Notification scheduler error: {e}")
                
                time.sleep(300)  # Check every 5 minutes
        
        threading.Thread(target=notification_scheduler, daemon=True).start()
    
    def get_current_browser_url(self):
        """Get the current URL from Chrome using AppleScript"""
        try:
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
            
            return None, None
            
        except Exception as e:
            print(f"Error getting browser URL: {e}")
            return None, None
    
    def categorize_website(self, url, title=""):
        """Categorize a website based on URL and title"""
        if not url:
            return 'other'
        
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '')
            path = parsed.path.lower()
            full_url = (url + " " + title).lower()
            
            for category, config in self.website_categories.items():
                for domain_pattern in config['domains']:
                    if domain_pattern in domain:
                        return category
                
                for keyword in config['keywords']:
                    if keyword in full_url:
                        return category
            
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
    
    def update_all_menu_items(self):
        """Update all menu items with current data including dumplings"""
        try:
            status_text = self.get_current_status()
            self.status_item.title = f"Status: {status_text}"
            
            # Update dumpling display
            self.dumplings_item.title = f"🥟 Dumplings: {self.dumplings}"
            self.session_earnings_item.title = f"📈 Session Earned: +{self.dumpling_earning_session:.1f}"
            
            # Website info
            if self.current_website:
                try:
                    domain = urlparse(self.current_website).netloc.replace('www.', '')
                    category_emoji = self.website_categories.get(self.current_website_category, {}).get('emoji', '🌐')
                    
                    # Show dumpling rate for current website
                    dumpling_rate = self.website_categories.get(self.current_website_category, {}).get('dumpling_rate', 0)
                    rate_display = f" (+{dumpling_rate}/min)" if dumpling_rate > 0 else f" ({dumpling_rate}/min)" if dumpling_rate < 0 else ""
                    
                    self.website_item.title = f"{category_emoji} {domain}{rate_display}"
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
            
            # Enhanced time breakdown with dumpling earning potential
            self.productive_item.title = f"  📖 Productive Sites: {self.format_time(self.time_spent['browsing_productive'])} (🥟+1.0/min)"
            self.work_item.title = f"  💼 Work Sites: {self.format_time(self.time_spent['browsing_work'])} (🥟+0.8/min)"
            self.social_item.title = f"  📱 Social Media: {self.format_time(self.time_spent['browsing_social'])} (🥟-0.2/min)"
            self.news_item.title = f"  📰 News Sites: {self.format_time(self.time_spent['browsing_news'])} (🥟+0.1/min)"
            self.entertainment_item.title = f"  🍿 Entertainment: {self.format_time(self.time_spent['browsing_entertainment'])} (🥟-0.1/min)"
            self.shopping_item.title = f"  🛒 Shopping: {self.format_time(self.time_spent['browsing_shopping'])} (🥟0/min)"
            self.other_browsing_item.title = f"  🌐 Other Browsing: {self.format_time(self.time_spent['browsing_other'])}"
            
            self.coding_item.title = f"  💻 Coding: {self.format_time(self.time_spent['coding'])} (🥟+2.0/min)"
            self.designing_item.title = f"  🎨 Designing: {self.format_time(self.time_spent['designing'])} (🥟+1.5/min)"
            
            # Update menu bar icon with dumpling indicator
            health_indicator = ""
            if self.health < 30:
                health_indicator = "🚨"
            elif self.health < 60:
                health_indicator = "⚠️"
            
            # Show dumpling count in menu bar for milestones
            dumpling_indicator = ""
            if self.dumplings >= 100:
                dumpling_indicator = "💰"
            elif self.dumplings >= 50:
                dumpling_indicator = "🥟"
            
            self.title = f"{self.states[self.current_state]}{health_indicator}{dumpling_indicator}"
            
        except Exception as e:
            print(f"Error updating menu: {e}")
    
    def get_current_status(self):
        """Get descriptive status text with website info"""
        base_status = {
            'idle': "Just chilling",
            'working': "Working hard on Slack!",
            'coding': "Coding like a pro! 🥟+2.0/min",
            'designing': "Designing something beautiful! 🥟+1.5/min",
            'browsing_productive': "Learning something new! 🥟+1.0/min",
            'browsing_work': "Handling work tasks 🥟+0.8/min",
            'browsing_social': "Checking social media 🥟-0.2/min",
            'browsing_news': "Reading the news 🥟+0.1/min",
            'browsing_entertainment': "Enjoying entertainment 🥟-0.1/min",
            'browsing_shopping': "Shopping online",
            'browsing_distraction': "Getting distracted...",
            'gaming': "Gaming time!",
            'sick': "Dino is very sick! 🤒",
            'dead': "Dino has died! 💀"
        }.get(self.current_state, "Unknown state")
        
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
        """Enhanced health monitoring with dumpling warnings"""
        def health_monitor():
            while True:
                try:
                    now = datetime.now()
                    
                    # Social media addiction warning with dumpling loss
                    if self.social_media_streak > 900:  # 15 minutes
                        self.send_native_notification(
                            "📱 Social Media Alert!",
                            f"🥟 Losing dumplings! {self.format_time(self.social_media_streak)} on social media",
                            "Your dumpling earning rate is negative! Switch to productive activities!"
                        )
                        self.social_media_streak = 0
                    
                    # Health warnings
                    if self.health < 30 and (not self.last_health_warning or 
                       now - self.last_health_warning > timedelta(minutes=10)):
                        dumpling_bonus = min(10, self.dumplings * 0.1)
                        self.send_native_notification(
                            "🚨 Health Critical!",
                            f"🥟 Earn {dumpling_bonus:.0f} bonus dumplings for recovery!",
                            "Take a break or do productive activities to restore health!"
                        )
                        self.last_health_warning = now
                        
                except Exception as e:
                    print(f"Health monitor error: {e}")
                
                time.sleep(30)
        
        threading.Thread(target=health_monitor, daemon=True).start()
    
    # ... (keeping all the website tracking methods from previous version)
    
    def check_current_activity(self):
        """Enhanced activity checking with website monitoring"""
        try:
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
                
                if any(browser in app_name for browser in ['chrome', 'safari', 'firefox']):
                    url, title = self.get_current_browser_url()
                    self.update_browsing_state(url, title, app_name)
                else:
                    self.update_non_browsing_state(app_name)
                
        except Exception as e:
            print(f"Error checking activity: {e}")
    
    def update_browsing_state(self, url, title, browser):
        """Update state based on current website"""
        self.track_time_spent()
        
        old_website = self.current_website
        self.current_website = url
        
        if url:
            category = self.categorize_website(url, title)
            self.current_website_category = category
            
            try:
                domain = urlparse(url).netloc.replace('www.', '')
                if domain not in self.website_time:
                    self.website_time[domain] = 0
                
                if old_website != url:
                    self.daily_websites.append({
                        'domain': domain,
                        'category': category,
                        'timestamp': datetime.now().isoformat(),
                        'duration': 0
                    })
                    
            except Exception as e:
                print(f"Error tracking website: {e}")
            
            emoji, new_state = self.get_website_display_info(category)
            self.apply_website_effects(category, url)
            
        else:
            new_state = 'browsing_other'
            self.current_website_category = 'other'
        
        old_state = self.current_state
        self.current_state = new_state
        self.website_start_time = datetime.now()
        
        self.update_all_menu_items()
        
        if old_website != url and url:
            try:
                domain = urlparse(url).netloc.replace('www.', '')
                category_emoji = self.website_categories.get(self.current_website_category, {}).get('emoji', '🌐')
                dumpling_rate = self.website_categories.get(self.current_website_category, {}).get('dumpling_rate', 0)
                
                if dumpling_rate > 0:
                    subtitle = f"🥟 +{dumpling_rate}/min | {domain}"
                elif dumpling_rate < 0:
                    subtitle = f"🥟 {dumpling_rate}/min | {domain}"
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
            
            health_change = config['health_modifier'] * 0.5
            happiness_change = config['happiness_modifier'] * 0.3
            
            self.health = max(0, min(100, self.health + health_change))
            self.happiness = max(0, min(100, self.happiness + happiness_change))
            
            if category == 'social':
                self.social_media_streak += 3
            else:
                self.social_media_streak = 0
    
    def update_non_browsing_state(self, app_name):
        """Update state for non-browser applications"""
        self.track_time_spent()
        
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
        self.update_all_menu_items()
        
        if old_state != new_state and new_state != 'idle':
            status = self.get_current_status()
            self.send_native_notification(
                f"🔄 App Change: {self.states[new_state]}",
                f"Health: {self.health}% | 🥟 {self.dumplings} dumplings",
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
                
                # Track productive time for daily goals
                if self.current_state in ['coding', 'working', 'designing', 'browsing_productive']:
                    self.productive_time_today += time_delta
        
        if hasattr(self, 'website_start_time') and self.current_website:
            try:
                website_delta = (datetime.now() - self.website_start_time).total_seconds()
                domain = urlparse(self.current_website).netloc.replace('www.', '')
                if domain in self.website_time:
                    self.website_time[domain] += website_delta
                
                if self.daily_websites:
                    self.daily_websites[-1]['duration'] += website_delta
                    
            except Exception as e:
                print(f"Error tracking website time: {e}")
        
        self.state_start_time = datetime.now()
        self.website_start_time = datetime.now()
    
    # ... (keeping all the menu callback methods)
    
    @rumps.clicked("Feed 🍖")
    def feed(self, sender):
        cost = 5  # Feeding costs 5 dumplings but gives big health boost
        if self.dumplings >= cost:
            self.dumplings -= cost
            old_state = self.current_state
            self.current_state = 'eating'
            self.happiness = min(100, self.happiness + 30)
            health_boost = min(100, self.health + 20)
            old_health = self.health
            self.health = health_boost
            
            self.update_all_menu_items()
            
            self.send_native_notification(
                "🍖 Dino Fed! (🥟 -5)",
                f"Health: {old_health}% → {self.health}% | Happiness: +30",
                f"Your dino is much happier! 🥟 {self.dumplings} dumplings remaining"
            )
            
            def reset_after_eating():
                time.sleep(3)
                self.current_state = old_state
                self.update_all_menu_items()
            
            threading.Thread(target=reset_after_eating, daemon=True).start()
        else:
            self.send_native_notification(
                "🍖 Not Enough Dumplings!",
                f"Need 🥟 5 dumplings (have {self.dumplings})",
                "Keep coding and learning to earn more dumplings!"
            )
    
    @rumps.clicked("Pet 🫳") 
    def pet(self, sender):
        # Petting is free but gives smaller boost
        old_state = self.current_state
        self.current_state = 'excited'
        self.happiness = min(100, self.happiness + 15)
        self.health = min(100, self.health + 5)
        
        self.update_all_menu_items()
        
        self.send_native_notification(
            "✨ Dino Petted! (Free!)",
            f"Your dino is overjoyed! Happiness: +15",
            f"Free love! 🥟 {self.dumplings} dumplings saved!"
        )
        
        def reset_after_petting():
            time.sleep(2)
            self.current_state = old_state
            self.update_all_menu_items()
        
        threading.Thread(target=reset_after_petting, daemon=True).start()
    
    @rumps.clicked("Take Break 🧘")
    def take_break(self, sender):
        # Taking a break earns bonus dumplings!
        bonus_dumplings = 3
        self.award_dumplings(bonus_dumplings, "Taking a healthy break")
        
        old_health = self.health
        old_energy = self.energy
        
        self.health = min(100, self.health + 15)
        self.energy = min(100, self.energy + 20)
        self.happiness = min(100, self.happiness + 10)
        self.social_media_streak = 0
        self.last_break_reminder = datetime.now()
        
        self.update_all_menu_items()
        
        self.send_native_notification(
            f"🧘 Break Taken! (🥟 +{bonus_dumplings})",
            f"Health: +{self.health - old_health} | Energy: +{self.energy - old_energy}",
            f"Self-care earns dumplings! 🥟 {self.dumplings} total"
        )
    
    @rumps.clicked("Reset Day")
    def reset(self, sender):
        # Save session summary before reset
        session_dumplings = self.dumpling_earning_session
        
        self.current_state = 'idle'
        self.current_website = None
        self.current_website_category = None
        self.happiness = 50
        self.energy = 50
        self.health = 100
        self.social_media_streak = 0
        self.dumpling_earning_session = 0
        self.productive_time_today = 0
        self.session_start = datetime.now()
        
        old_website_time = self.website_time.copy()
        
        self.time_spent = {key: 0 for key in self.time_spent}
        self.website_time = {}
        self.daily_websites = []
        
        # Reset streaks
        self.dumpling_streaks = {key: 0 for key in self.dumpling_streaks}
        
        self.update_all_menu_items()
        
        self.send_native_notification(
            "🔄 Day Reset Complete!",
            f"🥟 Session earned: {session_dumplings:.1f} dumplings",
            f"Fresh start! Current balance: 🥟 {self.dumplings} dumplings"
        )
    
    def save_data(self):
        """Enhanced save with dumpling data"""
        try:
            data = {
                'happiness': self.happiness,
                'energy': self.energy, 
                'health': self.health,
                'dumplings': self.dumplings,
                'total_dumplings_earned': self.total_dumplings_earned,
                'dumpling_earning_session': self.dumpling_earning_session,
                'dumpling_streaks': self.dumpling_streaks,
                'productive_time_today': self.productive_time_today,
                'time_spent': self.time_spent,
                'website_time': self.website_time,
                'daily_websites': self.daily_websites,
                'session_start': self.session_start.isoformat(),
                'social_media_streak': self.social_media_streak,
                'notifications_enabled': self.notifications_enabled
            }
            
            save_dir = os.path.expanduser("~/.dino_tamagotchi")
            os.makedirs(save_dir, exist_ok=True)
            
            with open(os.path.join(save_dir, "dumpling_dino_data.json"), "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        """Enhanced load with dumpling data"""
        try:
            save_dir = os.path.expanduser("~/.dino_tamagotchi")
            data_file = os.path.join(save_dir, "dumpling_dino_data.json")
            
            if os.path.exists(data_file):
                with open(data_file, "r") as f:
                    data = json.load(f)
                
                self.happiness = data.get('happiness', 50)
                self.energy = data.get('energy', 50)
                self.health = data.get('health', 100)
                self.dumplings = data.get('dumplings', 0)
                self.total_dumplings_earned = data.get('total_dumplings_earned', 0)
                self.dumpling_earning_session = data.get('dumpling_earning_session', 0)
                self.dumpling_streaks = data.get('dumpling_streaks', {'coding': 0, 'productive_browsing': 0, 'daily_goal': 0})
                self.productive_time_today = data.get('productive_time_today', 0)
                self.time_spent = data.get('time_spent', self.time_spent)
                self.website_time = data.get('website_time', {})
                self.daily_websites = data.get('daily_websites', [])
                self.social_media_streak = data.get('social_media_streak', 0)
                self.notifications_enabled = data.get('notifications_enabled', True)
                
                try:
                    saved_start = datetime.fromisoformat(data.get('session_start', datetime.now().isoformat()))
                    if (datetime.now() - saved_start).days > 0:
                        self.time_spent = {key: 0 for key in self.time_spent}
                        self.daily_websites = []
                        self.dumpling_earning_session = 0
                        self.productive_time_today = 0
                        self.session_start = datetime.now()
                    else:
                        self.session_start = saved_start
                except:
                    self.session_start = datetime.now()
                    
        except Exception as e:
            print(f"Error loading data: {e}")

if __name__ == "__main__":
    print("🦕 Starting Dumpling Dino...")
    DumplingDino().run()