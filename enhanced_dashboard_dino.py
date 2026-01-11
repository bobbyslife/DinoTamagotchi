#!/usr/bin/env python3

import rumps
import tkinter as tk
from tkinter import ttk, messagebox
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

class DinoDashboard:
    def __init__(self, parent_app):
        self.parent = parent_app
        self.window = None
        self.is_open = False
        
    def create_dashboard(self):
        """Create the main dashboard window"""
        if self.is_open:
            if self.window and self.window.winfo_exists():
                self.window.lift()
                self.window.focus_force()
                return
        
        self.window = tk.Tk()
        self.window.title("🦕 Dino Dashboard")
        self.window.geometry("400x600")
        self.window.resizable(False, False)
        self.is_open = True
        
        # Configure style
        style = ttk.Style()
        style.configure('Title.TLabel', font=('San Francisco', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('San Francisco', 12))
        style.configure('Small.TLabel', font=('San Francisco', 10))
        
        self.create_widgets()
        
        # Update every 5 seconds
        self.update_dashboard()
        self.schedule_updates()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Center window
        self.center_window()
        
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Create all dashboard widgets"""
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # === DINO STATUS SECTION ===
        status_frame = ttk.LabelFrame(main_frame, text="🦕 Your Dino", padding="10")
        status_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Big dino display
        self.dino_display = ttk.Label(status_frame, text="🦕", font=('San Francisco', 32))
        self.dino_display.grid(row=0, column=0, columnspan=2)
        
        self.mood_label = ttk.Label(status_frame, text="Happy & Productive", 
                                   style='Subtitle.TLabel', foreground='green')
        self.mood_label.grid(row=1, column=0, columnspan=2, pady=(5, 10))
        
        # Progress bars for stats
        ttk.Label(status_frame, text="Health:", style='Small.TLabel').grid(row=2, column=0, sticky=tk.W)
        self.health_bar = ttk.Progressbar(status_frame, length=200, mode='determinate')
        self.health_bar.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Label(status_frame, text="Energy:", style='Small.TLabel').grid(row=3, column=0, sticky=tk.W)
        self.energy_bar = ttk.Progressbar(status_frame, length=200, mode='determinate')
        self.energy_bar.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Label(status_frame, text="Mood:", style='Small.TLabel').grid(row=4, column=0, sticky=tk.W)
        self.mood_bar = ttk.Progressbar(status_frame, length=200, mode='determinate')
        self.mood_bar.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # === DUMPLINGS & ACTIVITY SECTION ===
        activity_frame = ttk.LabelFrame(main_frame, text="💰 Activity", padding="10")
        activity_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        dumplings_frame = ttk.Frame(activity_frame)
        dumplings_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.dumplings_label = ttk.Label(dumplings_frame, text="🥟 Dumplings: 0", style='Subtitle.TLabel')
        self.dumplings_label.grid(row=0, column=0, sticky=tk.W)
        
        self.session_label = ttk.Label(dumplings_frame, text="📈 Today: +0", style='Small.TLabel')
        self.session_label.grid(row=0, column=1, sticky=tk.E)
        
        self.activity_label = ttk.Label(activity_frame, text="🎯 Currently: Chilling", 
                                       style='Small.TLabel', foreground='blue')
        self.activity_label.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky=tk.W)
        
        # === SOCIAL SECTION ===
        social_frame = ttk.LabelFrame(main_frame, text="👥 Friends", padding="10")
        social_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.friends_status = ttk.Label(social_frame, text="🌐 Connecting...", style='Small.TLabel')
        self.friends_status.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        # Leaderboard frame
        self.leaderboard_frame = ttk.Frame(social_frame)
        self.leaderboard_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # === ACTIONS SECTION ===
        actions_frame = ttk.LabelFrame(main_frame, text="🎮 Actions", padding="10")
        actions_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        buttons_frame = ttk.Frame(actions_frame)
        buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(buttons_frame, text="🥟 Feed (-5 dumplings)", 
                  command=self.feed_dino, width=15).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(buttons_frame, text="🫳 Pet (Free!)", 
                  command=self.pet_dino, width=15).grid(row=0, column=1)
        
        ttk.Button(buttons_frame, text="📤 Share ID", 
                  command=self.share_id, width=15).grid(row=1, column=0, padx=(0, 5), pady=(5, 0))
        ttk.Button(buttons_frame, text="🔄 Sync Now", 
                  command=self.sync_now, width=15).grid(row=1, column=1, pady=(5, 0))
        
        # === INFO SECTION ===
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Info", padding="10")
        info_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
        self.user_info = ttk.Label(info_frame, text="Loading...", style='Small.TLabel')
        self.user_info.grid(row=0, column=0, sticky=tk.W)
        
        self.db_status = ttk.Label(info_frame, text="🗄️ Database: Connecting...", style='Small.TLabel')
        self.db_status.grid(row=1, column=0, sticky=tk.W)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        dumplings_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        
    def update_dashboard(self):
        """Update all dashboard elements"""
        if not self.window or not self.window.winfo_exists():
            return
            
        try:
            # Update dino display
            dino_emoji = self.parent.states.get(self.parent.current_state, '🦕')
            self.dino_display.config(text=dino_emoji)
            
            # Update mood based on stats
            avg_mood = (self.parent.happiness + self.parent.energy) / 2
            if avg_mood >= 80:
                mood_text = "Amazing & Energetic!"
                mood_color = 'green'
            elif avg_mood >= 60:
                mood_text = "Happy & Productive"
                mood_color = 'blue'
            elif avg_mood >= 40:
                mood_text = "Okay, needs care"
                mood_color = 'orange'
            else:
                mood_text = "Needs attention!"
                mood_color = 'red'
                
            self.mood_label.config(text=mood_text, foreground=mood_color)
            
            # Update progress bars
            self.health_bar['value'] = self.parent.health
            self.energy_bar['value'] = self.parent.energy
            self.mood_bar['value'] = self.parent.happiness
            
            # Update dumplings
            self.dumplings_label.config(text=f"🥟 Dumplings: {int(self.parent.dumplings)}")
            session_change = f"+{self.parent.dumpling_earning_session:.0f}" if self.parent.dumpling_earning_session >= 0 else f"{self.parent.dumpling_earning_session:.0f}"
            self.session_label.config(text=f"📈 Today: {session_change}")
            
            # Update current activity with friendly messages
            activity_messages = {
                'coding': '💻 Coding (earning dumplings!)',
                'working': '💼 Being productive!',
                'browsing_productive': '📖 Learning (good job!)',
                'browsing_social': '📱 Social media break',
                'browsing_entertainment': '🍿 Entertainment time',
                'browsing_news': '📰 Reading news',
                'browsing_shopping': '🛒 Shopping',
                'idle': '😴 Chilling'
            }
            
            activity_text = activity_messages.get(self.parent.current_state, '🎯 Unknown activity')
            self.activity_label.config(text=f"🎯 Currently: {activity_text}")
            
            # Update social section
            self.update_social_section()
            
            # Update info section
            self.user_info.config(text=f"👤 {self.parent.username} (ID: {self.parent.user_id})")
            db_text = "🗄️ Supabase Connected" if self.parent.use_supabase else "🗄️ Demo Mode"
            self.db_status.config(text=db_text)
            
        except Exception as e:
            print(f"Dashboard update error: {e}")
    
    def update_social_section(self):
        """Update the social/friends section"""
        try:
            # Clear existing leaderboard
            for widget in self.leaderboard_frame.winfo_children():
                widget.destroy()
            
            if self.parent.use_supabase:
                friends_data = self.parent.get_friends_data()
                
                if friends_data:
                    online_count = len([f for f in friends_data if self.is_recent_activity(f)])
                    self.friends_status.config(text=f"👥 {len(friends_data)} friends ({online_count} active)")
                    
                    # Create simple leaderboard
                    all_users = friends_data + [{
                        'username': self.parent.username,
                        'session_dumplings': self.parent.dumpling_earning_session,
                        'total_dumplings_earned': self.parent.total_dumplings_earned,
                        'user_id': self.parent.user_id
                    }]
                    
                    # Sort by session dumplings
                    sorted_users = sorted(all_users, key=lambda x: x.get('session_dumplings', 0), reverse=True)
                    
                    # Show top 3
                    for i, user in enumerate(sorted_users[:3]):
                        rank_emoji = ["🏆", "🥈", "🥉"][i] if i < 3 else "👤"
                        dumplings = int(user.get('session_dumplings', 0))
                        username = user['username']
                        
                        # Highlight current user
                        if user.get('user_id') == self.parent.user_id:
                            username = f"{username} (You!)"
                        
                        rank_label = ttk.Label(self.leaderboard_frame, 
                                             text=f"{rank_emoji} {username}: {dumplings} dumplings today",
                                             style='Small.TLabel')
                        rank_label.grid(row=i, column=0, sticky=tk.W, pady=1)
                else:
                    self.friends_status.config(text="👥 No friends yet - share your ID!")
            else:
                self.friends_status.config(text="👥 Connect to Supabase for multiplayer")
                
        except Exception as e:
            print(f"Social section update error: {e}")
            self.friends_status.config(text="👥 Error loading friends")
    
    def is_recent_activity(self, friend_data):
        """Check if friend has recent activity (within 30 minutes)"""
        try:
            last_activity = friend_data.get('last_activity')
            if not last_activity:
                return False
            
            last_time = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
            return (datetime.now() - last_time.replace(tzinfo=None)) < timedelta(minutes=30)
        except:
            return False
    
    def schedule_updates(self):
        """Schedule regular dashboard updates"""
        if self.window and self.window.winfo_exists():
            self.update_dashboard()
            self.window.after(5000, self.schedule_updates)  # Update every 5 seconds
    
    def feed_dino(self):
        """Feed the dino"""
        if self.parent.dumplings >= 5:
            self.parent.feed(None)
            messagebox.showinfo("🥟 Fed!", "Your dino enjoyed the meal!")
        else:
            messagebox.showwarning("💰 Not enough dumplings!", "You need 5 dumplings to feed your dino.")
    
    def pet_dino(self):
        """Pet the dino"""
        self.parent.pet(None)
        messagebox.showinfo("🫳 Petted!", "Your dino feels loved!")
    
    def share_id(self):
        """Share user ID"""
        self.parent.share_user_id(None)
    
    def sync_now(self):
        """Force sync with database"""
        if self.parent.use_supabase:
            self.parent.sync_to_supabase()
            messagebox.showinfo("🔄 Synced!", "Data synchronized with database.")
        else:
            messagebox.showinfo("🗄️ Demo Mode", "Connect to Supabase for real-time sync.")
    
    def on_close(self):
        """Handle dashboard close"""
        self.is_open = False
        self.window.destroy()


class EnhancedSupabaseDino(rumps.App):
    def __init__(self):
        super(EnhancedSupabaseDino, self).__init__("🦕", quit_button=None)
        
        # Supabase Configuration
        try:
            from config import SUPABASE_URL, SUPABASE_KEY, USE_SUPABASE
            self.use_supabase = USE_SUPABASE
        except ImportError:
            # Fallback configuration
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
        
        # User identification
        self.user_id = self.load_or_create_user_id()
        self.username = self.load_or_create_username()
        
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
        
        # Website categories (simplified for friendlier UI)
        self.website_categories = {
            'productive': {
                'domains': ['github.com', 'stackoverflow.com', 'docs.', 'developer.', 'learn.', 'coursera.com', 'udemy.com'],
                'keywords': ['documentation', 'tutorial', 'learn', 'course', 'guide'],
                'dumpling_rate': 2.0,  # Coding rate
                'emoji': '💻'
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
        
        # Dumpling system (treats)
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
        
        # Create dashboard
        self.dashboard = DinoDashboard(self)
        
        # Load saved data
        self.load_data()
        
        # Initialize user in database
        self.initialize_user()
        
        # Create minimal menu
        self.create_minimal_menu()
        
        # Send welcome notification (friendlier)
        self.send_native_notification("🦕 Dino Companion Started!", 
                                    f"Welcome back, {self.username}! 🥟 {int(self.dumplings)} dumplings",
                                    "Ready to be productive with your dino friend!")
        
        # Start monitoring
        self.start_monitoring()
        self.start_dumpling_monitoring()
        self.start_social_monitoring()
        self.start_realtime_sync()
        
        print(f"🦕 Enhanced Dino Started!")
        print(f"👤 User: {self.username} (ID: {self.user_id})")
        print(f"🥟 Dumplings: {int(self.dumplings)}")
        print(f"🗄️ Database: {'Supabase' if self.use_supabase else 'Local Demo'}")

    def create_minimal_menu(self):
        """Create ultra-minimal menu bar"""
        # Get current mood
        avg_mood = (self.happiness + self.energy) / 2
        if avg_mood >= 80:
            mood = "Amazing"
        elif avg_mood >= 60:
            mood = "Happy"
        elif avg_mood >= 40:
            mood = "Okay"
        else:
            mood = "Tired"
        
        self.status_item = rumps.MenuItem(f"Status: {mood}")
        
        self.menu = [
            self.status_item,
            rumps.separator,
            rumps.MenuItem("🏠 Open Dashboard", callback=self.open_dashboard),
            rumps.separator,
            rumps.MenuItem("🍖 Quick Feed", callback=self.feed),
            rumps.MenuItem("🫳 Quick Pet", callback=self.pet),
            rumps.separator,
            rumps.MenuItem("⚙️ Settings", callback=self.show_settings),
            rumps.MenuItem("🔄 Quit", callback=self.quit_app)
        ]

    @rumps.clicked("🏠 Open Dashboard")
    def open_dashboard(self, sender):
        """Open the main dashboard"""
        try:
            self.dashboard.create_dashboard()
        except Exception as e:
            print(f"Error opening dashboard: {e}")
            self.send_native_notification("❌ Dashboard Error", 
                                        "Could not open dashboard",
                                        "Please check console for details")

    def show_settings(self, sender):
        """Show simple settings dialog"""
        import tkinter as tk
        from tkinter import messagebox, simpledialog
        
        root = tk.Tk()
        root.withdraw()
        
        action = messagebox.askyesnocancel("⚙️ Settings", 
                                         "Would you like to:\n\n" +
                                         "YES - Change username\n" +
                                         "NO - Toggle notifications\n" +
                                         "CANCEL - Close")
        
        if action is True:  # Change username
            new_username = simpledialog.askstring("Username", "Enter new username:")
            if new_username and new_username.strip():
                self.username = new_username.strip()
                self.save_username()
                messagebox.showinfo("✅ Success", f"Username changed to: {self.username}")
        elif action is False:  # Toggle notifications
            self.notifications_enabled = not self.notifications_enabled
            status = "enabled" if self.notifications_enabled else "disabled"
            messagebox.showinfo("🔔 Notifications", f"Notifications {status}")
        
        root.destroy()

    def save_username(self):
        """Save username to file"""
        username_file = os.path.expanduser("~/.dino_tamagotchi/username.txt")
        os.makedirs(os.path.dirname(username_file), exist_ok=True)
        with open(username_file, 'w') as f:
            f.write(self.username)

    def quit_app(self, sender):
        """Quit the application"""
        try:
            # Save data before quitting
            self.save_data()
            if self.use_supabase:
                self.sync_to_supabase()
            
            self.send_native_notification("👋 Goodbye!", 
                                        f"See you later, {self.username}!",
                                        "Your dino will miss you!")
            rumps.quit_application()
        except Exception as e:
            print(f"Error during quit: {e}")
            rumps.quit_application()

    # Include all the core methods from original implementation
    # (I'll add key ones here, but we need to copy over the essential monitoring/tracking methods)
    
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

    def load_custom_categories(self):
        """Load custom website categories"""
        try:
            custom_file = os.path.expanduser("~/.dino_tamagotchi/custom_categories.json")
            if os.path.exists(custom_file):
                with open(custom_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_data(self):
        """Save current state"""
        try:
            data = {
                'happiness': self.happiness,
                'energy': self.energy,
                'health': self.health,
                'dumplings': self.dumplings,
                'total_dumplings_earned': self.total_dumplings_earned,
                'time_spent': self.time_spent,
                'custom_website_categories': self.custom_website_categories
            }
            
            save_dir = os.path.expanduser("~/.dino_tamagotchi")
            os.makedirs(save_dir, exist_ok=True)
            
            with open(f"{save_dir}/save_data.json", 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        """Load saved state"""
        try:
            save_file = os.path.expanduser("~/.dino_tamagotchi/save_data.json")
            if os.path.exists(save_file):
                with open(save_file, 'r') as f:
                    data = json.load(f)
                
                self.happiness = data.get('happiness', 50)
                self.energy = data.get('energy', 50)
                self.health = data.get('health', 100)
                self.dumplings = data.get('dumplings', 0)
                self.total_dumplings_earned = data.get('total_dumplings_earned', 0)
                self.time_spent = data.get('time_spent', self.time_spent)
                self.custom_website_categories.update(data.get('custom_website_categories', {}))
        except Exception as e:
            print(f"Error loading data: {e}")

    def send_native_notification(self, title, message, subtitle=""):
        """Send native macOS notification"""
        if not self.notifications_enabled:
            return
            
        try:
            script = f'''
            display notification "{message}" with title "{title}" subtitle "{subtitle}"
            '''
            subprocess.run(['osascript', '-e', script], check=True)
        except Exception as e:
            print(f"Notification error: {e}")

    @rumps.clicked("🍖 Quick Feed")
    def feed(self, sender):
        """Feed the dino"""
        if self.dumplings >= 5:
            self.dumplings -= 5
            self.happiness = min(100, self.happiness + 15)
            self.health = min(100, self.health + 10)
            
            self.send_native_notification("🥟 Nom Nom!", 
                                        "Your dino enjoyed the meal!",
                                        f"Health +10, Happiness +15")
            self.save_data()
            if self.use_supabase:
                self.sync_to_supabase()
        else:
            self.send_native_notification("💰 Not Enough Dumplings!", 
                                        "You need 5 dumplings to feed your dino",
                                        "Earn more by being productive!")

    @rumps.clicked("🫳 Quick Pet")  
    def pet(self, sender):
        """Pet the dino"""
        self.happiness = min(100, self.happiness + 8)
        self.energy = min(100, self.energy + 5)
        
        self.send_native_notification("🫳 Aww!", 
                                    "Your dino feels loved!",
                                    f"Happiness +8, Energy +5")
        self.save_data()

    def get_friends_data(self):
        """Get friends data from Supabase"""
        if not self.use_supabase:
            return []
        
        try:
            # For now, get all users except current user
            result = self.supabase.table('users').select('*').neq('user_id', self.user_id).limit(10).execute()
            return result.data
        except Exception as e:
            print(f"Error getting friends data: {e}")
            return []

    def initialize_user(self):
        """Initialize user in Supabase database"""
        if not self.use_supabase:
            return
        
        try:
            result = self.supabase.table('users').select('*').eq('user_id', self.user_id).execute()
            
            if not result.data:
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
            
            self.supabase.table('users').update(user_data).eq('user_id', self.user_id).execute()
            self.last_sync_time = datetime.now()
            
        except Exception as e:
            print(f"❌ Error syncing to Supabase: {e}")

    def share_user_id(self, sender):
        """Share user ID for adding friends"""
        try:
            subprocess.run(['pbcopy'], input=self.user_id.encode(), check=True)
            clipboard_note = " (Copied!)"
        except:
            clipboard_note = ""
        
        self.send_native_notification("🆔 Your Dino ID", 
                                    f"{self.user_id}{clipboard_note}",
                                    f"Share this with friends to compete!")

    # === CORE MONITORING SYSTEM ===
    def start_monitoring(self):
        """Start activity monitoring"""
        def monitor():
            while True:
                try:
                    self.detect_current_activity()
                    self.update_menu_title()
                    # Small delay to prevent excessive CPU usage
                    time.sleep(30)
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(30)
        
        threading.Thread(target=monitor, daemon=True).start()
        print("🔍 Activity monitoring started")

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
                if any(app in app_name for app in ['code', 'xcode', 'vim', 'atom', 'sublime', 'cursor']):
                    self.current_state = 'coding'
                    self.current_website = None
                    self.current_website_category = None
                elif any(app in app_name for app in ['slack', 'teams', 'notion', 'trello']):
                    self.current_state = 'working'
                    self.current_website = None
                    self.current_website_category = None
                elif any(app in app_name for app in ['figma', 'sketch', 'photoshop']):
                    self.current_state = 'designing'
                    self.current_website = None
                    self.current_website_category = None
                else:
                    # Default to idle if unknown app
                    if self.current_state not in ['idle', 'eating', 'sick']:
                        self.current_state = 'idle'
                    self.current_website = None
                    self.current_website_category = None
                    
        except Exception as e:
            print(f"Error detecting activity: {e}")

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
                self.current_website = url
                self.current_website_category = category
                
                # Determine state based on category
                self.current_state = f'browsing_{category}' if category != 'other' else 'browsing_other'
                    
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
            
            return 'other'
            
        except Exception as e:
            print(f"Error categorizing website: {e}")
            return 'other'

    def start_dumpling_monitoring(self):
        """Start dumpling earning monitoring"""
        def dumpling_monitor():
            while True:
                try:
                    self.calculate_dumpling_earnings()
                    self.update_stats()
                except Exception as e:
                    print(f"Dumpling monitor error: {e}")
                time.sleep(60)  # Check every minute
        
        threading.Thread(target=dumpling_monitor, daemon=True).start()
        print("🥟 Dumpling monitoring started")

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
            self.productive_time_today += time_since_last
        elif self.current_state == 'working':
            dumplings_earned = 0.8 * time_since_last
            self.productive_time_today += time_since_last
        elif self.current_state == 'designing':
            dumplings_earned = 1.5 * time_since_last
            self.productive_time_today += time_since_last
        elif self.current_state.startswith('browsing_'):
            # Use website category rates
            if self.current_website_category and self.current_website_category in self.website_categories:
                rate = self.website_categories[self.current_website_category]['dumpling_rate']
                dumplings_earned = rate * time_since_last
                
                # Add to productive time if it's a productive category
                if rate > 0:
                    self.productive_time_today += time_since_last
        
        # Apply earnings
        if dumplings_earned != 0:
            self.dumplings += dumplings_earned
            self.dumpling_earning_session += dumplings_earned
            if dumplings_earned > 0:
                self.total_dumplings_earned += dumplings_earned
        
        # Update mood based on activity
        if dumplings_earned > 0:
            self.happiness = min(100, self.happiness + 1)
            self.energy = min(100, self.energy + 0.5)
        elif dumplings_earned < 0:
            self.happiness = max(0, self.happiness - 0.5)
            self.energy = max(0, self.energy - 0.2)
        
        self.last_dumpling_time = now

    def update_stats(self):
        """Update dino stats"""
        # Gradually decrease stats over time
        now = datetime.now()
        time_diff = (now - getattr(self, 'last_stat_update', now)).total_seconds() / 3600  # Hours
        
        if time_diff > 0:
            # Decrease energy and happiness slowly over time
            self.energy = max(0, self.energy - time_diff * 2)
            self.happiness = max(0, self.happiness - time_diff * 1)
            
            # Health depends on other stats
            if self.energy < 20 or self.happiness < 20:
                self.health = max(0, self.health - time_diff * 5)
            else:
                self.health = min(100, self.health + time_diff * 1)
        
        self.last_stat_update = now

    def update_menu_title(self):
        """Update menu bar title with current state"""
        try:
            dino_emoji = self.states.get(self.current_state, '🦕')
            self.title = dino_emoji
        except Exception as e:
            print(f"Error updating menu title: {e}")

    def start_social_monitoring(self):
        """Start social monitoring"""
        def social_monitor():
            while True:
                try:
                    if self.social_notifications_enabled and self.use_supabase:
                        self.check_competitive_updates()
                except Exception as e:
                    print(f"Social monitor error: {e}")
                time.sleep(300)  # Check every 5 minutes
        
        threading.Thread(target=social_monitor, daemon=True).start()
        print("👥 Social monitoring started")

    def check_competitive_updates(self):
        """Check for competitive updates and send notifications"""
        try:
            friends_data = self.get_friends_data()
            
            if not friends_data:
                return
            
            now = datetime.now()
            
            # Don't spam notifications
            if (self.last_social_update and 
                now - self.last_social_update < timedelta(minutes=15)):
                return
            
            # Find the highest performer today
            top_performer = max(friends_data, key=lambda x: x.get('session_dumplings', 0))
            my_session_dumplings = self.dumpling_earning_session
            
            # If someone is significantly ahead of you
            if top_performer['session_dumplings'] > my_session_dumplings + 20:
                gap = top_performer['session_dumplings'] - my_session_dumplings
                
                self.send_native_notification(
                    "🏃‍♂️ Falling Behind!",
                    f"{top_performer['username']} has {gap:.0f} more dumplings!",
                    f"Time to catch up! 🥟"
                )
                self.last_social_update = now
                
        except Exception as e:
            print(f"Error checking competitive updates: {e}")

    def start_realtime_sync(self):
        """Start real-time syncing"""
        def sync_loop():
            while True:
                try:
                    if self.use_supabase:
                        self.sync_to_supabase()
                except Exception as e:
                    print(f"Sync error: {e}")
                time.sleep(120)  # Sync every 2 minutes
        
        threading.Thread(target=sync_loop, daemon=True).start()
        print("🔄 Real-time sync started")

if __name__ == "__main__":
    app = EnhancedSupabaseDino()
    app.run()