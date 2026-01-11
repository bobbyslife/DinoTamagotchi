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
import requests
from urllib.parse import urlparse
import uuid

class MultiplayerDino(rumps.App):
    def __init__(self):
        super(MultiplayerDino, self).__init__("🦕", quit_button=None)
        
        # User identification
        self.user_id = self.load_or_create_user_id()
        self.username = self.load_or_create_username()
        
        # Simple HTTP backend URL (you'll need to replace this)
        self.backend_url = "https://dino-tamagotchi-default-rtdb.firebaseio.com"  # Firebase example
        # For now, we'll use a simple file-based system that could easily become a REST API
        
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
        
        # Website categories (keeping from previous version)
        self.website_categories = {
            'productive': {
                'domains': ['github.com', 'stackoverflow.com', 'docs.', 'developer.', 'learn.', 'coursera.com', 'udemy.com', 'codecademy.com', 'freecodecamp.org'],
                'keywords': ['documentation', 'tutorial', 'learn', 'course', 'guide'],
                'emoji': '📖',
                'health_modifier': 1.0,
                'happiness_modifier': 1.5,
                'dumpling_rate': 1.0
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
                'dumpling_rate': -0.2
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
        
        # Dumpling system
        self.dumplings = 0
        self.total_dumplings_earned = 0
        self.dumpling_earning_session = 0
        self.last_dumpling_time = datetime.now()
        
        # Multiplayer stats
        self.friends_list = []
        self.pending_challenges = []
        self.active_challenges = []
        self.daily_ranking = 0
        
        # Enhanced time tracking
        self.session_start = datetime.now()
        self.state_start_time = datetime.now()
        self.website_start_time = datetime.now()
        self.productive_time_today = 0
        
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
        self.last_social_update = None
        self.last_leaderboard_check = None
        
        # Notification settings
        self.notifications_enabled = True
        self.social_notifications_enabled = True
        
        # Load saved data
        self.load_data()
        
        # Create menu
        self.create_static_menu()
        
        # Send welcome notification
        self.send_native_notification("🦕 Multiplayer Dino Started!", 
                                    f"Welcome back, {self.username}! 🥟 {self.dumplings} dumplings",
                                    "Add friends to compete and get motivated!")
        
        # Start monitoring
        self.start_monitoring()
        self.start_health_monitoring()
        self.start_dumpling_monitoring()
        self.start_social_monitoring()
        self.start_notification_scheduler()
        
        print(f"🦕 Multiplayer Dino Started!")
        print(f"👤 User: {self.username} (ID: {self.user_id})")
        print(f"🥟 Dumplings: {self.dumplings}")
        print(f"👥 Friends: {len(self.friends_list)}")
    
    def load_or_create_user_id(self):
        """Load existing user ID or create new one"""
        user_file = os.path.expanduser("~/.dino_tamagotchi/user_id.txt")
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                return f.read().strip()
        else:
            # Create new user ID
            new_id = str(uuid.uuid4())[:8]
            os.makedirs(os.path.dirname(user_file), exist_ok=True)
            with open(user_file, 'w') as f:
                f.write(new_id)
            return new_id
    
    def load_or_create_username(self):
        """Load existing username or prompt for new one"""
        username_file = os.path.expanduser("~/.dino_tamagotchi/username.txt")
        if os.path.exists(username_file):
            with open(username_file, 'r') as f:
                return f.read().strip()
        else:
            # For now, use a default. In real implementation, you'd prompt the user
            import getpass
            default_username = getpass.getuser()
            username = f"DinoUser_{self.user_id}"
            
            os.makedirs(os.path.dirname(username_file), exist_ok=True)
            with open(username_file, 'w') as f:
                f.write(username)
            return username
    
    def start_social_monitoring(self):
        """Monitor friends' activities and send social pressure notifications"""
        def social_monitor():
            while True:
                try:
                    if self.social_notifications_enabled:
                        self.check_friends_activity()
                        self.send_competitive_updates()
                        self.check_daily_rankings()
                except Exception as e:
                    print(f"Social monitor error: {e}")
                time.sleep(120)  # Check every 2 minutes
        
        threading.Thread(target=social_monitor, daemon=True).start()
    
    def sync_user_data(self):
        """Sync current user data to backend (simplified for demo)"""
        try:
            user_data = {
                'user_id': self.user_id,
                'username': self.username,
                'dumplings': self.dumplings,
                'total_dumplings_earned': self.total_dumplings_earned,
                'health': self.health,
                'happiness': self.happiness,
                'energy': self.energy,
                'productive_time_today': self.productive_time_today,
                'current_state': self.current_state,
                'last_activity': datetime.now().isoformat(),
                'daily_stats': {
                    'coding_time': self.time_spent.get('coding', 0),
                    'productive_browsing': self.time_spent.get('browsing_productive', 0),
                    'social_media_time': self.time_spent.get('browsing_social', 0),
                    'session_dumplings': self.dumpling_earning_session
                }
            }
            
            # In a real implementation, this would be an HTTP POST to your backend
            # For now, we'll save to a shared file that simulates a database
            shared_dir = os.path.expanduser("~/Desktop/DinoTamagotchi/shared_data")
            os.makedirs(shared_dir, exist_ok=True)
            
            with open(f"{shared_dir}/{self.user_id}.json", 'w') as f:
                json.dump(user_data, f)
                
        except Exception as e:
            print(f"Error syncing user data: {e}")
    
    def get_friends_data(self):
        """Get friends' current data from backend"""
        try:
            friends_data = []
            shared_dir = os.path.expanduser("~/Desktop/DinoTamagotchi/shared_data")
            
            if not os.path.exists(shared_dir):
                return friends_data
            
            # Read all user files (simulating database query)
            for filename in os.listdir(shared_dir):
                if filename.endswith('.json') and filename != f"{self.user_id}.json":
                    try:
                        with open(f"{shared_dir}/{filename}", 'r') as f:
                            friend_data = json.load(f)
                            
                            # Only include if they're in our friends list or for demo, include all
                            if not self.friends_list or friend_data['user_id'] in self.friends_list:
                                friends_data.append(friend_data)
                    except Exception as e:
                        print(f"Error reading friend data {filename}: {e}")
            
            return friends_data
            
        except Exception as e:
            print(f"Error getting friends data: {e}")
            return []
    
    def check_friends_activity(self):
        """Check what friends are doing and send social pressure notifications"""
        try:
            friends_data = self.get_friends_data()
            
            if not friends_data:
                return
            
            now = datetime.now()
            
            # Don't spam notifications
            if (self.last_social_update and 
                now - self.last_social_update < timedelta(minutes=5)):
                return
            
            for friend in friends_data:
                try:
                    friend_last_activity = datetime.fromisoformat(friend['last_activity'])
                    
                    # Only notify about recent activity (last 10 minutes)
                    if now - friend_last_activity < timedelta(minutes=10):
                        
                        # Friend is coding and earning more than you
                        if (friend['current_state'] == 'coding' and 
                            friend['daily_stats']['session_dumplings'] > self.dumpling_earning_session):
                            
                            diff = friend['daily_stats']['session_dumplings'] - self.dumpling_earning_session
                            self.send_native_notification(
                                "🏃‍♂️ You're Falling Behind!",
                                f"{friend['username']} is ahead by 🥟 {diff:.1f} dumplings",
                                f"They're coding right now! Time to catch up! 💻"
                            )
                            self.last_social_update = now
                            break
                        
                        # Friend achieved a milestone
                        elif friend['total_dumplings_earned'] % 50 < 1:  # Just hit a 50 dumpling milestone
                            self.send_native_notification(
                                "🏆 Friend Milestone!",
                                f"{friend['username']} just earned their {int(friend['total_dumplings_earned'])}th dumpling!",
                                "Can you beat their productivity streak?"
                            )
                            self.last_social_update = now
                            break
                        
                        # Friend has been very productive today
                        elif friend['daily_stats']['coding_time'] > 3600:  # 1+ hours coding
                            self.send_native_notification(
                                "🔥 Friend on Fire!",
                                f"{friend['username']} coded for {self.format_time(friend['daily_stats']['coding_time'])} today!",
                                "Think you can code longer? Show them what you've got!"
                            )
                            self.last_social_update = now
                            break
                            
                except Exception as e:
                    print(f"Error processing friend {friend.get('username', 'Unknown')}: {e}")
                    
        except Exception as e:
            print(f"Error checking friends activity: {e}")
    
    def send_competitive_updates(self):
        """Send competitive pressure notifications"""
        try:
            friends_data = self.get_friends_data()
            
            if not friends_data:
                return
            
            # Calculate your rank for today
            all_users = friends_data + [{
                'username': self.username,
                'daily_stats': {
                    'session_dumplings': self.dumpling_earning_session,
                    'coding_time': self.time_spent.get('coding', 0)
                }
            }]
            
            # Sort by session dumplings
            sorted_by_dumplings = sorted(all_users, key=lambda x: x['daily_stats']['session_dumplings'], reverse=True)
            my_rank = next((i+1 for i, user in enumerate(sorted_by_dumplings) if user['username'] == self.username), len(all_users))
            
            # Send ranking notification occasionally
            if random.random() < 0.3:  # 30% chance
                if my_rank == 1:
                    self.send_native_notification(
                        "👑 You're Leading!",
                        f"🥟 #{my_rank} out of {len(all_users)} friends today",
                        "Keep it up! Your friends are trying to catch up!"
                    )
                else:
                    leader = sorted_by_dumplings[0]
                    gap = leader['daily_stats']['session_dumplings'] - self.dumpling_earning_session
                    self.send_native_notification(
                        f"📊 Daily Ranking: #{my_rank}/{len(all_users)}",
                        f"{leader['username']} leads by 🥟 {gap:.1f} dumplings",
                        "Time to step up your productivity game!"
                    )
                    
        except Exception as e:
            print(f"Error sending competitive updates: {e}")
    
    def check_daily_rankings(self):
        """Check and update daily rankings"""
        try:
            friends_data = self.get_friends_data()
            
            if not friends_data:
                return
            
            now = datetime.now()
            
            # Only check rankings once every 30 minutes
            if (self.last_leaderboard_check and 
                now - self.last_leaderboard_check < timedelta(minutes=30)):
                return
            
            # End of day ranking (5 PM)
            if now.hour == 17 and now.minute < 5:
                all_users = friends_data + [{
                    'username': self.username,
                    'daily_stats': {'session_dumplings': self.dumpling_earning_session}
                }]
                
                sorted_users = sorted(all_users, key=lambda x: x['daily_stats']['session_dumplings'], reverse=True)
                my_rank = next((i+1 for i, user in enumerate(sorted_users) if user['username'] == self.username), len(all_users))
                
                if my_rank == 1:
                    self.send_native_notification(
                        "🥇 Daily Champion!",
                        f"You won today with 🥟 {self.dumpling_earning_session:.1f} dumplings!",
                        "Amazing productivity! Your friends are impressed! 🎉"
                    )
                elif my_rank <= 3:
                    self.send_native_notification(
                        f"🏅 Daily Top 3!",
                        f"#{my_rank} place with 🥟 {self.dumpling_earning_session:.1f} dumplings",
                        "Great work today! Almost at the top!"
                    )
                else:
                    winner = sorted_users[0]
                    self.send_native_notification(
                        f"📊 Daily Results: #{my_rank}/{len(all_users)}",
                        f"{winner['username']} won with 🥟 {winner['daily_stats']['session_dumplings']:.1f}",
                        "Tomorrow's a new day to climb the leaderboard!"
                    )
                
                self.last_leaderboard_check = now
                
        except Exception as e:
            print(f"Error checking daily rankings: {e}")
    
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
        """Create static menu items with multiplayer features"""
        self.status_item = rumps.MenuItem("Status: Just chilling")
        self.website_item = rumps.MenuItem("🌐 Website: None")
        
        # User info
        self.user_info_item = rumps.MenuItem(f"👤 {self.username} (ID: {self.user_id})")
        self.dumplings_item = rumps.MenuItem(f"🥟 Dumplings: {self.dumplings}")
        self.session_earnings_item = rumps.MenuItem(f"📈 Session Earned: +{self.dumpling_earning_session}")
        self.ranking_item = rumps.MenuItem("🏆 Daily Ranking: Loading...")
        
        self.health_item = rumps.MenuItem(f"🦕 Health: ❤️❤️❤️❤️❤️ {self.health}%")
        self.happiness_item = rumps.MenuItem(f"😊 Happiness: 😊😊😊😊😊 {self.happiness}%")
        self.energy_item = rumps.MenuItem(f"⚡ Energy: ⚡⚡⚡⚡⚡ {self.energy}%")
        
        self.session_item = rumps.MenuItem("⏰ Session: 0m")
        
        # Time tracking
        self.productive_item = rumps.MenuItem("  📖 Productive Sites: 0m")
        self.work_item = rumps.MenuItem("  💼 Work Sites: 0m") 
        self.social_item = rumps.MenuItem("  📱 Social Media: 0m")
        self.coding_item = rumps.MenuItem("  💻 Coding: 0m")
        self.designing_item = rumps.MenuItem("  🎨 Designing: 0m")
        
        # Multiplayer controls
        self.notifications_toggle = rumps.MenuItem("🔔 Notifications: ON", callback=self.toggle_notifications)
        self.social_toggle = rumps.MenuItem("👥 Social Alerts: ON", callback=self.toggle_social_notifications)
        
        # Set the menu
        self.menu = [
            self.status_item,
            self.website_item,
            rumps.separator,
            self.user_info_item,
            self.dumplings_item,
            self.session_earnings_item,
            self.ranking_item,
            rumps.separator,
            rumps.MenuItem("👥 Multiplayer Features:"),
            rumps.MenuItem("📊 View Leaderboard", callback=self.show_leaderboard),
            rumps.MenuItem("🤝 Add Friend (Coming Soon)", callback=self.show_add_friend),
            rumps.MenuItem("⚔️ Challenge Friend (Coming Soon)", callback=self.show_challenges),
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
            self.coding_item,
            self.designing_item,
            rumps.separator,
            rumps.MenuItem("Feed 🍖", callback=self.feed),
            rumps.MenuItem("Pet 🫳", callback=self.pet),
            rumps.MenuItem("Take Break 🧘", callback=self.take_break),
            rumps.separator,
            self.notifications_toggle,
            self.social_toggle,
            rumps.MenuItem("Reset Day", callback=self.reset),
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]
        
        # Initial update
        self.update_all_menu_items()
    
    @rumps.clicked("📊 View Leaderboard")
    def show_leaderboard(self, sender):
        """Show current leaderboard"""
        try:
            friends_data = self.get_friends_data()
            
            all_users = friends_data + [{
                'username': self.username,
                'daily_stats': {'session_dumplings': self.dumpling_earning_session}
            }]
            
            sorted_users = sorted(all_users, key=lambda x: x['daily_stats']['session_dumplings'], reverse=True)
            
            if len(sorted_users) > 1:
                top_3 = sorted_users[:3]
                leaderboard = "\\n".join([
                    f"{i+1}. {user['username']}: 🥟 {user['daily_stats']['session_dumplings']:.1f}"
                    for i, user in enumerate(top_3)
                ])
                
                my_rank = next((i+1 for i, user in enumerate(sorted_users) if user['username'] == self.username), len(all_users))
                
                self.send_native_notification(
                    "🏆 Today's Leaderboard",
                    f"You're #{my_rank} out of {len(all_users)}",
                    leaderboard
                )
            else:
                self.send_native_notification(
                    "🏆 Leaderboard",
                    "You're the only player!",
                    "Add friends to compete! Share your ID: " + self.user_id
                )
                
        except Exception as e:
            print(f"Error showing leaderboard: {e}")
    
    @rumps.clicked("🤝 Add Friend (Coming Soon)")
    def show_add_friend(self, sender):
        """Show add friend feature preview"""
        self.send_native_notification(
            "🤝 Add Friends (Coming Soon)",
            f"Your ID: {self.user_id}",
            "Share this ID with friends so they can add you! Friend system launching soon."
        )
    
    @rumps.clicked("⚔️ Challenge Friend (Coming Soon)")
    def show_challenges(self, sender):
        """Show challenge system preview"""
        self.send_native_notification(
            "⚔️ Challenge System (Coming Soon)",
            "Battle friends in productivity duels!",
            "🥊 Code battles • ⏰ Focus challenges • 🥟 Dumpling races • 🏆 Weekly tournaments"
        )
    
    @rumps.clicked("🔔 Notifications: ON")
    def toggle_notifications(self, sender):
        """Toggle general notifications on/off"""
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
            self.send_native_notification("👥 Social Alerts Enabled", 
                                        "You'll get competitive notifications!", 
                                        "Friends' achievements will motivate your productivity!")
        else:
            self.send_native_notification("👥 Social Alerts Disabled", 
                                        "No more competitive pressure", 
                                        "Focus on your own productivity journey")
    
    # ... (keeping all the dumpling, website tracking, and core functionality from previous version)
    
    def start_dumpling_monitoring(self):
        """Monitor and award dumplings based on activity"""
        def dumpling_monitor():
            while True:
                try:
                    self.calculate_dumpling_earnings()
                    self.sync_user_data()  # Sync to backend every minute
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
        
        if self.current_state == 'coding':
            dumplings_earned = 2.0 * time_since_last
        elif self.current_state == 'working':
            dumplings_earned = 1.0 * time_since_last
        elif self.current_state == 'designing':
            dumplings_earned = 1.5 * time_since_last
        elif self.current_state.startswith('browsing_'):
            if self.current_website_category in self.website_categories:
                rate = self.website_categories[self.current_website_category]['dumpling_rate']
                dumplings_earned = rate * time_since_last
        
        if self.health > 80:
            dumplings_earned *= 1.2
        elif self.health < 30:
            dumplings_earned *= 0.5
        
        if dumplings_earned > 0:
            final_dumplings = round(dumplings_earned, 1)
            self.award_dumplings(final_dumplings, f"{self.get_current_status()}")
        elif dumplings_earned < 0:
            final_loss = round(abs(dumplings_earned), 1)
            self.lose_dumplings(final_loss, "Distracting activity")
        
        self.last_dumpling_time = now
    
    def award_dumplings(self, amount, reason):
        """Award dumplings and send notification"""
        self.dumplings += amount
        self.total_dumplings_earned += amount
        self.dumpling_earning_session += amount
        
        if amount >= 5:
            self.send_native_notification(
                f"🥟 +{amount} Dumplings Earned!",
                f"Total: 🥟 {self.dumplings} dumplings",
                f"Keep it up! Your friends will see this progress!"
            )
        
        print(f"🥟 +{amount} dumplings! Total: {self.dumplings} | Reason: {reason}")
    
    def lose_dumplings(self, amount, reason):
        """Lose dumplings for distracting activities"""
        if self.dumplings > 0:
            lost = min(amount, self.dumplings)
            self.dumplings -= lost
            print(f"🥟 -{lost} dumplings lost. Total: {self.dumplings} | Reason: {reason}")
    
    # ... (rest of the core functionality methods)
    
    def update_all_menu_items(self):
        """Update all menu items including multiplayer info"""
        try:
            # Update basic info
            status_text = self.get_current_status()
            self.status_item.title = f"Status: {status_text}"
            
            self.user_info_item.title = f"👤 {self.username} (ID: {self.user_id})"
            self.dumplings_item.title = f"🥟 Dumplings: {self.dumplings}"
            self.session_earnings_item.title = f"📈 Session Earned: +{self.dumpling_earning_session:.1f}"
            
            # Update ranking (simplified)
            friends_data = self.get_friends_data()
            if friends_data:
                self.ranking_item.title = f"🏆 Competing with {len(friends_data)} friends"
            else:
                self.ranking_item.title = "🏆 Add friends to compete!"
            
            # ... (rest of the menu updates from previous version)
            
            # Website info
            if self.current_website:
                try:
                    domain = urlparse(self.current_website).netloc.replace('www.', '')
                    category_emoji = self.website_categories.get(self.current_website_category, {}).get('emoji', '🌐')
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
            
            self.productive_item.title = f"  📖 Productive Sites: {self.format_time(self.time_spent.get('browsing_productive', 0))}"
            self.work_item.title = f"  💼 Work Sites: {self.format_time(self.time_spent.get('browsing_work', 0))}"
            self.social_item.title = f"  📱 Social Media: {self.format_time(self.time_spent.get('browsing_social', 0))}"
            self.coding_item.title = f"  💻 Coding: {self.format_time(self.time_spent.get('coding', 0))}"
            self.designing_item.title = f"  🎨 Designing: {self.format_time(self.time_spent.get('designing', 0))}"
            
            # Update menu bar icon
            health_indicator = ""
            if self.health < 30:
                health_indicator = "🚨"
            elif self.health < 60:
                health_indicator = "⚠️"
            
            dumpling_indicator = ""
            if self.dumplings >= 100:
                dumpling_indicator = "💰"
            elif self.dumplings >= 50:
                dumpling_indicator = "🥟"
            
            # Add multiplayer indicator
            multiplayer_indicator = ""
            if len(self.get_friends_data()) > 0:
                multiplayer_indicator = "👥"
            
            self.title = f"{self.states[self.current_state]}{health_indicator}{dumpling_indicator}{multiplayer_indicator}"
            
        except Exception as e:
            print(f"Error updating menu: {e}")
    
    # ... (keeping core methods like get_current_status, create_bar, format_time, etc.)
    
    def get_current_status(self):
        """Get descriptive status text"""
        return {
            'idle': "Just chilling",
            'working': "Working hard! 🥟+1.0/min",
            'coding': "Coding like a pro! 🥟+2.0/min",
            'designing': "Designing! 🥟+1.5/min",
            'browsing_productive': "Learning! 🥟+1.0/min",
            'browsing_work': "Work tasks 🥟+0.8/min",
            'browsing_social': "Social media 🥟-0.2/min",
            'browsing_news': "Reading news 🥟+0.1/min",
            'browsing_entertainment': "Entertainment 🥟-0.1/min",
            'browsing_shopping': "Shopping",
            'gaming': "Gaming time!",
            'sick': "Dino is sick! 🤒",
            'dead': "Dino died! 💀"
        }.get(self.current_state, "Unknown state")
    
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
    
    # ... (keeping all the core monitoring and website tracking methods)
    
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
        """Health monitoring with competitive elements"""
        def health_monitor():
            while True:
                try:
                    now = datetime.now()
                    
                    if self.health < 30 and (not self.last_health_warning or 
                       now - self.last_health_warning > timedelta(minutes=10)):
                        self.send_native_notification(
                            "🚨 Health Critical!",
                            f"🥟 Your friends might notice your low productivity!",
                            "Get back on track before you fall behind in rankings!"
                        )
                        self.last_health_warning = now
                        
                except Exception as e:
                    print(f"Health monitor error: {e}")
                
                time.sleep(30)
        
        threading.Thread(target=health_monitor, daemon=True).start()
    
    def start_notification_scheduler(self):
        """Enhanced notification scheduler with social pressure"""
        def notification_scheduler():
            while True:
                try:
                    now = datetime.now()
                    
                    # Daily goal with social pressure
                    if now.hour == 17 and now.minute < 5:
                        friends_data = self.get_friends_data()
                        if friends_data:
                            avg_friend_dumplings = sum(f['daily_stats']['session_dumplings'] for f in friends_data) / len(friends_data)
                            
                            if self.dumpling_earning_session < avg_friend_dumplings:
                                self.send_native_notification(
                                    "📊 Daily Summary",
                                    f"🥟 {avg_friend_dumplings:.1f} average vs your {self.dumpling_earning_session:.1f}",
                                    "Your friends outperformed you today. Tomorrow's a new chance!"
                                )
                            else:
                                self.send_native_notification(
                                    "🏆 Daily Success!",
                                    f"🥟 You beat the friend average by {self.dumpling_earning_session - avg_friend_dumplings:.1f}!",
                                    "Great productivity! Your friends are impressed! 🎉"
                                )
                        
                except Exception as e:
                    print(f"Notification scheduler error: {e}")
                
                time.sleep(300)
        
        threading.Thread(target=notification_scheduler, daemon=True).start()
    
    # ... (simplified versions of core methods - keeping feed, pet, take_break, reset, save_data, load_data)
    
    @rumps.clicked("Feed 🍖")
    def feed(self, sender):
        cost = 5
        if self.dumplings >= cost:
            self.dumplings -= cost
            self.happiness = min(100, self.happiness + 30)
            self.health = min(100, self.health + 20)
            self.sync_user_data()  # Sync immediately
            self.send_native_notification("🍖 Dino Fed!", f"🥟 -{cost} | Health boosted!", "Your friends might notice your healthy dino!")
    
    @rumps.clicked("Pet 🫳") 
    def pet(self, sender):
        self.happiness = min(100, self.happiness + 15)
        self.health = min(100, self.health + 5)
        self.send_native_notification("✨ Dino Petted!", "Free love boost!", "Your dino is happy!")
    
    @rumps.clicked("Take Break 🧘")
    def take_break(self, sender):
        bonus_dumplings = 3
        self.award_dumplings(bonus_dumplings, "Taking a healthy break")
        self.health = min(100, self.health + 15)
        self.energy = min(100, self.energy + 20)
        self.sync_user_data()
        self.send_native_notification("🧘 Break Taken!", f"🥟 +{bonus_dumplings} for self-care!", "Smart productivity earns more dumplings!")
    
    @rumps.clicked("Reset Day")
    def reset(self, sender):
        session_dumplings = self.dumpling_earning_session
        self.current_state = 'idle'
        self.happiness = 50
        self.energy = 50
        self.health = 100
        self.dumpling_earning_session = 0
        self.productive_time_today = 0
        self.session_start = datetime.now()
        self.time_spent = {key: 0 for key in self.time_spent}
        
        self.sync_user_data()
        self.send_native_notification("🔄 Day Reset!", f"🥟 Earned {session_dumplings:.1f} dumplings today", "Fresh start! Beat your friends tomorrow!")
    
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
                'productive_time_today': self.productive_time_today,
                'time_spent': self.time_spent,
                'session_start': self.session_start.isoformat(),
                'friends_list': self.friends_list,
                'notifications_enabled': self.notifications_enabled,
                'social_notifications_enabled': self.social_notifications_enabled
            }
            
            save_dir = os.path.expanduser("~/.dino_tamagotchi")
            os.makedirs(save_dir, exist_ok=True)
            
            with open(os.path.join(save_dir, "multiplayer_dino_data.json"), "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        """Load local data"""
        try:
            save_dir = os.path.expanduser("~/.dino_tamagotchi")
            data_file = os.path.join(save_dir, "multiplayer_dino_data.json")
            
            if os.path.exists(data_file):
                with open(data_file, "r") as f:
                    data = json.load(f)
                
                self.happiness = data.get('happiness', 50)
                self.energy = data.get('energy', 50)
                self.health = data.get('health', 100)
                self.dumplings = data.get('dumplings', 0)
                self.total_dumplings_earned = data.get('total_dumplings_earned', 0)
                self.dumpling_earning_session = data.get('dumpling_earning_session', 0)
                self.productive_time_today = data.get('productive_time_today', 0)
                self.time_spent = data.get('time_spent', self.time_spent)
                self.friends_list = data.get('friends_list', [])
                self.notifications_enabled = data.get('notifications_enabled', True)
                self.social_notifications_enabled = data.get('social_notifications_enabled', True)
                
                try:
                    saved_start = datetime.fromisoformat(data.get('session_start', datetime.now().isoformat()))
                    if (datetime.now() - saved_start).days > 0:
                        self.time_spent = {key: 0 for key in self.time_spent}
                        self.dumpling_earning_session = 0
                        self.productive_time_today = 0
                        self.session_start = datetime.now()
                    else:
                        self.session_start = saved_start
                except:
                    self.session_start = datetime.now()
                    
        except Exception as e:
            print(f"Error loading data: {e}")

    # Simplified core activity monitoring methods
    def check_current_activity(self):
        """Simplified activity checking"""
        try:
            # This would include the same app detection logic as before
            # but I'm keeping it simple for the multiplayer demo
            self.current_state = 'coding'  # Simplified for demo
            self.update_all_menu_items()
            self.save_data()
        except Exception as e:
            print(f"Error checking activity: {e}")

if __name__ == "__main__":
    print("🦕 Starting Multiplayer Dino...")
    MultiplayerDino().run()