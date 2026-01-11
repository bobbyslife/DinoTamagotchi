#!/usr/bin/env python3

"""
Quick Supabase connection test for Dino Tamagotchi
Run this to verify your database setup is working
"""

from supabase import create_client, Client
import traceback

# Your Supabase credentials
SUPABASE_URL = "https://vcclceadrxrswxaxiitj.supabase.co"
SUPABASE_KEY = "sb_publishable_1SGzjoZCE65W6cNRU0_K4Q_CQTXYbCT"

def test_connection():
    print("🦕 Testing Supabase connection for Dino Tamagotchi...")
    
    try:
        # Create client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client created successfully")
        
        # Test basic connection
        result = supabase.table('users').select('*').limit(1).execute()
        print(f"✅ Connection successful! Found {len(result.data)} users")
        
        if len(result.data) > 0:
            print("📊 Sample user data:")
            for user in result.data:
                print(f"  - {user.get('username', 'Unknown')} (Health: {user.get('health', 0)}%)")
        
        # Test creating a new user
        test_user_id = "test_12345"
        test_username = "TestDino_001"
        
        print(f"\n🧪 Testing user creation with ID: {test_user_id}")
        
        # Try to insert/update test user
        user_data = {
            'user_id': test_user_id,
            'username': test_username,
            'health': 100,
            'dumplings': 0,
            'current_state': 'idle'
        }
        
        result = supabase.table('users').upsert(user_data).execute()
        print("✅ User creation/update successful!")
        
        # Test fetching the user back
        result = supabase.table('users').select('*').eq('user_id', test_user_id).execute()
        if result.data:
            print(f"✅ User retrieved: {result.data[0]['username']}")
        
        print("\n🎉 All tests passed! Your Supabase setup is working correctly.")
        print("You can now run the Dino Tamagotchi app and it will sync with the database.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n🛠️ To fix this, you need to:")
        print("1. Go to https://supabase.com/dashboard/projects")
        print("2. Open your project")
        print("3. Go to SQL Editor")
        print("4. Run the SQL from supabase_schema.sql")
        print("\nTraceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()