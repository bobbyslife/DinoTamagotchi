# 🔄 Remote Configuration System

The Dino Tamagotchi app now supports **remote configuration updates**, allowing you to update dumpling rates and website categories **without users needing to re-download the app**!

## 🚀 How It Works

1. **Database Setup**: Configuration is stored in Supabase `app_config` table
2. **Auto-Updates**: Apps check for config updates every hour
3. **Versioning**: Each config has a version number that increments on updates
4. **Live Updates**: Users get notifications when configs are updated

## 📋 Setup Instructions

### 1. Create Database Tables

Run this SQL in your Supabase SQL Editor:

```sql
-- Run the contents of remote_config.sql
```

### 2. Current Configuration Categories

The system manages three config types:

- **`website_categories`**: Website domains, keywords, and dumpling rates
- **`dumpling_rates`**: Base earning rates for each activity type  
- **`app_settings`**: Feature toggles and app behavior settings

## 🎯 Updating Configurations

### Option 1: Use the Update Tool

```bash
python3 update_config.py
```

Interactive tool to:
- View current configurations
- Update dumpling rates
- Add new website categories
- Manage app settings

### Option 2: Direct SQL Updates

Update dumpling rates:
```sql
UPDATE app_config 
SET config_value = '{
    "base_rates": {
        "coding": 2.5,      -- Increased from 2.0!
        "designing": 2.0,   -- Increased from 1.5!
        "learning": 1.8,
        ...
    }
}'::jsonb
WHERE config_key = 'dumpling_rates';
```

Add new website category:
```sql
-- Get current categories, modify JSON, then update
```

## 📱 User Experience

When you update configs:

1. **Automatic Detection**: Apps check every hour for updates
2. **Live Application**: New rates apply immediately  
3. **User Notification**: "🔄 Config Updated - Dumpling rates updated!"
4. **No Restart Required**: Changes apply in real-time

## 💡 Example Use Cases

### Productivity Boost Week
```python
# Increase coding rewards
"coding": 2.5,      # Was 2.0
"designing": 2.0,   # Was 1.5
```

### Add New Tools
```python
# Add AI tools category
"ai_tools": {
    "domains": ["openai.com", "claude.ai", "chatgpt.com"],
    "dumpling_rate": 1.8,
    "emoji": "🤖"
}
```

### Seasonal Events
```python
# Halloween: Reduce entertainment penalties
"entertainment": -0.1,  # Was -0.3 (more forgiving!)
```

## 🔧 Configuration Structure

### Website Categories
```json
{
    "category_name": {
        "domains": ["site1.com", "site2.com"],
        "keywords": ["keyword1", "keyword2"],
        "dumpling_rate": 1.5,
        "emoji": "🎨"
    }
}
```

### Dumpling Rates  
```json
{
    "base_rates": {
        "coding": 2.0,
        "designing": 1.5,
        ...
    },
    "multipliers": {
        "high_health": 1.2,
        "low_health": 0.8
    }
}
```

## 🎉 Benefits

- **No App Updates**: Users never need to re-download
- **Instant Changes**: Apply new rates across all users
- **A/B Testing**: Try different reward structures
- **Event Support**: Special rates for productivity challenges
- **Category Growth**: Add new tools as they become popular

Now you can evolve the dumpling economy and add new website categories without any user friction! 🚀