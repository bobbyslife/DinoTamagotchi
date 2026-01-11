#!/usr/bin/env python3
"""
Remote Config Update Tool for Dino Tamagotchi
Use this to update dumpling rates and website categories remotely
"""

from supabase import create_client, Client
import json

# Your Supabase credentials  
SUPABASE_URL = "https://vcclceadrxrswxaxiitj.supabase.co"
SUPABASE_KEY = "sb_publishable_1SGzjoZCE65W6cNRU0_K4Q_CQTXYbCT"

def update_dumpling_rates():
    """Update dumpling rates remotely"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Example: Boost coding rewards for a productivity week!
    new_rates = {
        "base_rates": {
            "coding": 2.5,      # Increased from 2.0
            "working": 1.0,
            "designing": 2.0,    # Increased from 1.5 
            "learning": 1.8,
            "productivity": 1.2,
            "communication": 0.8,
            "research": 1.0,
            "browsing_productive": 1.0,
            "idle": 0.0,
            "eating": 0.0,
            "social": -0.2,
            "news": -0.1,
            "entertainment": -0.3,
            "gaming": -0.4,
            "shopping": -0.15
        },
        "multipliers": {
            "high_health": 1.2,
            "low_health": 0.8,
            "streak_bonus": 1.1
        }
    }
    
    try:
        result = supabase.table('app_config').update({
            'config_value': new_rates
        }).eq('config_key', 'dumpling_rates').execute()
        
        print("✅ Dumpling rates updated!")
        print("🎯 Coding now earns 2.5 dumplings/min (was 2.0)")
        print("🎨 Designing now earns 2.0 dumplings/min (was 1.5)")
        print("📱 All existing users will get these updates automatically!")
        
    except Exception as e:
        print(f"❌ Error updating rates: {e}")

def add_new_website_category():
    """Add a new website category (example: AI tools)"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get current categories
    try:
        result = supabase.table('app_config').select('config_value').eq('config_key', 'website_categories').execute()
        
        if result.data:
            categories = result.data[0]['config_value']
            
            # Add new AI category
            categories['ai_tools'] = {
                "domains": ["openai.com", "claude.ai", "chatgpt.com", "midjourney.com", "huggingface.co"],
                "keywords": ["ai", "gpt", "claude", "machine learning", "artificial intelligence"],
                "dumpling_rate": 1.8,  # Good productivity tool
                "emoji": "🤖"
            }
            
            # Update in database
            update_result = supabase.table('app_config').update({
                'config_value': categories
            }).eq('config_key', 'website_categories').execute()
            
            print("✅ Added new AI Tools category!")
            print("🤖 AI websites now earn 1.8 dumplings/min")
            print("📱 Users will get this update automatically!")
            
        else:
            print("❌ No existing categories found")
            
    except Exception as e:
        print(f"❌ Error adding category: {e}")

def show_current_config():
    """Show current remote configuration"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        result = supabase.table('app_config').select('config_key, version, updated_at').execute()
        
        print("📋 Current Remote Configuration:")
        print("=" * 40)
        for config in result.data:
            key = config['config_key']
            version = config['version']
            updated = config['updated_at']
            print(f"{key}: v{version} (updated: {updated[:10]})")
            
    except Exception as e:
        print(f"❌ Error fetching config: {e}")

if __name__ == "__main__":
    print("🦕 Dino Tamagotchi Remote Config Tool")
    print("=" * 40)
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Show current config")
        print("2. Update dumpling rates (boost productivity!)")
        print("3. Add AI Tools category")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            show_current_config()
        elif choice == "2":
            update_dumpling_rates()
        elif choice == "3":
            add_new_website_category()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")