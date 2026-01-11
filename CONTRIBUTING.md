# Contributing to Dino Tamagotchi 🦕

Thank you for your interest in contributing to Dino Tamagotchi! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- macOS 10.15+ (for development and testing)
- Python 3.7+
- Git
- Google Chrome (for website tracking features)

### Development Setup
1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/DinoTamagotchi.git
   cd DinoTamagotchi
   ```
3. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```
4. Set up Supabase (see README for details)
5. Test the app: `python3 supabase_dino.py`

## 🎯 Ways to Contribute

### 🐛 Bug Reports
- Use GitHub Issues with the "bug" label
- Include macOS version, Python version, and error messages
- Provide steps to reproduce the issue
- Include relevant log output

### 💡 Feature Requests
- Use GitHub Discussions for feature ideas
- Explain the use case and benefits
- Consider implementation complexity

### 🔧 Code Contributions
- Check open issues for "good first issue" label
- Comment on issues you want to work on
- Follow the coding standards below

## 📝 Coding Standards

### Python Style
- Follow PEP 8 guidelines
- Use descriptive variable and function names
- Add docstrings for all classes and functions
- Keep functions focused and under 50 lines when possible

### Code Structure
```python
def example_function(param1, param2):
    """
    Brief description of what this function does.
    
    Args:
        param1 (str): Description of param1
        param2 (int): Description of param2
        
    Returns:
        bool: Description of return value
    """
    # Implementation here
    return result
```

### Comments
- Use comments to explain WHY, not WHAT
- Keep comments up to date with code changes
- Use TODO comments for future improvements

## 🏗️ Project Structure

```
DinoTamagotchi/
├── supabase_dino.py          # Main application (primary file)
├── supabase_schema.sql       # Database schema
├── website_tracking_dino.py  # Website tracking implementation
├── dumpling_currency_dino.py # Currency system
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
└── CONTRIBUTING.md          # This file
```

## 🔄 Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number
```

### 2. Make Your Changes
- Write code following the style guidelines
- Add appropriate comments and docstrings
- Test your changes thoroughly

### 3. Test Your Changes
- Run the app: `python3 supabase_dino.py`
- Test all affected features
- Ensure no existing functionality breaks

### 4. Commit Your Changes
```bash
git add .
git commit -m "Add feature: brief description

- Detailed explanation of changes
- Any breaking changes
- Related issue numbers (#123)"
```

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```
Then create a Pull Request on GitHub.

## 🎨 UI/UX Guidelines

### Menu Bar Design
- Keep menu items concise and readable
- Use emojis consistently for visual clarity
- Group related items with separators
- Maintain the playful Tamagotchi theme

### Notifications
- Make notifications informative but not annoying
- Use appropriate icons and urgency levels
- Respect user notification preferences

## 🗄️ Database Guidelines

### Supabase Schema
- All schema changes must be backward compatible
- Add migration scripts for schema updates
- Document new tables and columns
- Follow PostgreSQL naming conventions

### Data Privacy
- Never log sensitive information
- Respect user privacy in all data collection
- Follow data minimization principles

## 🧪 Testing

### Manual Testing
- Test on different macOS versions when possible
- Verify all notification scenarios work
- Test with different Chrome tab configurations
- Ensure multiplayer features work with multiple users

### Areas Needing Tests
We welcome contributions for automated testing:
- Unit tests for core functions
- Integration tests for Supabase
- UI automation tests
- Performance tests

## 📊 Performance Guidelines

- Keep background monitoring lightweight
- Minimize AppleScript calls
- Use appropriate threading for background tasks
- Optimize database queries

## 🎯 Priority Areas for Contribution

### High Priority
1. **Browser Support** - Add Safari, Firefox, Edge tracking
2. **Error Handling** - Improve robustness and user feedback
3. **Performance** - Optimize resource usage
4. **Testing** - Add automated tests

### Medium Priority
1. **UI Improvements** - Better menu design and animations
2. **Analytics** - Advanced productivity insights
3. **Mobile App** - iOS/Android companion
4. **Integrations** - Slack, Discord, Notion

### Future Ideas
1. **Team Features** - Group challenges and competitions
2. **Customization** - Dino skins, themes, sounds
3. **AI Features** - Smart productivity suggestions
4. **Gamification** - Achievements, streaks, levels

## 💬 Communication

### Getting Help
- GitHub Discussions for questions and ideas
- GitHub Issues for bugs and feature requests
- Comment on issues before starting work

### Code Reviews
- All PRs require review before merging
- Be respectful and constructive in reviews
- Address feedback promptly
- Test suggestions when provided

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributor graphs

## 📞 Questions?

Feel free to:
- Open a GitHub Discussion
- Comment on relevant issues
- Reach out to maintainers

Thank you for helping make Dino Tamagotchi awesome! 🦕✨