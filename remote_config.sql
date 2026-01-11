-- Remote Configuration System for Dino Tamagotchi
-- Add this to your Supabase database to enable remote config updates

-- Configuration table for remote updates
CREATE TABLE IF NOT EXISTS app_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS for app_config
ALTER TABLE app_config ENABLE ROW LEVEL SECURITY;

-- Public read access for all users
CREATE POLICY "Public read access to config" ON app_config
    FOR SELECT USING (true);

-- Insert default configuration values
INSERT INTO app_config (config_key, config_value, version) VALUES 
(
    'website_categories', 
    '{
        "coding": {
            "domains": ["github.com", "gitlab.com", "bitbucket.org", "stackoverflow.com", "codepen.io", "replit.com"],
            "keywords": ["code", "repository", "commit", "pull request", "api"],
            "dumpling_rate": 2.0,
            "emoji": "💻"
        },
        "learning": {
            "domains": ["docs.", "developer.", "learn.", "coursera.com", "udemy.com", "khanacademy.org", "pluralsight.com"],
            "keywords": ["documentation", "tutorial", "learn", "course", "guide", "training"],
            "dumpling_rate": 1.8,
            "emoji": "📚"
        },
        "designing": {
            "domains": ["figma.com", "sketch.com", "adobe.com", "dribbble.com", "behance.net", "canva.com"],
            "keywords": ["design", "ui", "ux", "prototype", "mockup", "wireframe"],
            "dumpling_rate": 1.5,
            "emoji": "🎨"
        },
        "productivity": {
            "domains": ["notion.so", "trello.com", "asana.com", "monday.com", "linear.app", "todoist.com"],
            "keywords": ["task", "project", "todo", "organize", "planning"],
            "dumpling_rate": 1.2,
            "emoji": "📋"
        },
        "communication": {
            "domains": ["gmail.com", "outlook.com", "slack.com", "discord.com", "zoom.us", "teams.microsoft.com"],
            "keywords": ["email", "message", "meeting", "call", "chat"],
            "dumpling_rate": 0.8,
            "emoji": "💼"
        },
        "research": {
            "domains": ["wikipedia.org", "scholar.google.com", "medium.com", "dev.to", "hashnode.com"],
            "keywords": ["research", "article", "paper", "study", "analysis"],
            "dumpling_rate": 1.0,
            "emoji": "🔍"
        },
        "social": {
            "domains": ["twitter.com", "x.com", "facebook.com", "instagram.com", "reddit.com", "tiktok.com", "linkedin.com"],
            "keywords": ["social", "post", "feed", "comment", "like", "share"],
            "dumpling_rate": -0.2,
            "emoji": "📱"
        },
        "news": {
            "domains": ["news.", "cnn.com", "bbc.com", "nytimes.com", "techcrunch.com", "ycombinator.com", "hackernews"],
            "keywords": ["news", "article", "breaking", "headlines"],
            "dumpling_rate": -0.1,
            "emoji": "📰"
        },
        "entertainment": {
            "domains": ["youtube.com", "netflix.com", "twitch.tv", "spotify.com", "hulu.com", "disney.com"],
            "keywords": ["video", "music", "stream", "watch", "movie", "show"],
            "dumpling_rate": -0.3,
            "emoji": "🍿"
        },
        "gaming": {
            "domains": ["steam.com", "twitch.tv/directory/game", "itch.io", "epicgames.com"],
            "keywords": ["game", "gaming", "play", "level", "achievement"],
            "dumpling_rate": -0.4,
            "emoji": "🎮"
        },
        "shopping": {
            "domains": ["amazon.com", "ebay.com", "etsy.com", "shopify.com", "target.com", "walmart.com"],
            "keywords": ["shop", "buy", "cart", "checkout", "purchase", "deal"],
            "dumpling_rate": -0.15,
            "emoji": "🛒"
        }
    }',
    1
),
(
    'dumpling_rates',
    '{
        "base_rates": {
            "coding": 2.0,
            "working": 1.0,
            "designing": 1.5,
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
    }',
    1
),
(
    'app_settings',
    '{
        "min_app_version": "1.0",
        "update_interval_minutes": 60,
        "notification_cooldown_minutes": 30,
        "daily_reset_hour": 0,
        "features": {
            "multiplayer": true,
            "website_tracking": true,
            "social_notifications": true
        }
    }',
    1
)
ON CONFLICT (config_key) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_app_config_key ON app_config(config_key);
CREATE INDEX IF NOT EXISTS idx_app_config_version ON app_config(version);

-- Add update trigger
CREATE OR REPLACE FUNCTION update_config_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_app_config_updated_at 
    BEFORE UPDATE ON app_config
    FOR EACH ROW EXECUTE FUNCTION update_config_updated_at();