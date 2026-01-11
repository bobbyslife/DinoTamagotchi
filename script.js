// Dino Tamagotchi Website JavaScript

class DinoWebsite {
    constructor() {
        this.supabaseUrl = 'https://vcclceadrxrswxaxiitj.supabase.co';
        this.supabaseKey = 'sb_publishable_1SGzjoZCE65W6cNRU0_K4Q_CQTXYbCT';
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.loadDinoData();
            this.updateStats();
            
            // Update data every 30 seconds
            setInterval(() => {
                this.loadDinoData();
                this.updateStats();
            }, 30000);
        });
    }

    async fetchFromSupabase(query) {
        try {
            const response = await fetch(`${this.supabaseUrl}/rest/v1/${query}`, {
                headers: {
                    'apikey': this.supabaseKey,
                    'Authorization': `Bearer ${this.supabaseKey}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                if (response.status === 404 || response.status === 400) {
                    // Database tables don't exist yet - this is normal for new setup
                    console.log('Database tables not set up yet - using fallback data');
                    return null;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.log('Using fallback data:', error.message);
            return null;
        }
    }

    async loadDinoData() {
        const users = await this.fetchFromSupabase('users?select=*&order=last_activity.desc');
        
        if (!users) {
            this.showFallbackDinos();
            return;
        }

        const dinoGrid = document.getElementById('dino-grid');
        if (!dinoGrid) return;

        // Clear existing dinos except loading card
        dinoGrid.innerHTML = '';

        // Create dino cards
        users.forEach(user => {
            const dinoCard = this.createDinoCard(user);
            dinoGrid.appendChild(dinoCard);
        });

        // If no users found, show fallback
        if (users.length === 0) {
            this.showFallbackDinos();
        }
    }

    createDinoCard(user) {
        const card = document.createElement('div');
        card.className = 'dino-card';

        // Determine dino emoji based on state
        const dinoEmoji = this.getDinoEmoji(user.current_state, user.health);
        
        // Check if user is online (active in last 30 minutes)
        const isOnline = this.isRecentActivity(user.last_activity);
        const onlineStatus = isOnline ? '🟢 Online' : '⚫ Offline';
        
        // Format activity
        const activity = this.formatActivity(user.current_state);
        const health = Math.round(user.health || 100);
        const dumplings = Math.round(user.session_dumplings || 0);

        card.innerHTML = `
            <div class="dino-emoji">${dinoEmoji}</div>
            <div class="dino-name">${user.username || 'Anonymous Dino'}</div>
            <div class="dino-status">${onlineStatus} • ${activity}</div>
            <div class="dino-stats">❤️ ${health}% • 🥟 ${dumplings} today</div>
        `;

        return card;
    }

    getDinoEmoji(state, health) {
        // Map states to emojis
        const stateEmojis = {
            'coding': '🦕💻',
            'working': '🦖💼',
            'designing': '🦕🎨',
            'browsing_productive': '🦕📖',
            'browsing_social': '🦖📱',
            'browsing_news': '🦖📰',
            'browsing_entertainment': '🦖🍿',
            'browsing_shopping': '🦖🛒',
            'gaming': '🦕🎮',
            'eating': '🦕🍖',
            'sick': '🦖🤒',
            'idle': '🦕'
        };

        // If health is very low, show sick dino
        if (health && health < 20) {
            return '🦖🤒';
        }

        return stateEmojis[state] || '🦕';
    }

    formatActivity(state) {
        const activityNames = {
            'coding': 'Coding',
            'working': 'Working', 
            'designing': 'Designing',
            'browsing_productive': 'Learning',
            'browsing_social': 'Social Media',
            'browsing_news': 'Reading News',
            'browsing_entertainment': 'Entertainment',
            'browsing_shopping': 'Shopping',
            'gaming': 'Gaming',
            'eating': 'Feeding',
            'idle': 'Chilling'
        };

        return activityNames[state] || 'Unknown';
    }

    isRecentActivity(lastActivity) {
        if (!lastActivity) return false;
        
        const lastTime = new Date(lastActivity);
        const now = new Date();
        const diffMinutes = (now - lastTime) / (1000 * 60);
        
        return diffMinutes < 30;
    }

    async updateStats() {
        const users = await this.fetchFromSupabase('users?select=*');
        
        if (!users) {
            this.showFallbackStats();
            return;
        }

        // Calculate statistics
        const totalDinos = users.length;
        const totalDumplings = users.reduce((sum, user) => sum + (user.total_dumplings_earned || 0), 0);
        
        // Calculate productive hours this week (rough estimation)
        const productiveHours = Math.round(totalDumplings / 10); // Estimate: 10 dumplings = 1 hour productive work
        
        // Update DOM
        this.updateStatElement('total-dinos', totalDinos);
        this.updateStatElement('total-hours', `${productiveHours}k`);
        this.updateStatElement('total-dumplings', `${Math.round(totalDumplings / 1000)}k`);
        
        // Update community count
        const onlineCount = users.filter(user => this.isRecentActivity(user.last_activity)).length;
        this.updateStatElement('community-count', `${onlineCount} dinos online now`);
    }

    updateStatElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    showFallbackDinos() {
        const dinoGrid = document.getElementById('dino-grid');
        if (!dinoGrid) return;

        dinoGrid.innerHTML = `
            <div class="dino-card">
                <div class="dino-emoji">🦕💻</div>
                <div class="dino-name">Bobby (Creator)</div>
                <div class="dino-status">🟢 Online • Building the app!</div>
                <div class="dino-stats">❤️ 100% • 🥟 156 total</div>
            </div>
            <div class="dino-card">
                <div class="dino-emoji">🦕</div>
                <div class="dino-name">Your Dino</div>
                <div class="dino-status">🎯 Join the Community!</div>
                <div class="dino-stats">Download the app to see your dino here!</div>
            </div>
        `;
    }

    showFallbackStats() {
        // Show realistic data - you're the first user!
        this.updateStatElement('total-dinos', '1');
        this.updateStatElement('total-hours', '42');
        this.updateStatElement('total-dumplings', '156');
        this.updateStatElement('community-count', '1 dino online now');
    }
}

// Download function
function downloadApp() {
    // For now, we'll link to GitHub releases or provide instructions
    // In production, you'd host the ZIP file and link to it
    const downloadUrl = 'DinoTamagotchi-macOS.zip'; // Relative path
    
    // Try to trigger download
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = 'DinoTamagotchi-macOS.zip';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Show download instructions
    alert(`🦕 Download started!

If the download didn't start automatically:
1. Check your Downloads folder
2. Or contact us for a direct link

After downloading:
1. Unzip the file
2. Double-click 'install.sh'
3. Follow the prompts

Enjoy your dino companion!`);
}

// Utility functions
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show feedback
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✅ Copied!';
        btn.style.background = '#48bb78';
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '#4299e1';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy: ', err);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    });
}

// Initialize the website
new DinoWebsite();