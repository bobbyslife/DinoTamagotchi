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
        
        # Progress bar for health
        ttk.Label(status_frame, text="Health:", style='Small.TLabel').grid(row=2, column=0, sticky=tk.W)
        self.health_bar = ttk.Progressbar(status_frame, length=200, mode='determinate')
        self.health_bar.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
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
        
        # Friend management in dashboard
        ttk.Button(buttons_frame, text="👥 Add Friend", 
                  command=self.add_friend_by_code, width=15).grid(row=2, column=0, padx=(0, 5), pady=(5, 0))
        ttk.Button(buttons_frame, text="📤 Invite", 
                  command=self.invite_from_dashboard, width=15).grid(row=2, column=1, pady=(5, 0))
        
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
            
            # Update status based on health
            if self.parent.health >= 80:
                status_text = "Healthy & Strong!"
                status_color = 'green'
            elif self.parent.health >= 60:
                status_text = "Doing Well"
                status_color = 'blue'
            elif self.parent.health >= 40:
                status_text = "Okay, needs care"
                status_color = 'orange'
            else:
                status_text = "Needs attention!"
                status_color = 'red'
                
            self.mood_label.config(text=status_text, foreground=status_color)
            
            # Update health progress bar
            self.health_bar['value'] = self.parent.health
            
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

    def add_friend_by_code(self):
        """Add friend by friend code through dashboard"""
        from tkinter import simpledialog
        
        if not self.parent.use_supabase:
            messagebox.showwarning("🗄️ Setup Required", "Connect to Supabase for multiplayer features.")
            return
        
        friend_code = simpledialog.askstring("👥 Add Friend", 
                                           "Enter your friend's code:")
        
        if friend_code and friend_code.strip():
            result = self.parent.add_friend_by_code(friend_code.strip())
            if result:
                messagebox.showinfo("✅ Friend Added!", f"Successfully added {result}!")
            else:
                messagebox.showwarning("❌ Not Found", "Friend code not found. Make sure it's correct!")

    def invite_from_dashboard(self):
        """Show invitation from dashboard"""
        self.parent.invite_friends(None)
    
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
            'coding': {
                'domains': ['github.com', 'gitlab.com', 'bitbucket.org', 'stackoverflow.com', 'codepen.io', 'replit.com'],
                'keywords': ['code', 'repository', 'commit', 'pull request', 'api'],
                'dumpling_rate': 2.0,
                'emoji': '💻'
            },
            'learning': {
                'domains': ['docs.', 'developer.', 'learn.', 'coursera.com', 'udemy.com', 'khanacademy.org', 'pluralsight.com'],
                'keywords': ['documentation', 'tutorial', 'learn', 'course', 'guide', 'training'],
                'dumpling_rate': 1.8,
                'emoji': '📚'
            },
            'designing': {
                'domains': ['figma.com', 'sketch.com', 'adobe.com', 'dribbble.com', 'behance.net', 'canva.com'],
                'keywords': ['design', 'ui', 'ux', 'prototype', 'mockup', 'wireframe'],
                'dumpling_rate': 1.5,
                'emoji': '🎨'
            },
            'productivity': {
                'domains': ['notion.so', 'trello.com', 'asana.com', 'monday.com', 'linear.app', 'todoist.com'],
                'keywords': ['task', 'project', 'todo', 'organize', 'planning'],
                'dumpling_rate': 1.2,
                'emoji': '📋'
            },
            'communication': {
                'domains': ['gmail.com', 'outlook.com', 'slack.com', 'discord.com', 'zoom.us', 'teams.microsoft.com'],
                'keywords': ['email', 'message', 'meeting', 'call', 'chat'],
                'dumpling_rate': 0.8,
                'emoji': '💼'
            },
            'research': {
                'domains': ['wikipedia.org', 'scholar.google.com', 'medium.com', 'dev.to', 'hashnode.com'],
                'keywords': ['research', 'article', 'paper', 'study', 'analysis'],
                'dumpling_rate': 1.0,
                'emoji': '🔍'
            },
            'social': {
                'domains': ['twitter.com', 'x.com', 'facebook.com', 'instagram.com', 'reddit.com', 'tiktok.com', 'linkedin.com'],
                'keywords': ['social', 'post', 'feed', 'comment', 'like', 'share'],
                'dumpling_rate': -0.2,
                'emoji': '📱'
            },
            'news': {
                'domains': ['news.', 'cnn.com', 'bbc.com', 'nytimes.com', 'techcrunch.com', 'ycombinator.com', 'hackernews'],
                'keywords': ['news', 'article', 'breaking', 'headlines'],
                'dumpling_rate': -0.1,
                'emoji': '📰'
            },
            'entertainment': {
                'domains': ['youtube.com', 'netflix.com', 'twitch.tv', 'spotify.com', 'hulu.com', 'disney.com'],
                'keywords': ['video', 'music', 'stream', 'watch', 'movie', 'show'],
                'dumpling_rate': -0.3,
                'emoji': '🍿'
            },
            'gaming': {
                'domains': ['steam.com', 'twitch.tv/directory/game', 'itch.io', 'epicgames.com'],
                'keywords': ['game', 'gaming', 'play', 'level', 'achievement'],
                'dumpling_rate': -0.4,
                'emoji': '🎮'
            },
            'shopping': {
                'domains': ['amazon.com', 'ebay.com', 'etsy.com', 'shopify.com', 'target.com', 'walmart.com'],
                'keywords': ['shop', 'buy', 'cart', 'checkout', 'purchase', 'deal'],
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
        
        # Enhanced multiplayer stats
        self.friends_list = []
        self.daily_ranking = 0
        self.online_friends = []
        self.friend_requests = []
        self.friend_code = None  # For easy sharing
        
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
        
        # Create enhanced menu
        self.create_enhanced_menu()
        
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

    def create_enhanced_menu(self):
        """Create enhanced but cleaner menu"""
        # Get current status based on health
        if self.health >= 80:
            status = "Healthy"
        elif self.health >= 60:
            status = "Good"
        elif self.health >= 40:
            status = "Okay"
        else:
            status = "Needs Care"
        
        # Create menu items
        self.status_item = rumps.MenuItem(f"Status: {status}")
        
        # User info (cleaner)
        online_status = "🟢 Online" if self.use_supabase else "🔴 Offline"
        self.user_info_item = rumps.MenuItem(f"👤 {self.username} • {online_status}")
        self.dumplings_item = rumps.MenuItem(f"🥟 Dumplings: {int(self.dumplings)}")
        self.session_item = rumps.MenuItem(f"📈 Today: +{self.dumpling_earning_session:.0f}")
        
        # Essential stats (simplified)
        self.health_item = rumps.MenuItem(f"❤️ Health: {int(self.health)}%")
        
        # Current activity (friendlier)
        activity_text = self.get_friendly_activity_text()
        self.activity_item = rumps.MenuItem(f"🎯 {activity_text}")
        
        # Time tracking (top categories only)
        session_minutes = int((datetime.now() - self.session_start).total_seconds() / 60)
        self.session_time_item = rumps.MenuItem(f"⏰ Session: {session_minutes}m")
        
        # Key time stats
        coding_time = int(self.time_spent.get('coding', 0) / 60)
        social_time = int(self.time_spent.get('browsing_social', 0) / 60)
        
        self.coding_time_item = rumps.MenuItem(f"  💻 Coding: {coding_time}m")
        self.social_time_item = rumps.MenuItem(f"  📱 Social: {social_time}m")
        
        # Multiplayer (simplified)
        self.ranking_item = rumps.MenuItem("🏆 Checking rankings...")
        
        # Actions
        self.notifications_toggle = rumps.MenuItem("🔔 Notifications: ON", callback=self.toggle_notifications)
        
        # Build menu
        self.menu = [
            self.status_item,
            rumps.separator,
            self.user_info_item,
            self.dumplings_item,
            self.session_item,
            self.ranking_item,
            rumps.separator,
            self.health_item,
            rumps.separator,
            self.activity_item,
            self.session_time_item,
            self.coding_time_item,
            self.social_time_item,
            rumps.separator,
            rumps.MenuItem("🥟 Feed (-5)", callback=self.feed),
            rumps.MenuItem("🫳 Pet (free)", callback=self.pet),
            rumps.separator,
            rumps.MenuItem("👥 Community", callback=self.show_friends_menu),
            rumps.MenuItem("📤 Invite Friends", callback=self.invite_friends),
            rumps.MenuItem("🆔 My Friend Code", callback=self.share_friend_code),
            self.notifications_toggle,
            rumps.MenuItem("🔔 Test Notification", callback=self.test_notification),
            rumps.separator,
            rumps.MenuItem("🔄 Quit", callback=self.quit_app)
        ]

    def get_friendly_activity_text(self):
        """Get friendly description of current activity"""
        activity_messages = {
            'coding': 'Coding (earning dumplings!)',
            'working': 'Being productive!',
            'browsing_productive': 'Learning',
            'browsing_social': 'Social media',
            'browsing_entertainment': 'Entertainment',
            'browsing_news': 'Reading news',
            'browsing_shopping': 'Shopping',
            'idle': 'Chilling'
        }
        return activity_messages.get(self.current_state, 'Unknown activity')

    def show_friends_menu(self, sender):
        """Show enhanced friends and multiplayer menu"""
        if not self.use_supabase:
            self.send_native_notification("🗄️ Supabase Setup Required",
                                        "Connect to database for multiplayer",
                                        "Update SUPABASE_URL and SUPABASE_KEY in code")
            return
        
        try:
            friends_data = self.get_friends_data()
            online_count = len([f for f in friends_data if self.is_recent_activity(f)])
            
            if friends_data:
                # Show friend status and leaderboard
                self.show_detailed_leaderboard(friends_data)
            else:
                self.send_native_notification("👥 No Friends Yet!",
                                            f"Share your friend code: {self.get_friend_code()}",
                                            "Invite friends to compete and have more fun!")
        except Exception as e:
            print(f"Friends menu error: {e}")
            self.send_native_notification("❌ Connection Error",
                                        "Could not load friends data",
                                        "Check your internet connection")

    def invite_friends(self, sender):
        """Create and share invitation"""
        import tkinter as tk
        from tkinter import messagebox
        
        if not self.use_supabase:
            self.send_native_notification("🗄️ Setup Required",
                                        "Connect to Supabase first",
                                        "Multiplayer needs database connection")
            return
        
        friend_code = self.get_friend_code()
        invitation_text = f"""🦕 Join me in Dino Tamagotchi!

I'm using a cute productivity app where you care for a virtual dino that lives in your menu bar! It earns dumplings by being productive and we can compete in real-time.

🌟 See everyone's dinos: https://dino.rest
📱 Download & setup guide: https://dino.rest/#download

My Friend Code: {friend_code}
My Username: {self.username}

1. Visit the website to see the community
2. Follow the download guide 
3. Add my friend code to start competing!

Currently I have {int(self.dumplings)} dumplings! Let's motivate each other to stay productive! 🏆"""
        
        try:
            # Copy invitation to clipboard
            import subprocess
            subprocess.run(['pbcopy'], input=invitation_text.encode(), check=True)
            
            self.send_native_notification("📤 Invitation Ready!",
                                        "Invitation copied to clipboard",
                                        f"Share it to invite friends! Code: {friend_code}")
        except:
            # Fallback - show in dialog
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("📤 Invitation Text", invitation_text)
            root.destroy()

    def share_friend_code(self, sender):
        """Share simplified friend code"""
        friend_code = self.get_friend_code()
        
        try:
            import subprocess
            subprocess.run(['pbcopy'], input=friend_code.encode(), check=True)
            clipboard_note = " (Copied!)"
        except:
            clipboard_note = ""
        
        self.send_native_notification("🆔 My Friend Code",
                                    f"{friend_code}{clipboard_note}",
                                    f"Share this code so friends can add you!")

    def get_friend_code(self):
        """Get or create a memorable friend code"""
        if not self.friend_code:
            # Create a more memorable friend code based on user ID and username
            import hashlib
            hash_input = f"{self.user_id}-{self.username}".encode()
            hash_result = hashlib.md5(hash_input).hexdigest()[:6].upper()
            self.friend_code = f"{self.username[:4].upper()}-{hash_result}"
        
        return self.friend_code

    def show_detailed_leaderboard(self, friends_data):
        """Show detailed leaderboard with friend status"""
        try:
            # Add yourself to the data
            all_users = friends_data + [{
                'username': self.username,
                'session_dumplings': self.dumpling_earning_session,
                'total_dumplings_earned': self.total_dumplings_earned,
                'user_id': self.user_id,
                'health': self.health,
                'current_state': self.current_state,
                'last_activity': datetime.now().isoformat()
            }]
            
            # Sort by session dumplings
            sorted_users = sorted(all_users, key=lambda x: x.get('session_dumplings', 0), reverse=True)
            
            my_rank = next((i+1 for i, user in enumerate(sorted_users) if user.get('user_id') == self.user_id), len(all_users))
            
            # Count online friends
            online_count = len([f for f in friends_data if self.is_recent_activity(f)])
            
            # Create detailed status message
            top_3 = sorted_users[:3]
            leaderboard_text = "\\n".join([
                f"{'🏆' if i==0 else '🥈' if i==1 else '🥉'} {user['username']}: {int(user.get('session_dumplings', 0))} dumplings"
                for i, user in enumerate(top_3)
            ])
            
            # Show current activities of friends
            friend_activities = []
            for friend in friends_data[:3]:  # Show top 3 friends' activities
                if self.is_recent_activity(friend):
                    state = friend.get('current_state', 'idle')
                    activity = self.get_friendly_activity_from_state(state)
                    friend_activities.append(f"• {friend['username']}: {activity}")
            
            activities_text = "\\n".join(friend_activities) if friend_activities else "No friends currently active"
            
            self.send_native_notification("🏆 Daily Leaderboard",
                                        f"{leaderboard_text}\\n\\nYou're #{my_rank} of {len(all_users)}",
                                        f"{online_count}/{len(friends_data)} friends online")
            
            # Update menu item
            self.ranking_item.title = f"🏆 #{my_rank} of {len(all_users)} • {online_count} online"
            
        except Exception as e:
            print(f"Detailed leaderboard error: {e}")

    def get_friendly_activity_from_state(self, state):
        """Convert state to friendly activity description"""
        activity_map = {
            'coding': 'Coding 💻',
            'working': 'Working 💼', 
            'browsing_productive': 'Learning 📖',
            'browsing_social': 'Social media 📱',
            'browsing_entertainment': 'Entertainment 🍿',
            'browsing_news': 'Reading news 📰',
            'browsing_shopping': 'Shopping 🛒',
            'idle': 'Chilling 😴'
        }
        return activity_map.get(state, 'Unknown activity')

    def is_recent_activity(self, friend_data):
        """Check if friend has recent activity (within 30 minutes)"""
        try:
            last_activity = friend_data.get('last_activity')
            if not last_activity:
                return False
            
            # Handle different datetime formats
            if last_activity.endswith('Z'):
                last_activity = last_activity[:-1] + '+00:00'
            
            last_time = datetime.fromisoformat(last_activity)
            if last_time.tzinfo:
                last_time = last_time.replace(tzinfo=None)
                
            return (datetime.now() - last_time) < timedelta(minutes=30)
        except Exception as e:
            print(f"Activity check error: {e}")
            return False

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
                    f"{'🏆' if i==0 else '🥈' if i==1 else '🥉'} {user['username']}: {int(user.get('session_dumplings', 0))} today"
                    for i, user in enumerate(top_3)
                ])
                
                self.send_native_notification("🏆 Daily Leaderboard",
                                            leaderboard,
                                            f"You're #{my_rank} of {len(all_users)}")
                
                # Update menu item
                self.ranking_item.title = f"🏆 You're #{my_rank} of {len(all_users)}"
            else:
                self.send_native_notification("👥 No Friends Yet",
                                            "Share your ID to compete with friends!",
                                            f"Your ID: {self.user_id}")
                self.ranking_item.title = "🏆 Share ID for multiplayer"
                
        except Exception as e:
            print(f"Leaderboard error: {e}")
            self.send_native_notification("❌ Leaderboard Error",
                                        "Could not load rankings",
                                        "Check your connection")

    def toggle_notifications(self, sender):
        """Toggle notifications"""
        self.notifications_enabled = not self.notifications_enabled
        status = "ON" if self.notifications_enabled else "OFF"
        sender.title = f"🔔 Notifications: {status}"
        
        self.send_native_notification("🔔 Notifications",
                                    f"Notifications {status.lower()}",
                                    "Settings updated")
    
    @rumps.clicked("🔔 Test Notification")  
    def test_notification(self, sender):
        """Test notification system"""
        self.send_native_notification("🦕 Test Notification", 
                                    "If you see this, notifications are working!", 
                                    "Dino Tamagotchi")

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
            self.health = min(100, self.health + 20)
            
            self.send_native_notification("🥟 Nom Nom!", 
                                        "Your dino enjoyed the meal!",
                                        f"Health +20")
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
        self.health = min(100, self.health + 10)
        
        self.send_native_notification("🫳 Aww!", 
                                    "Your dino feels loved!",
                                    f"Health +10")
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
        
        # Update health based on activity
        if dumplings_earned > 0:
            self.health = min(100, self.health + 0.5)  # Gradual health improvement
        elif dumplings_earned < 0:
            self.health = max(0, self.health - 0.3)  # Gradual health decline
        
        self.last_dumpling_time = now

    def update_stats(self):
        """Update dino stats"""
        # Gradually decrease health over time if not being productive
        now = datetime.now()
        time_diff = (now - getattr(self, 'last_stat_update', now)).total_seconds() / 3600  # Hours
        
        if time_diff > 0:
            # Health decreases slowly over time without care
            self.health = max(0, self.health - time_diff * 1)
        
        self.last_stat_update = now

    def update_menu_title(self):
        """Update menu bar title with current state"""
        try:
            dino_emoji = self.states.get(self.current_state, '🦕')
            self.title = dino_emoji
            
            # Update menu items
            self.update_menu_items()
        except Exception as e:
            print(f"Error updating menu title: {e}")

    def update_menu_items(self):
        """Update dynamic menu items"""
        try:
            # Update status based on health
            if self.health >= 80:
                status = "Healthy"
            elif self.health >= 60:
                status = "Good"
            elif self.health >= 40:
                status = "Okay"
            else:
                status = "Needs Care"
            
            self.status_item.title = f"Status: {status}"
            
            # Update user info with online/offline status
            online_status = "🟢 Online" if self.use_supabase else "🔴 Offline"
            self.user_info_item.title = f"👤 {self.username} • {online_status}"
            
            self.dumplings_item.title = f"🥟 Dumplings: {int(self.dumplings)}"
            self.session_item.title = f"📈 Today: +{self.dumpling_earning_session:.0f}"
            
            self.health_item.title = f"❤️ Health: {int(self.health)}%"
            
            # Update activity
            activity_text = self.get_friendly_activity_text()
            self.activity_item.title = f"🎯 {activity_text}"
            
            # Update time tracking
            session_minutes = int((datetime.now() - self.session_start).total_seconds() / 60)
            self.session_time_item.title = f"⏰ Session: {session_minutes}m"
            
            coding_time = int(self.time_spent.get('coding', 0) / 60)
            social_time = int(self.time_spent.get('browsing_social', 0) / 60)
            
            self.coding_time_item.title = f"  💻 Coding: {coding_time}m"
            self.social_time_item.title = f"  📱 Social: {social_time}m"
            
        except Exception as e:
            print(f"Error updating menu items: {e}")

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
        """Check for competitive updates and send engaging notifications"""
        try:
            friends_data = self.get_friends_data()
            
            if not friends_data:
                return
            
            now = datetime.now()
            
            # Don't spam notifications
            if (self.last_social_update and 
                now - self.last_social_update < timedelta(minutes=15)):
                return
            
            my_session_dumplings = self.dumpling_earning_session
            
            # Find interesting social dynamics
            notifications_sent = 0
            
            # 1. Check if someone passed you
            sorted_users = sorted(friends_data, key=lambda x: x.get('session_dumplings', 0), reverse=True)
            my_rank = len([f for f in friends_data if f.get('session_dumplings', 0) > my_session_dumplings]) + 1
            
            for friend in sorted_users[:3]:  # Check top 3
                friend_dumplings = friend.get('session_dumplings', 0)
                
                # Someone just passed you with a small margin
                if (friend_dumplings > my_session_dumplings and 
                    friend_dumplings - my_session_dumplings <= 10 and
                    self.is_recent_activity(friend)):
                    
                    activity = self.get_friendly_activity_from_state(friend.get('current_state', 'idle'))
                    self.send_native_notification(
                        "🏆 Competition Alert!",
                        f"{friend['username']} just passed you while {activity}",
                        f"They're ahead by {friend_dumplings - my_session_dumplings:.0f} dumplings!"
                    )
                    notifications_sent += 1
                    break
            
            # 2. Motivational notifications for big gaps
            if not notifications_sent:
                top_performer = max(friends_data, key=lambda x: x.get('session_dumplings', 0))
                
                if top_performer['session_dumplings'] > my_session_dumplings + 30:
                    gap = top_performer['session_dumplings'] - my_session_dumplings
                    
                    motivational_messages = [
                        f"🚀 {top_performer['username']} is crushing it with {gap:.0f} more dumplings!",
                        f"💪 Time to step up! {top_performer['username']} is {gap:.0f} ahead!",
                        f"🔥 {top_performer['username']} is on fire! Can you catch up?",
                    ]
                    
                    import random
                    message = random.choice(motivational_messages)
                    
                    self.send_native_notification(
                        "🏃‍♂️ Challenge Time!",
                        message,
                        "Your dino believes in you! 🦕"
                    )
                    notifications_sent += 1
            
            # 3. Friend achievement celebrations
            if not notifications_sent:
                for friend in friends_data:
                    friend_total = friend.get('total_dumplings_earned', 0)
                    
                    # Check for milestone achievements (every 100 dumplings)
                    if friend_total > 0 and friend_total % 100 < 5:  # Just hit a milestone
                        self.send_native_notification(
                            "🎉 Friend Achievement!",
                            f"{friend['username']} just hit {friend_total} total dumplings!",
                            "Send them a congrats! 🥳"
                        )
                        notifications_sent += 1
                        break
            
            # 4. Productivity buddy notifications
            if not notifications_sent:
                # Find friends who are currently being productive
                productive_friends = [
                    f for f in friends_data 
                    if (f.get('current_state', '').startswith('coding') or 
                        f.get('current_state', '').startswith('working')) and
                    self.is_recent_activity(f)
                ]
                
                if productive_friends and self.current_state in ['idle', 'browsing_social', 'browsing_entertainment']:
                    friend = random.choice(productive_friends)
                    activity = self.get_friendly_activity_from_state(friend.get('current_state', 'working'))
                    
                    self.send_native_notification(
                        "💼 Productivity Buddy Alert!",
                        f"{friend['username']} is {activity} right now!",
                        "Maybe join them? Your dino would love some productivity! 🦕"
                    )
                    notifications_sent += 1
            
            if notifications_sent > 0:
                self.last_social_update = now
                
        except Exception as e:
            print(f"Error checking competitive updates: {e}")

    def add_friend_by_code(self, friend_code):
        """Add friend by their friend code"""
        if not self.use_supabase:
            return None
            
        try:
            # Find user by friend code pattern
            # Friend codes are like "DINO-ABC123" where DINO is username prefix
            username_prefix = friend_code.split('-')[0].lower()
            
            # Search for users with matching friend code pattern
            result = self.supabase.table('users').select('*').execute()
            
            for user in result.data:
                if user['user_id'] == self.user_id:  # Don't add yourself
                    continue
                
                # Check if this user's friend code matches
                import hashlib
                hash_input = f"{user['user_id']}-{user['username']}"
                user_friend_code = f"{user['username'][:4].upper()}-{hashlib.md5(hash_input.encode()).hexdigest()[:6].upper()}"
                
                if user_friend_code == friend_code.upper():
                    # Found the user! Add them as friend
                    # For now, just return success - in a real app you'd manage a friends table
                    return user['username']
            
            return None  # Friend code not found
            
        except Exception as e:
            print(f"Error adding friend: {e}")
            return None

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