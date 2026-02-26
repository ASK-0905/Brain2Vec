// Load sample EEG data for testing
function loadSampleData() {
    const sampleData = Array(32).fill().map(() => 
        Array(500).fill().map(() => (Math.random() * 2 - 1).toFixed(4)).join(', ')
    ).join('\n');
    
    document.getElementById('eegInput').value = sampleData;
    showNotification('Sample data loaded successfully', 'success');
}

// Clear input
function clearInput() {
    document.getElementById('eegInput').value = '';
    document.getElementById('resultsSection').style.display = 'none';
}

// Show notification
function showNotification(message, type = 'info') {
    // Simple alert for now - can be enhanced with custom toast
    console.log(`${type.toUpperCase()}: ${message}`);
}

// Parse CSV input to array
function parseEEGInput(input) {
    const lines = input.trim().split('\n').filter(line => line.trim());

    // Parse all numeric values from all lines
    const rows = lines.map(line =>
        line.split(',').map(val => parseFloat(val.trim())).filter(v => !isNaN(v))
    ).filter(row => row.length > 0);

    // Flatten everything to a single array of numbers
    const flat = rows.flat();

    // If we have at least 32 values, reshape into frames of 32 (time x channels)
    // This prevents the "single time sample" bug where channels become constant
    if (flat.length >= 32) {
        const frames = [];
        const fullFrames = Math.floor(flat.length / 32);
        for (let i = 0; i < fullFrames; i++) {
            const start = i * 32;
            frames.push(flat.slice(start, start + 32));
        }
        return frames; // Each element is a time-sample with 32 channels
    }

    // Fallback: return parsed rows as-is
    return rows;
}

// Validate EEG data
function validateEEGData(data) {
    if (data.length === 0) {
        throw new Error('No valid data found. Please paste EEG values in CSV format.');
    }
    
    // Check if we have at least some channels
    const channels = data[0].length;
    if (channels < 10) {
        throw new Error(`Not enough channels detected (${channels}). Expected at least 32 channels.`);
    }
    
    // Pad to 32 channels if needed
    if (channels < 32) {
        data = data.map(row => {
            const padded = [...row];
            while (padded.length < 32) padded.push(0);
            return padded.slice(0, 32);
        });
    } else if (channels > 32) {
        data = data.map(row => row.slice(0, 32));
    }
    
    return data;
}

// Main analysis function
async function analyzeStress() {
    const input = document.getElementById('eegInput').value.trim();
    
    if (!input) {
        alert('Please paste your EEG data or load sample data first.');
        return;
    }
    
    try {
        // Show loading
        document.getElementById('loading').style.display = 'flex';
        document.getElementById('analyzeBtn').disabled = true;
        
        // Parse and validate
        let eegData = parseEEGInput(input);
        eegData = validateEEGData(eegData);
        
        // Transpose to (channels, time) format
        const transposed = eegData[0].map((_, colIndex) => 
            eegData.map(row => row[colIndex])
        );

        // Normalize time dimension to match model expectation (9600 samples)
        const TARGET_TIME = 9600;
        const normalized = transposed.map(channel => {
            const out = new Array(TARGET_TIME);
            const len = channel.length;
            for (let i = 0; i < TARGET_TIME; i++) {
                out[i] = channel[i % len];
            }
            return out;
        });
        
        // Send to backend
        const response = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ eeg: normalized })
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const result = await response.json();
        displayResults(result);
        
    } catch (error) {
        alert(`Error: ${error.message}`);
        console.error('Analysis error:', error);
    } finally {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('analyzeBtn').disabled = false;
    }
}

// Display results
function displayResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    const stressCard = document.getElementById('stressCard');
    const stressLevel = document.getElementById('stressLevel');
    const stressMessage = document.getElementById('stressMessage');
    const stressIcon = document.getElementById('stressIcon');
    const scoreValue = document.getElementById('scoreValue');
    const scoreFill = document.getElementById('scoreFill');
    const reliefSection = document.getElementById('reliefSection');
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Update stress level
    const score = result.score * 100;
    stressLevel.textContent = result.stress_level;
    scoreValue.textContent = `${score.toFixed(1)}%`;
    scoreFill.style.width = `${score}%`;
    
    // Set colors based on stress level
    stressCard.className = 'card result-card';
    if (result.stress_level === 'RELAXED') {
        stressCard.classList.add('relaxed');
        stressIcon.textContent = '😌';
        stressMessage.textContent = 'Your brain activity shows a relaxed state. Keep up the good work!';
    } else if (result.stress_level === 'MILD STRESS') {
        stressCard.classList.add('mild');
        stressIcon.textContent = '😐';
        stressMessage.textContent = result.relief?.message || 'Light stress detected. Consider taking a break.';
    } else {
        stressCard.classList.add('high');
        stressIcon.textContent = '😰';
        stressMessage.textContent = result.relief?.message || 'High stress detected. Please take time to relax.';
    }
    
    // Show relief recommendations if stress detected
    if (result.relief && result.stress) {
        reliefSection.style.display = 'block';
        displayMusic(result.relief.actions?.music);
        displayGames(result.relief.actions?.games);
    } else {
        reliefSection.style.display = 'none';
    }
}

// Display music recommendations
function displayMusic(musicList) {
    const musicGrid = document.getElementById('musicGrid');
    musicGrid.innerHTML = '';
    
    const cleaned = Array.isArray(musicList)
        ? musicList.filter(m => m && m.external_urls?.spotify)
        : [];

    if (!cleaned.length) {
        musicGrid.innerHTML = '<p class="empty-state">No music suggestions available right now.</p>';
        return;
    }

    cleaned.forEach(music => {
        const musicCard = document.createElement('div');
        musicCard.className = 'music-card';
        
        const imageUrl = music.images?.[0]?.url || 'https://via.placeholder.com/300x300/0a0e27/ffffff?text=Music';
        const playlistId = music.id;
        const embedUrl = playlistId
            ? `https://open.spotify.com/embed/playlist/${playlistId}?utm_source=generator`
            : music.external_urls.spotify;
        
        musicCard.innerHTML = `
            <div class="music-image">
                <img src="${imageUrl}" alt="${music.name}">
                <div class="music-overlay">
                    <a href="${music.external_urls?.spotify}" target="_blank" rel="noopener" class="play-btn">
                        ▶ Open in Spotify
                    </a>
                </div>
            </div>
            <div class="music-embed">
                <iframe src="${embedUrl}" width="100%" height="152" frameborder="0" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>
            </div>
            <div class="music-info">
                <h4 class="music-title">${music.name}</h4>
                <p class="music-owner">${music.owner?.display_name || 'Spotify'}</p>
                <p class="music-tracks">${music.tracks?.total || 0} tracks</p>
            </div>
        `;
        
        musicGrid.appendChild(musicCard);
    });
}

// Display game recommendations
function displayGames(gamesList) {
    const gamesGrid = document.getElementById('gamesGrid');
    gamesGrid.innerHTML = '';
    
    const defaults = [
        {
            name: 'Breathing Exercise',
            description: 'Guided box breathing to calm the nervous system.',
            action: 'breathing'
        },
        {
            name: 'Memory Match',
            description: 'Light concentration game to shift focus and reduce stress.',
            action: 'memory'
        },
        {
            name: 'Color Tap',
            description: 'Simple tapping game to reset attention quickly.',
            action: 'color'
        }
    ];

    const cleaned = Array.isArray(gamesList) && gamesList.length
        ? gamesList
        : defaults;
    const resolveAction = (game) => {
        if (game.action) return game.action;
        const name = (game.name || '').toLowerCase();
        if (name.includes('breath')) return 'breathing';
        if (name.includes('memory') || name.includes('match')) return 'memory';
        if (name.includes('color') || name.includes('tap')) return 'color';
        return null;
    };

    cleaned.forEach(game => {
        const gameCard = document.createElement('div');
        gameCard.className = 'game-card';

        const action = resolveAction(game);
        const title = game.name || 'Stress Relief Activity';
        const description = game.description || 'Tap to launch the activity.';
        const externalUrl = game.url || '';

        const buttonLabel = 'Try Now →';

        gameCard.innerHTML = `
            <div class="game-icon">🎮</div>
            <h4 class="game-title">${title}</h4>
            <p class="game-description">${description}</p>
            ${action
                ? `<button class="game-link" onclick="launchGame('${action}')">${buttonLabel}</button>`
                : externalUrl
                    ? `<a class="game-link" href="${externalUrl}" target="_blank" rel="noopener">${buttonLabel}</a>`
                    : `<button class="game-link" disabled>Unavailable</button>`
            }
        `;

        gamesGrid.appendChild(gameCard);
    });
}

// Launch game in new window
function launchGame(gameType) {
    let gameFile = '';
    
    if (gameType === 'breathing') {
        gameFile = 'breathing.html';
    } else if (gameType === 'memory') {
        gameFile = 'memory.html';
    } else if (gameType === 'color') {
        gameFile = 'color.html';
    }
    
    if (gameFile) {
        window.open(gameFile, 'game', 'width=700,height=900,resizable=yes,scrollbars=yes');
    }
}

// Smooth scroll for navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = link.getAttribute('href');
        const targetEl = document.querySelector(targetId);
        if (targetEl) {
            targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
    });
});
