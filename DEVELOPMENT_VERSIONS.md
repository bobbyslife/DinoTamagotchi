# Development Versions 📁

This document tracks the evolution of the Dino Tamagotchi app through various development iterations.

## 🗂️ File Versions in this Repository

### Core Applications
- `supabase_dino.py` - **[MAIN APP]** Full-featured multiplayer version with Supabase
- `website_tracking_dino.py` - Enhanced website tracking implementation  
- `dumpling_currency_dino.py` - Currency system implementation
- `multiplayer_dino.py` - Local multiplayer prototype

### Development Iterations
- `dino_tamagotchi.py` - Original basic version
- `enhanced_dino_tamagotchi.py` - Early enhanced version
- `simple_working_dino.py` - Simplified stable version
- `notification_enhanced_dino.py` - Added notification features
- `dock_dino_tamagotchi.py` - Dock integration attempt
- `fixed_dock_dino.py` - Fixed dock version

### Configuration & Setup
- `supabase_schema.sql` - Complete database schema
- `config.template.py` - Configuration template
- `main.swift` - Early Swift attempt (deprecated)

## 🚀 Recommended Usage

**For Production**: Use `supabase_dino.py` - it includes all features:
- Real-time multiplayer with Supabase
- Smart website categorization 
- Dumpling currency system
- Social pressure notifications
- Activity tracking and leaderboards

**For Development**: Reference other versions for specific features:
- Website tracking logic → `website_tracking_dino.py`
- Currency mechanics → `dumpling_currency_dino.py`  
- Multiplayer concepts → `multiplayer_dino.py`

## 🔄 Migration Path

If you're upgrading from an older version:

1. **Backup your data**: `~/.dino_tamagotchi/`
2. **Install dependencies**: `pip3 install -r requirements.txt`
3. **Set up Supabase**: Run `supabase_schema.sql`
4. **Configure**: Copy `config.template.py` → `config.py`
5. **Run**: `python3 supabase_dino.py`

## 📊 Feature Matrix

| Feature | Basic | Enhanced | Currency | Website | Multiplayer | Supabase |
|---------|-------|----------|----------|---------|-------------|----------|
| Menu Bar | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Notifications | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Activity Detection | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Website Tracking | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Dumpling System | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Categorization | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Local Multiplayer | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| Real-time Multiplayer | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Social Pressure | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Database Sync | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

## 🎯 Current Focus: supabase_dino.py

The main application now includes everything:
- **Lines 20-29**: Supabase configuration with fallback
- **Lines 646-690**: Real-time activity detection  
- **Lines 752-791**: Smart website categorization
- **Lines 793-868**: Interactive categorization prompts
- **Lines 957-990**: Dumpling earning system
- **Lines 324-421**: Social pressure notifications

All other files are preserved for reference and potential feature extraction.

---

*This structure allows contributors to understand the project evolution and choose the right starting point for their contributions.*