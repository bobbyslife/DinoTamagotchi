# 🦕 Dino Tamagotchi

A multiplayer macOS menu bar Tamagotchi featuring a cute dinosaur that reacts to your productivity and competes with friends in real-time!

![Dino Tamagotchi Demo](https://img.shields.io/badge/macOS-Menu%20Bar%20App-blue) ![Python](https://img.shields.io/badge/Python-3.7+-green) ![Supabase](https://img.shields.io/badge/Database-Supabase-purple)

## ✨ Features

### 🎮 Core Tamagotchi Mechanics
- **Health, Happiness, and Energy** stats that change based on your activities
- **Feed, Pet, and Care** for your dino using earned dumplings
- **Dynamic states** - dino changes appearance based on what you're doing

### 💰 Dumpling Currency System
- **Earn dumplings** for productive activities:
  - 💻 Coding: +2.0/min
  - 💼 Working: +0.8/min  
  - 📖 Learning: +1.0/min
- **Lose dumplings** for distracting activities:
  - 📱 Social Media: -0.2/min
  - 🍿 Entertainment: -0.3/min
  - 🛒 Shopping: -0.15/min

### 🌐 Smart Website Tracking
- **Real-time Chrome tab detection** with AppleScript integration
- **Automatic website categorization** (productive, social, entertainment, etc.)
- **Custom categorization prompts** for unknown websites
- **Persistent learning** - remembers your categorizations

### 👥 Real-time Multiplayer
- **Live leaderboards** powered by Supabase
- **Social pressure notifications** when friends outperform you
- **Achievement alerts** for friend milestones
- **Real-time activity sharing** across all connected users

### 📊 Activity Tracking
- **Time tracking** for all activities (coding, working, browsing)
- **Session statistics** with detailed breakdowns
- **Productivity insights** and dumpling earning history

## 🚀 Quick Start

### Prerequisites
- macOS 10.15+ (Catalina or later)
- Python 3.7+
- Google Chrome (for website tracking)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/DinoTamagotchi.git
   cd DinoTamagotchi
   ```

2. **Install dependencies:**
   ```bash
   pip3 install rumps supabase
   ```

3. **Set up Supabase database:**
   - Create a new project at [supabase.com](https://supabase.com)
   - Run the SQL from `supabase_schema.sql` in your Supabase SQL editor
   - Update credentials in `supabase_dino.py` (lines 21-22)

4. **Enable notifications:**
   ```bash
   /usr/libexec/PlistBuddy -c 'Add :CFBundleIdentifier string "rumps"' /Users/$(whoami)/anaconda3/bin/Info.plist
   ```

5. **Run the app:**
   ```bash
   python3 supabase_dino.py
   ```

## 📱 Usage

1. **Your dino appears in the menu bar** - click to see stats and controls
2. **Browse websites** - dino automatically detects and categorizes them
3. **Earn dumplings** through productive work
4. **Compete with friends** by sharing your User ID
5. **Get notifications** for achievements and social pressure

## 🗂️ File Structure

- `supabase_dino.py` - **Main app** with full multiplayer features
- `supabase_schema.sql` - **Database schema** for Supabase setup
- `website_tracking_dino.py` - **Enhanced website tracking** version
- `dumpling_currency_dino.py` - **Currency system** implementation
- `multiplayer_dino.py` - **Local multiplayer** prototype

## 🛠️ Development

### Code Architecture
- **rumps** - macOS menu bar app framework
- **AppleScript** - Chrome integration for URL detection
- **Supabase** - Real-time multiplayer database
- **Threading** - Background monitoring and sync

### Key Components
1. **Activity Detection** (`detect_current_activity`) - Monitors active apps and websites
2. **Website Categorization** (`categorize_website`) - Smart URL classification
3. **Dumpling System** (`calculate_dumpling_earnings`) - Productivity-based rewards
4. **Social Features** (`check_competitive_updates`) - Real-time friend competition
5. **Notifications** (`send_native_notification`) - Native macOS alerts

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📊 Database Schema

The app uses Supabase PostgreSQL with these tables:
- **users** - User profiles, stats, and dumplings
- **activities** - Activity logs for social features
- **friends** - Friend relationships
- **custom_website_categories** - User-defined site categories

## 🔧 Configuration

### Supabase Setup
Replace these in `supabase_dino.py`:
```python
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

### Website Categories
Customize dumpling rates in the `website_categories` dictionary:
```python
'productive': {
    'domains': ['github.com', 'stackoverflow.com'],
    'dumpling_rate': 1.0,  # Dumplings per minute
    'emoji': '📖'
}
```

## 🎯 Roadmap

- [ ] **Safari support** for website tracking
- [ ] **Team challenges** and group competitions
- [ ] **Daily/weekly quests** for bonus dumplings
- [ ] **Dino customization** with earned rewards
- [ ] **Mobile companion app** for iOS
- [ ] **Slack/Discord integrations** for team productivity
- [ ] **Advanced analytics** and productivity insights

## 🤝 Contributing

We welcome contributions! Areas where you can help:

- **🌐 Browser Support** - Add Firefox, Safari, Edge website tracking
- **📱 Mobile App** - iOS/Android companion apps
- **🎨 UI/UX** - Better menu design and animations  
- **📊 Analytics** - Advanced productivity insights
- **🔌 Integrations** - Slack, Discord, Notion, etc.
- **🧪 Testing** - Unit tests and CI/CD setup
- **📚 Documentation** - Tutorials and guides

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **rumps** library for macOS menu bar integration
- **Supabase** for real-time multiplayer backend
- **AppleScript** for seamless Chrome integration
- The **Tamagotchi** concept for inspiration

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/DinoTamagotchi/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/yourusername/DinoTamagotchi/discussions)
- 💬 **Community**: Join our Discord server

---

**Made with ❤️ for productive developers who need a cute dino companion!** 🦕✨