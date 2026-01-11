// Retro Dino Tamagotchi Website JavaScript
class RetroDinoWebsite {
    constructor() {
        this.supabaseUrl = 'https://vcclceadrxrswxaxiitj.supabase.co';
        this.supabaseKey = 'sb_publishable_1SGzjoZCE65W6cNRU0_K4Q_CQTXYbCT';
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.loadDinoData();
            this.updateStats();
            this.setupModalClose();
            
            // Update data every 30 seconds
            setInterval(() => {
                this.loadDinoData();
                this.updateStats();
            }, 30000);
        });
    }

    setupModalClose() {
        const closeBtn = document.querySelector('.close-btn');
        const modal = document.querySelector('.warning-modal');
        
        if (closeBtn && modal) {
            closeBtn.addEventListener('click', () => {
                modal.style.display = 'none';
            });
        }
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

        const dinoGrid = document.getElementById('retro-dino-grid');
        if (!dinoGrid) return;

        // Clear existing dinos except loading card
        dinoGrid.innerHTML = '';

        // Create dino cards
        users.forEach(user => {
            const dinoCard = this.createRetroDinoCard(user);
            dinoGrid.appendChild(dinoCard);
        });

        // If no users found, show fallback
        if (users.length === 0) {
            this.showFallbackDinos();
        }
    }

    createRetroDinoCard(user) {
        const card = document.createElement('div');
        card.className = 'retro-dino-card';

        // Determine dino emoji based on state
        const dinoEmoji = this.getDinoEmoji(user.current_state, user.health);
        
        // Check if user is online (active in last 30 minutes)
        const isOnline = this.isRecentActivity(user.last_activity);
        const onlineStatus = isOnline ? 'ONLINE' : 'OFFLINE';
        
        // Format activity
        const activity = this.formatActivity(user.current_state);
        const health = Math.round(user.health || 100);
        const dumplings = Math.round(user.session_dumplings || 0);

        card.innerHTML = `
            <div class="retro-dino-emoji">${dinoEmoji}</div>
            <div class="retro-dino-name">${user.username || 'ANONYMOUS DINO'}</div>
            <div class="retro-dino-status">${onlineStatus} • ${activity.toUpperCase()}</div>
            <div class="retro-dino-stats">HP: ${health}% • DUMPLINGS: ${dumplings}</div>
        `;

        return card;
    }

    getDinoEmoji(state, health) {
        // Map states to emojis
        const stateEmojis = {
            'coding': '🦕',
            'working': '🦖',
            'designing': '🦕',
            'browsing_productive': '🦕',
            'browsing_social': '🦖',
            'browsing_news': '🦖',
            'browsing_entertainment': '🦖',
            'browsing_shopping': '🦖',
            'gaming': '🦕',
            'eating': '🦕',
            'sick': '🤒',
            'idle': '😴'
        };

        // If health is very low, show sick dino
        if (health && health < 20) {
            return '🤒';
        }

        return stateEmojis[state] || '🦕';
    }

    formatActivity(state) {
        const activityNames = {
            'coding': 'coding',
            'working': 'working', 
            'designing': 'designing',
            'browsing_productive': 'learning',
            'browsing_social': 'social media',
            'browsing_news': 'reading news',
            'browsing_entertainment': 'entertainment',
            'browsing_shopping': 'shopping',
            'gaming': 'gaming',
            'eating': 'feeding',
            'idle': 'idle'
        };

        return activityNames[state] || 'unknown';
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
        
        // Update DOM
        this.updateStatElement('total-dinos', totalDinos);
        this.updateStatElement('total-dumplings', `${Math.round(totalDumplings)}`);
    }

    updateStatElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    showFallbackDinos() {
        const dinoGrid = document.getElementById('retro-dino-grid');
        if (!dinoGrid) return;

        dinoGrid.innerHTML = `
            <div class="retro-dino-card">
                <div class="retro-dino-emoji">🦕</div>
                <div class="retro-dino-name">BOBBY (CREATOR)</div>
                <div class="retro-dino-status">ONLINE • BUILDING</div>
                <div class="retro-dino-stats">HP: 100% • DUMPLINGS: 156</div>
            </div>
            <div class="retro-dino-card">
                <div class="retro-dino-emoji">🦖</div>
                <div class="retro-dino-name">YOUR DINO</div>
                <div class="retro-dino-status">JOIN THE GAME!</div>
                <div class="retro-dino-stats">DOWNLOAD TO START</div>
            </div>
        `;
    }

    showFallbackStats() {
        // Show realistic data
        this.updateStatElement('total-dinos', '1');
        this.updateStatElement('total-dumplings', '156');
    }
}

// Download function
function downloadApp() {
    const downloadUrl = 'Dino-Tamagotchi-macOS.zip';
    
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = 'Dino-Tamagotchi-macOS.zip';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Show retro download message
    alert(`🦕 DOWNLOAD STARTED!

SUPER EASY INSTALL:
1. UNZIP THE FILE
2. DOUBLE-CLICK "🦕 Install Dino Tamagotchi.command"
3. FOLLOW THE PROMPTS
4. YOUR DINO APPEARS IN MENU BAR!

NO TERMINAL NEEDED!`);
}

// Initialize the retro website
new RetroDinoWebsite();