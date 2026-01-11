-- Supabase Database Schema for Multiplayer Dino Tamagotchi
-- Run this in your Supabase SQL editor to set up the required tables

-- Users table to store user profiles and stats
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    dumplings DECIMAL(10,2) DEFAULT 0,
    total_dumplings_earned DECIMAL(10,2) DEFAULT 0,
    health INTEGER DEFAULT 100,
    happiness INTEGER DEFAULT 50,
    energy INTEGER DEFAULT 50,
    current_state VARCHAR(50) DEFAULT 'idle',
    productive_time_today INTEGER DEFAULT 0,
    session_dumplings DECIMAL(10,2) DEFAULT 0,
    coding_time_today INTEGER DEFAULT 0,
    social_media_time_today INTEGER DEFAULT 0,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Activities table to log user activities for friends to see
CREATE TABLE IF NOT EXISTS activities (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,
    dumplings_earned DECIMAL(10,2) DEFAULT 0,
    duration_minutes DECIMAL(10,2) DEFAULT 0,
    website_category VARCHAR(50),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Friends table for friend relationships (optional for future use)
CREATE TABLE IF NOT EXISTS friends (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    friend_user_id VARCHAR(50) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, blocked
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, friend_user_id)
);

-- Custom website categories table (optional for syncing across devices)
CREATE TABLE IF NOT EXISTS custom_website_categories (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    domain VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, domain)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS idx_users_last_activity ON users(last_activity);
CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id);
CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON activities(timestamp);
CREATE INDEX IF NOT EXISTS idx_friends_user_id ON friends(user_id);
CREATE INDEX IF NOT EXISTS idx_custom_categories_user_id ON custom_website_categories(user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE friends ENABLE ROW LEVEL SECURITY;
ALTER TABLE custom_website_categories ENABLE ROW LEVEL SECURITY;

-- Create policies for users table (users can read all, update only their own)
CREATE POLICY "Users can view all profiles" ON users
    FOR SELECT USING (true);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (true);

CREATE POLICY "Users can insert own profile" ON users
    FOR INSERT WITH CHECK (true);

-- Create policies for activities table (users can read all, insert only their own)
CREATE POLICY "Users can view all activities" ON activities
    FOR SELECT USING (true);

CREATE POLICY "Users can insert own activities" ON activities
    FOR INSERT WITH CHECK (true);

-- Create policies for friends table
CREATE POLICY "Users can manage own friendships" ON friends
    FOR ALL USING (true);

-- Create policies for custom website categories
CREATE POLICY "Users can manage own categories" ON custom_website_categories
    FOR ALL USING (true);

-- Add updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add trigger to users table
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sample data (optional - remove if you don't want test data)
-- INSERT INTO users (user_id, username) VALUES 
--     ('demo1234', 'DemoUser_demo'),
--     ('test5678', 'TestUser_test')
-- ON CONFLICT (user_id) DO NOTHING;

-- Grant necessary permissions (adjust as needed)
-- GRANT ALL ON users TO authenticated;
-- GRANT ALL ON activities TO authenticated;
-- GRANT ALL ON friends TO authenticated;
-- GRANT ALL ON custom_website_categories TO authenticated;