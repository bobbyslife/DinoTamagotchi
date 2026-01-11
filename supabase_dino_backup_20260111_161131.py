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
import uuid
from supabase import create_client, Client

class SupabaseDino(rumps.App):
    def __init__(self):
        super(SupabaseDino, self).__init__("🦕", quit_button=None)
        
        # Supabase Configuration
        # Import from config.py or use environment variables for production
        try:
            from config import SUPABASE_URL, SUPABASE_KEY, USE_SUPABASE
            self.use_supabase = USE_SUPABASE
        except ImportError:
            # Fallback configuration - replace with your actual credentials
            SUPABASE_URL = "https://vcclceadrxrswxaxiitj.supabase.co"
            SUPABASE_KEY = "sb_publishable_1SGzjoZCE65W6cNRU0_K4Q_CQTXYbCT"
            self.use_supabase = True
        
        if self.use_supabase:
            try:
                self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
                print("🗄️ Connected to Supabase!")
            except Exception as e:
                print(f"❌ Supabase connection failed: {e}")
                self.use_supabase = False
        else:
            print("🗄️ Running in demo mode (no Supabase connection)")
        
        # User identification
        self.user_id = self.load_or_create_user_id()
        self.username = self.load_or_create_username()
        
        # Dino states (keeping from previous version)
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
        
        # Website categories (expanded with more categories and custom learning)
        self.website_categories = {
            'productive': {
                'domains': ['github.com', 'stackoverflow.com', 'docs.', 'developer.', 'learn.', 'coursera.com', 'udemy.com'],
                'keywords': ['documentation', 'tutorial', 'learn', 'course', 'guide'],
                'dumpling_rate': 1.0,
                'emoji': '📖'
            },
            'work': {
                'domains': ['gmail.com', 'google.com/drive', 'notion.so', 'trello.com', 'asana.com', 'monday.com'],
                'keywords': ['email', 'calendar', 'meeting', 'project'],
                'dumpling_rate': 0.8,
                'emoji': '💼'
            },
            'social': {
                'domains': ['twitter.com', 'x.com', 'facebook.com', 'instagram.com', 'reddit.com', 'tiktok.com'],
                'keywords': ['social', 'post', 'feed', 'comment'],
                'dumpling_rate': -0.2,
                'emoji': '📱'
            },
            'news': {
                'domains': ['news.', 'cnn.com', 'bbc.com', 'nytimes.com', 'techcrunch.com', 'ycombinator.com'],
                'keywords': ['news', 'article', 'breaking'],
                'dumpling_rate': -0.1,
                'emoji': '📰'
            },
            'entertainment': {
                'domains': ['youtube.com', 'netflix.com', 'twitch.tv', 'spotify.com'],
                'keywords': ['video', 'music', 'stream', 'watch'],
                'dumpling_rate': -0.3,
                'emoji': '🍿'
            },
            'shopping': {
                'domains': ['amazon.com', 'ebay.com', 'etsy.com', 'shopify.com'],
                'keywords': ['shop', 'buy', 'cart', 'checkout'],
                'dumpling_rate': -0.15,
                'emoji': '🛒'
            }
        }
        
        # Custom user-defined website categories
        self.custom_website_categories = self.load_custom_categories()
        
        # Core stats
        self.current_state = 'idle'
        self.current_website = None
        self.current_website_category = None
        self.happiness = 50
        self.energy = 50
        self.health = 100
        
        # Dumpling system
        self.dumplings = 0
        self.total_dumplings_earned = 0
        self.dumpling_earning_session = 0
        self.last_dumpling_time = datetime.now()
        
        # Multiplayer stats
        self.friends_list = []
        self.daily_ranking = 0
        self.online_friends = []
        
        # Time tracking
        self.session_start = datetime.now()
        self.state_start_time = datetime.now()
        self.productive_time_today = 0
        
        self.time_spent = {
            'coding': 0,
            'working': 0,
            'designing': 0,
            'browsing_productive': 0,
            'browsing_social': 0,
            'browsing_news': 0,
            'browsing_entertainment': 0,
            'browsing_shopping': 0,
            'browsing_other': 0
        }
        
        # Social monitoring
        self.last_social_update = None
        self.last_leaderboard_check = None
        self.last_sync_time = datetime.now()
        
        # Notification settings
        self.notifications_enabled = True
        self.social_notifications_enabled = True
        
        # Load saved data
        self.load_data()
        
        # Initialize user in database
        self.initialize_user()
        
        # Create menu
        self.create_static_menu()
        
        # Send welcome notification
        self.send_native_notification("🦕 Supabase Dino Started!", 
                                    f"Welcome {self.username}! 🥟 {self.dumplings} dumplings",
                                    "Real-time multiplayer enabled! Compete with friends!")
        
        # Start monitoring
        self.start_monitoring()
        self.start_dumpling_monitoring()
        self.start_social_monitoring()
        self.start_realtime_sync()
        
        print(f"🦕 Supabase Dino Started!")
        print(f"👤 User: {self.username} (ID: {self.user_id})")
        print(f"🥟 Dumplings: {self.dumplings}")
        print(f"🗄️ Database: {'Supabase' if self.use_supabase else 'Local Demo'}")
    
    def load_or_create_user_id(self):
        """Load existing user ID or create new one"""
        user_file = os.path.expanduser("~/.dino_tamagotchi/user_id.txt")
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                return f.read().strip()
        else:
            new_id = str(uuid.uuid4())[:8]
            os.makedirs(os.path.dirname(user_file), exist_ok=True)
            with open(user_file, 'w') as f:
                f.write(new_id)
            return new_id
    
    def load_or_create_username(self):
        """Load existing username or create default"""
        username_file = os.path.expanduser("~/.dino_tamagotchi/username.txt")
        if os.path.exists(username_file):
            with open(username_file, 'r') as f:
                return f.read().strip()
        else:
            import getpass
            username = f"Dino_{getpass.getuser()}_{self.user_id[:4]}"
            os.makedirs(os.path.dirname(username_file), exist_ok=True)
            with open(username_file, 'w') as f:
                f.write(username)
            return username
    
    def initialize_user(self):
        """Initialize user in Supabase database"""
        if not self.use_supabase:
            return
        
        try:
            # Check if user exists
            result = self.supabase.table('users').select('*').eq('user_id', self.user_id).execute()
            
            if not result.data:
                # Create new user
                new_user = {
                    'user_id': self.user_id,
                    'username': self.username,
                    'dumplings': self.dumplings,
                    'total_dumplings_earned': self.total_dumplings_earned,
                    'health': self.health,
                    'happiness': self.happiness,
                    'energy': self.energy,
                    'current_state': self.current_state,
                    'last_activity': datetime.now().isoformat(),
                    'created_at': datetime.now().isoformat()
                }
                
                self.supabase.table('users').insert(new_user).execute()
                print(f"✅ Created new user in database: {self.username}")
            else:
                print(f"✅ User already exists in database: {self.username}")
                
        except Exception as e:
            print(f"❌ Error initializing user: {e}")
    
    def sync_to_supabase(self):
        """Sync current user data to Supabase"""
        if not self.use_supabase:
            # Demo mode - save to local file for simulation
            self.save_demo_data()
            return
        
        try:
            user_data = {
                'username': self.username,
                'dumplings': self.dumplings,
                'total_dumplings_earned': self.total_dumplings_earned,
                'health': self.health,
                'happiness': self.happiness,
                'energy': self.energy,
                'current_state': self.current_state,
                'productive_time_today': self.productive_time_today,
                'session_dumplings': self.dumpling_earning_session,
                'last_activity': datetime.now().isoformat(),
                'coding_time_today': self.time_spent.get('coding', 0),
                'social_media_time_today': self.time_spent.get('browsing_social', 0)
            }
            
            # Update user data
            self.supabase.table('users').update(user_data).eq('user_id', self.user_id).execute()
            
            # Log activity for friends to see
            activity_data = {
                'user_id': self.user_id,
                'activity_type': self.current_state,
                'dumplings_earned': self.dumpling_earning_session,
                'duration_minutes': (datetime.now() - self.session_start).total_seconds() / 60,
                'timestamp': datetime.now().isoformat()
            }
            
            self.supabase.table('activities').insert(activity_data).execute()
            self.last_sync_time = datetime.now()
            
        except Exception as e:
            print(f"❌ Error syncing to Supabase: {e}")
    
    def save_demo_data(self):
        """Save data to local file for demo mode"""
        try:
            demo_data = {
                'user_id': self.user_id,
                'username': self.username,
                'dumplings': self.dumplings,
                'total_dumplings_earned': self.total_dumplings_earned,
                'health': self.health,
                'happiness': self.happiness,
                'energy': self.energy,
                'current_state': self.current_state,
                'productive_time_today': self.productive_time_today,
                'session_dumplings': self.dumpling_earning_session,
                'last_activity': datetime.now().isoformat(),
                'coding_time_today': self.time_spent.get('coding', 0),
                'social_media_time_today': self.time_spent.get('browsing_social', 0)
            }
            
            demo_dir = os.path.expanduser("~/Desktop/DinoTamagotchi/supabase_demo_data")
            os.makedirs(demo_dir, exist_ok=True)
            
            with open(f"{demo_dir}/{self.user_id}.json", 'w') as f:
                json.dump(demo_data, f)
                
        except Exception as e:
            print(f"Error saving demo data: {e}")
    
    def get_friends_data(self):
        """Get friends' data from Supabase or demo files"""
        if self.use_supabase:
            return self.get_supabase_friends()
        else:
            return self.get_demo_friends()
    
    def get_supabase_friends(self):
        """Get friends data from Supabase"""
        try:
            # Get all users who were active in the last hour
            one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            
            result = self.supabase.table('users').select('*').gte('last_activity', one_hour_ago).neq('user_id', self.user_id).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error getting friends from Supabase: {e}")
            return []
    
    def get_demo_friends(self):
        """Get friends data from demo files"""
        try:
            friends_data = []
            demo_dir = os.path.expanduser("~/Desktop/DinoTamagotchi/supabase_demo_data")
            
            if not os.path.exists(demo_dir):
                return friends_data
            
            for filename in os.listdir(demo_dir):
                if filename.endswith('.json') and filename != f"{self.user_id}.json":
                    try:
                        with open(f"{demo_dir}/{filename}", 'r') as f:
                            friend_data = json.load(f)
                            
                            # Only include recent activity (last hour)
                            last_activity = datetime.fromisoformat(friend_data['last_activity'])
                            if (datetime.now() - last_activity).total_seconds() < 3600:
                                friends_data.append(friend_data)
                    except Exception as e:
                        print(f"Error reading demo friend data {filename}: {e}")
            
            return friends_data
            
        except Exception as e:
            print(f"Error getting demo friends: {e}")
            return []
    
    def start_social_monitoring(self):
        """Monitor friends' activities and send social pressure notifications"""
        def social_monitor():
            while True:
                try:
                    if self.social_notifications_enabled:
                        self.check_competitive_updates()
                        self.check_friend_achievements()
                except Exception as e:
                    print(f"Social monitor error: {e}")
                time.sleep(180)  # Check every 3 minutes
        
        threading.Thread(target=social_monitor, daemon=True).start()
    
    def start_realtime_sync(self):
        """Start real-time syncing with Supabase"""
        def sync_loop():
            while True:
                try:
                    self.sync_to_supabase()
                except Exception as e:
                    print(f"Sync error: {e}")
                time.sleep(60)  # Sync every minute
        
        threading.Thread(target=sync_loop, daemon=True).start()
    
    def check_competitive_updates(self):
        """Check for competitive updates and send notifications"""
        try:
            friends_data = self.get_friends_data()
            
            if not friends_data or len(friends_data) == 0:
                return
            
            now = datetime.now()
            
            # Don't spam notifications
            if (self.last_social_update and 
                now - self.last_social_update < timedelta(minutes=10)):
                return
            
            # Find the highest performer today
            top_performer = max(friends_data, key=lambda x: x.get('session_dumplings', 0))
            my_session_dumplings = self.dumpling_earning_session
            
            # If someone is significantly ahead of you
            if top_performer['session_dumplings'] > my_session_dumplings + 20:
                gap = top_performer['session_dumplings'] - my_session_dumplings
                
                self.send_native_notification(
                    "🏃‍♂️ You're Falling Behind!",
                    f"{top_performer['username']} is ahead by 🥟 {gap:.1f} dumplings!",
                    f"They're {top_performer['current_state'].replace('_', ' ')}. Time to step up!"
                )
                self.last_social_update = now
                return
            
            # If you're leading, motivate to stay ahead
            elif my_session_dumplings > top_performer['session_dumplings']:
                gap = my_session_dumplings - top_performer['session_dumplings']
                
                self.send_native_notification(
                    "👑 You're Leading!",
                    f"🥟 Ahead by {gap:.1f} dumplings!",
                    f"{top_performer['username']} is trying to catch up. Keep it up!"
                )
                self.last_social_update = now
                
        except Exception as e:
            print(f"Error checking competitive updates: {e}")
    
    def check_friend_achievements(self):
        """Check for friend achievements and milestones"""
        try:
            friends_data = self.get_friends_data()
            
            for friend in friends_data:
                # Friend just hit a major milestone
                if friend.get('total_dumplings_earned', 0) % 100 < 2:  # Just hit 100, 200, etc.
                    milestone = int(friend['total_dumplings_earned'] / 100) * 100
                    self.send_native_notification(
                        "🏆 Friend Milestone!",
                        f"{friend['username']} just hit 🥟 {milestone} total dumplings!",
                        "That's some serious productivity! Can you match their dedication?"
                    )
                    break
                
                # Friend has been very productive today
                elif friend.get('coding_time_today', 0) > 7200:  # 2+ hours coding
                    self.send_native_notification(
                        "🔥 Friend Coding Marathon!",
                        f"{friend['username']} coded for 2+ hours today!",
                        "They're in the zone! Join the coding session?"
                    )
                    break
                    
        except Exception as e:
            print(f"Error checking friend achievements: {e}")
    
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
        """Create static menu items with Supabase features"""
        self.status_item = rumps.MenuItem("Status: Just chilling")
        
        # User info with database status
        db_status = "🗄️ Supabase" if self.use_supabase else "🗄️ Demo Mode"
        self.user_info_item = rumps.MenuItem(f"👤 {self.username} | {db_status}")
        self.dumplings_item = rumps.MenuItem(f"🥟 Dumplings: {self.dumplings}")
        self.session_earnings_item = rumps.MenuItem(f"📈 Session: +{self.dumpling_earning_session:.1f}")
        self.ranking_item = rumps.MenuItem("🏆 Loading rankings...")
        
        self.health_item = rumps.MenuItem(f"🦕 Health: {self.health}%")
        self.happiness_item = rumps.MenuItem(f"😊 Happiness: {self.happiness}%")
        self.energy_item = rumps.MenuItem(f"⚡ Energy: {self.energy}%")
        
        # Website tracking
        self.website_item = rumps.MenuItem("🌐 Website: None")
        
        self.session_item = rumps.MenuItem("⏰ Session: 0m")
        
        # Time tracking
        self.coding_item = rumps.MenuItem("  💻 Coding: 0m (🥟+2.0/min)")
        self.working_item = rumps.MenuItem("  💼 Working: 0m (🥟+0.8/min)")
        self.productive_item = rumps.MenuItem("  📖 Learning: 0m (🥟+1.0/min)")
        self.social_item = rumps.MenuItem("  📱 Social: 0m (🥟-0.2/min)")
        self.news_item = rumps.MenuItem("  📰 News: 0m (🥟-0.1/min)")
        self.entertainment_item = rumps.MenuItem("  🍿 Entertainment: 0m (🥟-0.3/min)")
        self.shopping_item = rumps.MenuItem("  🛒 Shopping: 0m (🥟-0.15/min)")
        
        # Initialize pending categorizations
        self.pending_categorizations = {}
        
        # Multiplayer controls
        self.notifications_toggle = rumps.MenuItem("🔔 Notifications: ON", callback=self.toggle_notifications)
        self.social_toggle = rumps.MenuItem("👥 Social Alerts: ON", callback=self.toggle_social_notifications)
        
        # Set the menu
        self.menu = [
            self.status_item,
            rumps.separator,
            self.user_info_item,
            self.dumplings_item,
            self.session_earnings_item,
            self.ranking_item,
            rumps.separator,
            rumps.MenuItem("🗄️ Supabase Features:"),
            rumps.MenuItem("📊 View Live Leaderboard", callback=self.show_leaderboard),
            rumps.MenuItem("👥 Setup Multiplayer", callback=self.setup_multiplayer),
            rumps.MenuItem("🆔 Share User ID", callback=self.share_user_id),
            rumps.separator,
            self.health_item,
            self.happiness_item,
            self.energy_item,
            rumps.separator,
            self.website_item,
            rumps.separator,
            self.session_item,
            rumps.MenuItem("📊 Time Tracking:"),
            self.coding_item,
            self.working_item,
            self.productive_item,
            self.social_item,
            self.news_item,
            self.entertainment_item,
            self.shopping_item,
            rumps.separator,
            rumps.MenuItem("Feed 🍖 (🥟-5)", callback=self.feed),
            rumps.MenuItem("Pet 🫳 (Free!)", callback=self.pet),
            rumps.MenuItem("Take Break 🧘 (🥟+3)", callback=self.take_break),
            rumps.separator,
            self.notifications_toggle,
            self.social_toggle,
            rumps.MenuItem("Reset Day", callback=self.reset),
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]
        
        # Initial update
        self.update_all_menu_items()
    
    @rumps.clicked("📊 View Live Leaderboard")
    def show_leaderboard(self, sender):
        """Show current live leaderboard"""
        try:
            friends_data = self.get_friends_data()
            
            # Add yourself to the data
            all_users = friends_data + [{
                'username': self.username,
                'session_dumplings': self.dumpling_earning_session,
                'total_dumplings_earned': self.total_dumplings_earned
            }]
            
            if len(all_users) > 1:
                # Sort by session dumplings
                sorted_users = sorted(all_users, key=lambda x: x.get('session_dumplings', 0), reverse=True)
                
                my_rank = next((i+1 for i, user in enumerate(sorted_users) if user['username'] == self.username), len(all_users))
                
                # Show top 3
                top_3 = sorted_users[:3]
                leaderboard = "\\n".join([
                    f"#{i+1} {user['username']}: 🥟 {user.get('session_dumplings', 0):.1f}"
                    for i, user in enumerate(top_3)
                ])
                
                db_note = " (Real-time via Supabase!)" if self.use_supabase else " (Demo mode)"
                
                self.send_native_notification(
                    "🏆 Live Leaderboard",
                    f"You're #{my_rank} of {len(all_users)} players{db_note}",
                    leaderboard
                )
            else:
                self.send_native_notification(
                    "🏆 Leaderboard",
                    "You're the only player online!",
                    f"Share your ID ({self.user_id}) to invite friends!"
                )
                
        except Exception as e:
            print(f"Error showing leaderboard: {e}")
            self.send_native_notification(
                "❌ Leaderboard Error",
                "Could not fetch live data",
                "Check your internet connection or Supabase setup"
            )
    
    @rumps.clicked("👥 Setup Multiplayer")
    def setup_multiplayer(self, sender):
        """Show multiplayer setup instructions"""
        if self.use_supabase:
            self.send_native_notification(
                "✅ Multiplayer Ready!",
                "Connected to Supabase database",
                f"Share your ID ({self.user_id}) with friends to compete!"
            )
        else:
            self.send_native_notification(
                "🗄️ Supabase Setup Required",
                "Replace SUPABASE_URL and SUPABASE_KEY in code",
                "Then set use_supabase = True for real multiplayer!"
            )
    
    @rumps.clicked("🆔 Share User ID")
    def share_user_id(self, sender):
        """Share user ID for adding friends"""
        # Copy to clipboard
        try:
            import subprocess
            subprocess.run(['pbcopy'], input=self.user_id.encode(), check=True)
            clipboard_note = " (Copied to clipboard!)"
        except:
            clipboard_note = ""
        
        self.send_native_notification(
            "🆔 Your Dino ID",
            f"{self.user_id}{clipboard_note}",
            f"Share this ID with friends so they can compete with {self.username}!"
        )
    
    @rumps.clicked("🔔 Notifications: ON")
    def toggle_notifications(self, sender):
        """Toggle general notifications"""
        self.notifications_enabled = not self.notifications_enabled
        status = "ON" if self.notifications_enabled else "OFF"
        self.notifications_toggle.title = f"🔔 Notifications: {status}"
    
    @rumps.clicked("👥 Social Alerts: ON")
    def toggle_social_notifications(self, sender):
        """Toggle social pressure notifications"""
        self.social_notifications_enabled = not self.social_notifications_enabled
        status = "ON" if self.social_notifications_enabled else "OFF"
        self.social_toggle.title = f"👥 Social Alerts: {status}"
        
        if self.social_notifications_enabled:
            self.send_native_notification("👥 Social Competition ON", 
                                        "Real-time friend updates enabled!", 
                                        "You'll get notifications when friends outperform you!")
    
    # Core functionality methods with enhanced website tracking
    
    def start_monitoring(self):
        """Start monitoring activity with website tracking"""
        def monitor():
            while True:
                try:
                    self.detect_current_activity()
                    self.update_all_menu_items()
                except Exception as e:
                    print(f"Monitor error: {e}")
                time.sleep(5)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def detect_current_activity(self):
        """Detect what the user is currently doing"""
        try:
            # Get the current active application
            active_app_script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
                return frontApp
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', active_app_script], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                app_name = result.stdout.strip().lower()
                
                # If it's Chrome, get the current URL
                if 'chrome' in app_name:
                    url, title = self.get_current_chrome_url()
                    if url:
                        self.handle_website_detection(url, title)
                        return
                
                # Handle other applications
                if any(app in app_name for app in ['code', 'xcode', 'vim', 'atom', 'sublime']):
                    self.current_state = 'coding'
                    self.current_website = None
                    self.current_website_category = None
                elif 'slack' in app_name:
                    self.current_state = 'working'
                    self.current_website = None
                    self.current_website_category = None
                elif any(app in app_name for app in ['figma', 'sketch', 'photoshop']):
                    self.current_state = 'designing'
                    self.current_website = None
                    self.current_website_category = None
                else:
                    self.current_state = 'idle'
                    self.current_website = None
                    self.current_website_category = None
            
        except Exception as e:
            print(f"Error detecting activity: {e}")
            self.current_state = 'idle'
    
    def get_current_chrome_url(self):
        """Get current Chrome tab URL and title"""
        try:
            chrome_script = '''
            tell application "Google Chrome"
                if (count of windows) = 0 then
                    return "No windows"
                end if
                
                set currentWindow to front window
                if (count of tabs of currentWindow) = 0 then
                    return "No tabs"
                end if
                
                set currentTab to active tab of currentWindow
                set currentURL to URL of currentTab
                set currentTitle to title of currentTab
                return currentURL & " ||| " & currentTitle
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', chrome_script], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and " ||| " in result.stdout:
                parts = result.stdout.strip().split(" ||| ")
                return parts[0], parts[1] if len(parts) > 1 else ""
            
        except Exception as e:
            print(f"Error getting Chrome URL: {e}")
            
        return None, None
    
    def handle_website_detection(self, url, title):
        """Handle when a new website is detected"""
        try:
            # Categorize the website
            category = self.categorize_website(url, title)
            
            # If it's a new website, update tracking
            if url != self.current_website:
                old_url = self.current_website
                self.current_website = url
                self.current_website_category = category
                
                # Determine state based on category
                if category == 'other':
                    # Prompt user to categorize unknown website
                    self.prompt_website_categorization(url, title)
                    self.current_state = 'browsing_other'
                else:
                    self.current_state = f'browsing_{category}'
                
                # Send website change notification if URL changed
                if old_url != url:
                    self.send_website_change_notification(url, category)
                    
        except Exception as e:
            print(f"Error handling website detection: {e}")
    
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
            
            # Check custom user categories first
            for domain_pattern, category in self.custom_website_categories.items():
                if domain_pattern in domain:
                    return category
            
            # Check each standard category
            for category, config in self.website_categories.items():
                # Check domains
                for domain_pattern in config['domains']:
                    if domain_pattern in domain:
                        return category
                
                # Check keywords in URL/title
                for keyword in config.get('keywords', []):
                    if keyword in full_url:
                        return category
            
            # Special cases
            if any(term in full_url for term in ['login', 'auth', 'signin']):
                return 'work'
            
            if any(term in domain for term in ['gov', 'edu']):
                return 'productive'
                
        except Exception as e:
            print(f"Error categorizing website: {e}")
            
        return 'other'
    
    def prompt_website_categorization(self, url, title):
        """Prompt user to categorize an unknown website"""
        try:
            domain = urlparse(url).netloc.replace('www.', '')
            
            # Create categorization options
            categories = list(self.website_categories.keys())
            category_options = []
            
            for cat in categories:
                emoji = self.website_categories[cat]['emoji']
                rate = self.website_categories[cat]['dumpling_rate']
                rate_text = f"+{rate}/min" if rate > 0 else f"{rate}/min" if rate < 0 else "0/min"
                category_options.append(f"{emoji} {cat.title()} ({rate_text})")
            
            # Send notification asking user to categorize
            self.send_native_notification(
                "❓ Unknown Website Detected",
                f"How should I categorize {domain}?",
                f"Visit the menu to categorize this site and earn appropriate dumplings!"
            )
            
            # Add to menu for categorization
            self.add_categorization_menu_item(url, domain)
            
        except Exception as e:
            print(f"Error prompting categorization: {e}")
    
    def add_categorization_menu_item(self, url, domain):
        """Add temporary menu item for website categorization"""
        try:
            # Store the uncategorized website
            if not hasattr(self, 'pending_categorizations'):
                self.pending_categorizations = {}
            
            self.pending_categorizations[domain] = url
            
            # Add categorization menu items (will be handled in menu creation)
            self.update_categorization_menu()
            
        except Exception as e:
            print(f"Error adding categorization menu: {e}")
    
    def categorize_pending_website(self, domain, category):
        """Categorize a pending website"""
        try:
            # Add to custom categories
            self.custom_website_categories[domain] = category
            self.save_custom_categories()
            
            # Remove from pending
            if hasattr(self, 'pending_categorizations') and domain in self.pending_categorizations:
                del self.pending_categorizations[domain]
            
            # Update current categorization if this is the current site
            if self.current_website and domain in self.current_website:
                self.current_website_category = category
                self.current_state = f'browsing_{category}'
            
            # Send confirmation
            emoji = self.website_categories[category]['emoji']
            rate = self.website_categories[category]['dumpling_rate']
            rate_text = f"+{rate}/min" if rate > 0 else f"{rate}/min" if rate < 0 else "0/min"
            
            self.send_native_notification(
                f"{emoji} Website Categorized!",
                f"{domain} → {category.title()}",
                f"Earning {rate_text} dumplings while browsing this site!"
            )
            
            # Update menu
            self.update_categorization_menu()
            self.update_all_menu_items()
            
        except Exception as e:
            print(f"Error categorizing website: {e}")
    
    def send_website_change_notification(self, url, category):
        """Send notification when website changes"""
        try:
            domain = urlparse(url).netloc.replace('www.', '')
            emoji = self.website_categories.get(category, {}).get('emoji', '🌐')
            rate = self.website_categories.get(category, {}).get('dumpling_rate', 0)
            
            if category == 'other':
                subtitle = f"❓ Unknown site: {domain}"
                message = "Click menu to categorize and earn dumplings!"
            elif rate > 0:
                subtitle = f"🥟 +{rate}/min | {domain}"
                message = f"Great choice! Earning dumplings on {category} sites."
            elif rate < 0:
                subtitle = f"🥟 {rate}/min | {domain}"
                message = f"Distraction detected! {category.title()} sites cost dumplings."
            else:
                subtitle = f"🌐 Neutral | {domain}"
                message = f"Browsing {category} sites (no dumpling change)"
            
            self.send_native_notification(
                f"{emoji} Website Change",
                subtitle,
                message,
                sound=False
            )
            
        except Exception as e:
            print(f"Error sending website notification: {e}")
    
    def load_custom_categories(self):
        """Load user's custom website categories"""
        try:
            custom_file = os.path.expanduser("~/.dino_tamagotchi/custom_categories.json")
            if os.path.exists(custom_file):
                with open(custom_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading custom categories: {e}")
        return {}
    
    def save_custom_categories(self):
        """Save user's custom website categories"""
        try:
            save_dir = os.path.expanduser("~/.dino_tamagotchi")
            os.makedirs(save_dir, exist_ok=True)
            
            with open(os.path.join(save_dir, "custom_categories.json"), "w") as f:
                json.dump(self.custom_website_categories, f)
        except Exception as e:
            print(f"Error saving custom categories: {e}")
    
    def update_categorization_menu(self):
        """Update menu with pending categorizations"""
        # Force menu update to show/hide categorization items
        self.update_all_menu_items()
    
    def start_dumpling_monitoring(self):
        """Monitor and award dumplings"""
        def dumpling_monitor():
            while True:
                try:
                    self.calculate_dumpling_earnings()
                except Exception as e:
                    print(f"Dumpling monitor error: {e}")
                time.sleep(60)
        
        threading.Thread(target=dumpling_monitor, daemon=True).start()
    
    def calculate_dumpling_earnings(self):
        """Calculate and award dumplings based on current activity"""
        now = datetime.now()
        time_since_last = (now - self.last_dumpling_time).total_seconds() / 60.0
        
        if time_since_last < 1:
            return
        
        dumplings_earned = 0
        
        # Track time spent
        if self.current_state in self.time_spent:
            self.time_spent[self.current_state] += time_since_last * 60  # Convert to seconds
        
        # Calculate earnings based on activity
        if self.current_state == 'coding':
            dumplings_earned = 2.0 * time_since_last
        elif self.current_state == 'working':
            dumplings_earned = 0.8 * time_since_last
        elif self.current_state == 'designing':
            dumplings_earned = 1.5 * time_since_last
        elif self.current_state.startswith('browsing_'):
            # Use website category rates
            if self.current_website_category and self.current_website_category in self.website_categories:
                rate = self.website_categories[self.current_website_category]['dumpling_rate']
                dumplings_earned = rate * time_since_last
            elif self.current_website_category == 'other':
                # Neutral rate for uncategorized sites
                dumplings_earned = 0
        
        if dumplings_earned != 0:
            self.award_dumplings(abs(dumplings_earned) if dumplings_earned > 0 else dumplings_earned, self.current_state)
        
        self.last_dumpling_time = now
    
    def award_dumplings(self, amount, reason):
        """Award dumplings"""
        if amount > 0:
            self.dumplings += amount
            self.total_dumplings_earned += amount
            self.dumpling_earning_session += amount
            
            if amount >= 3:
                self.send_native_notification(
                    f"🥟 +{amount:.1f} Dumplings!",
                    f"Total: 🥟 {self.dumplings:.1f}",
                    f"Great {reason}! Your friends will see this progress!"
                )
        else:
            # Losing dumplings
            self.dumplings = max(0, self.dumplings + amount)  # amount is negative
        
        print(f"🥟 {'+' if amount > 0 else ''}{amount:.1f} dumplings! Total: {self.dumplings:.1f}")
    
    def update_all_menu_items(self):
        """Update all menu items"""
        try:
            # Update basic info
            self.status_item.title = f"Status: {self.current_state.replace('_', ' ').title()}"
            
            db_status = "🗄️ Supabase" if self.use_supabase else "🗄️ Demo"
            self.user_info_item.title = f"👤 {self.username} | {db_status}"
            self.dumplings_item.title = f"🥟 Dumplings: {self.dumplings:.1f}"
            self.session_earnings_item.title = f"📈 Session: +{self.dumpling_earning_session:.1f}"
            
            # Update ranking
            friends_data = self.get_friends_data()
            if friends_data:
                self.ranking_item.title = f"🏆 Competing with {len(friends_data)} friends"
            else:
                self.ranking_item.title = "🏆 Add friends to compete!"
            
            self.health_item.title = f"🦕 Health: {self.health}%"
            self.happiness_item.title = f"😊 Happiness: {self.happiness}%"
            self.energy_item.title = f"⚡ Energy: {self.energy}%"
            
            # Update website tracking
            if self.current_website:
                try:
                    domain = urlparse(self.current_website).netloc.replace('www.', '')
                    category_emoji = self.website_categories.get(self.current_website_category, {}).get('emoji', '🌐')
                    
                    if self.current_website_category == 'other':
                        self.website_item.title = f"❓ {domain} (Click to categorize!)"
                    else:
                        rate = self.website_categories.get(self.current_website_category, {}).get('dumpling_rate', 0)
                        rate_display = f" (+{rate}/min)" if rate > 0 else f" ({rate}/min)" if rate < 0 else ""
                        self.website_item.title = f"{category_emoji} {domain}{rate_display}"
                except:
                    self.website_item.title = "🌐 Website: Unknown"
            else:
                self.website_item.title = "🌐 Website: None"
            
            session_time = self.format_time((datetime.now() - self.session_start).total_seconds())
            self.session_item.title = f"⏰ Session: {session_time}"
            
            self.coding_item.title = f"  💻 Coding: {self.format_time(self.time_spent.get('coding', 0))} (🥟+2.0/min)"
            self.working_item.title = f"  💼 Working: {self.format_time(self.time_spent.get('working', 0))} (🥟+0.8/min)"
            self.productive_item.title = f"  📖 Learning: {self.format_time(self.time_spent.get('browsing_productive', 0))} (🥟+1.0/min)"
            self.social_item.title = f"  📱 Social: {self.format_time(self.time_spent.get('browsing_social', 0))} (🥟-0.2/min)"
            self.news_item.title = f"  📰 News: {self.format_time(self.time_spent.get('browsing_news', 0))} (🥟-0.1/min)"
            self.entertainment_item.title = f"  🍿 Entertainment: {self.format_time(self.time_spent.get('browsing_entertainment', 0))} (🥟-0.3/min)"
            self.shopping_item.title = f"  🛒 Shopping: {self.format_time(self.time_spent.get('browsing_shopping', 0))} (🥟-0.15/min)"
            
            # Update dynamic categorization menu items
            self.update_dynamic_menu_items()
            
            # Update menu bar icon
            multiplayer_indicator = "👥" if len(friends_data) > 0 else ""
            dumpling_indicator = "💰" if self.dumplings >= 100 else "🥟" if self.dumplings >= 50 else ""
            
            self.title = f"{self.states[self.current_state]}{dumpling_indicator}{multiplayer_indicator}"
            
        except Exception as e:
            print(f"Error updating menu: {e}")
    
    def update_dynamic_menu_items(self):
        """Update menu with categorization options for pending sites"""
        try:
            # Remove old categorization items
            items_to_remove = []
            for item in self.menu:
                if hasattr(item, 'title') and item.title.startswith("❓ Categorize"):
                    items_to_remove.append(item)
            
            for item in items_to_remove:
                self.menu.remove(item)
            
            # Add categorization items for pending sites
            if hasattr(self, 'pending_categorizations') and self.pending_categorizations:
                # Find the position to insert (after website_item)
                insert_pos = None
                for i, item in enumerate(self.menu):
                    if item == self.website_item:
                        insert_pos = i + 1
                        break
                
                if insert_pos is not None:
                    # Add separator if needed
                    if self.menu[insert_pos] != rumps.separator:
                        self.menu.insert(insert_pos, rumps.separator)
                        insert_pos += 1
                    
                    # Add categorization header
                    header_item = rumps.MenuItem("❓ Categorize Unknown Sites:")
                    self.menu.insert(insert_pos, header_item)
                    insert_pos += 1
                    
                    # Add categorization options for each pending site
                    for domain in self.pending_categorizations:
                        for category in self.website_categories:
                            emoji = self.website_categories[category]['emoji']
                            rate = self.website_categories[category]['dumpling_rate']
                            rate_text = f"+{rate}" if rate > 0 else str(rate) if rate < 0 else "0"
                            
                            item_title = f"  {emoji} {domain} → {category.title()} ({rate_text}/min)"
                            callback_func = self.create_categorization_callback(domain, category)
                            cat_item = rumps.MenuItem(item_title, callback=callback_func)
                            self.menu.insert(insert_pos, cat_item)
                            insert_pos += 1
                    
                    # Add separator after categorization items
                    self.menu.insert(insert_pos, rumps.separator)
                    
        except Exception as e:
            print(f"Error updating dynamic menu items: {e}")
    
    def create_categorization_callback(self, domain, category):
        """Create a callback function for website categorization"""
        def callback(sender):
            self.categorize_pending_website(domain, category)
        return callback
    
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
    
    # Action methods
    
    @rumps.clicked("Feed 🍖 (🥟-5)")
    def feed(self, sender):
        cost = 5
        if self.dumplings >= cost:
            self.dumplings -= cost
            self.happiness = min(100, self.happiness + 30)
            self.health = min(100, self.health + 20)
            self.send_native_notification("🍖 Dino Fed!", f"🥟 -{cost} | Health +20!", "Your dino is thriving!")
        else:
            self.send_native_notification("🍖 Not Enough Dumplings!", f"Need 🥟 {cost} (have {self.dumplings:.1f})", "Earn more through productivity!")
    
    @rumps.clicked("Pet 🫳 (Free!)")
    def pet(self, sender):
        self.happiness = min(100, self.happiness + 15)
        self.health = min(100, self.health + 5)
        self.send_native_notification("✨ Dino Petted!", "Free happiness boost!", "Your dino loves the attention!")
    
    @rumps.clicked("Take Break 🧘 (🥟+3)")
    def take_break(self, sender):
        bonus = 3
        self.award_dumplings(bonus, "taking a break")
        self.health = min(100, self.health + 15)
        self.energy = min(100, self.energy + 20)
        self.send_native_notification("🧘 Break Taken!", f"🥟 +{bonus} for self-care!", "Smart breaks earn dumplings!")
    
    @rumps.clicked("Reset Day")
    def reset(self, sender):
        session_dumplings = self.dumpling_earning_session
        
        self.current_state = 'idle'
        self.happiness = 50
        self.energy = 50
        self.health = 100
        self.dumpling_earning_session = 0
        self.session_start = datetime.now()
        self.time_spent = {key: 0 for key in self.time_spent}
        
        self.send_native_notification("🔄 Day Reset!", f"🥟 Earned {session_dumplings:.1f} today", "Fresh start with live multiplayer!")
    
    # Data persistence
    
    def save_data(self):
        """Save local data"""
        try:
            data = {
                'happiness': self.happiness,
                'energy': self.energy, 
                'health': self.health,
                'dumplings': self.dumplings,
                'total_dumplings_earned': self.total_dumplings_earned,
                'dumpling_earning_session': self.dumpling_earning_session,
                'time_spent': self.time_spent,
                'session_start': self.session_start.isoformat(),
                'notifications_enabled': self.notifications_enabled,
                'social_notifications_enabled': self.social_notifications_enabled
            }
            
            save_dir = os.path.expanduser("~/.dino_tamagotchi")
            os.makedirs(save_dir, exist_ok=True)
            
            with open(os.path.join(save_dir, "supabase_dino_data.json"), "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        """Load local data"""
        try:
            save_dir = os.path.expanduser("~/.dino_tamagotchi")
            data_file = os.path.join(save_dir, "supabase_dino_data.json")
            
            if os.path.exists(data_file):
                with open(data_file, "r") as f:
                    data = json.load(f)
                
                self.happiness = data.get('happiness', 50)
                self.energy = data.get('energy', 50)
                self.health = data.get('health', 100)
                self.dumplings = data.get('dumplings', 0)
                self.total_dumplings_earned = data.get('total_dumplings_earned', 0)
                self.dumpling_earning_session = data.get('dumpling_earning_session', 0)
                self.time_spent = data.get('time_spent', self.time_spent)
                self.notifications_enabled = data.get('notifications_enabled', True)
                self.social_notifications_enabled = data.get('social_notifications_enabled', True)
                
                try:
                    saved_start = datetime.fromisoformat(data.get('session_start', datetime.now().isoformat()))
                    if (datetime.now() - saved_start).days > 0:
                        self.dumpling_earning_session = 0
                        self.session_start = datetime.now()
                    else:
                        self.session_start = saved_start
                except:
                    self.session_start = datetime.now()
                    
        except Exception as e:
            print(f"Error loading data: {e}")

if __name__ == "__main__":
    print("🦕 Starting Supabase-Powered Multiplayer Dino...")
    SupabaseDino().run()