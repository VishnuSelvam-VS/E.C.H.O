// State Management
let state = {
    tension: 100,
    tensionHistory: Array(20).fill(100),
    messages: [],
    agentLogs: [],
    apiKey: localStorage.getItem('gemini_api_key') || '',
    chart: null
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initChart();
    checkApiKey();
    updateTensionDisplay();
});

// Check for API Key
function checkApiKey() {
    if (!state.apiKey) {
        document.getElementById('apiModal').classList.remove('hidden');
    } else {
        document.getElementById('apiModal').classList.add('hidden');
    }
}

// Save API Key
function saveApiKey() {
    const apiKey = document.getElementById('apiKeyInput').value.trim();
    if (apiKey) {
        state.apiKey = apiKey;
        localStorage.setItem('gemini_api_key', apiKey);
        document.getElementById('apiModal').classList.add('hidden');
    } else {
        alert('Please enter a valid API key');
    }
}

// Initialize Chart
function initChart() {
    const ctx = document.getElementById('tensionChart').getContext('2d');
    state.chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array(20).fill(''),
            datasets: [{
                data: state.tensionHistory,
                borderColor: '#ff2b2b',
                backgroundColor: 'rgba(255, 43, 43, 0.2)',
                fill: true,
                tension: 0.4,
                borderWidth: 3,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    display: false
                },
                x: {
                    display: false
                }
            },
            animation: {
                duration: 500
            }
        }
    });
}

// Update Tension Display
function updateTensionDisplay() {
    const tensionValue = document.getElementById('tensionValue');
    const tensionDisplay = document.getElementById('tensionDisplay');
    const heartRate = document.getElementById('heartRate');
    const statusIndicator = document.getElementById('statusIndicator');

    tensionValue.textContent = state.tension;
    heartRate.textContent = `💓 ${60 + state.tension} BPM`;

    // Update colors based on tension
    let color;
    if (state.tension > 70) {
        color = '#ff2b2b';
    } else if (state.tension > 30) {
        color = '#f7b731';
    } else {
        color = '#00cc96';
    }

    tensionDisplay.style.borderColor = color;
    tensionDisplay.style.backgroundColor = `${color}10`;
    tensionValue.style.color = color;
    statusIndicator.style.backgroundColor = color;

    // Update chart
    if (state.chart) {
        state.chart.data.datasets[0].borderColor = color;
        state.chart.data.datasets[0].backgroundColor = `${color}40`;
        state.chart.data.datasets[0].data = state.tensionHistory;
        state.chart.update();
    }
}

// Send Message
async function sendMessage() {
    const input = document.getElementById('userInput');
    const userText = input.value.trim();

    if (!userText) {
        alert('Please enter a message');
        return;
    }

    if (!state.apiKey) {
        alert('Please configure your API key first');
        checkApiKey();
        return;
    }

    // Add user message
    addMessage('user', userText);
    input.value = '';

    // Show loading
    showLoading();

    // Call AI
    try {
        await runSimulation(userText);
    } catch (error) {
        console.error('Error:', error);
        addMessage('system', `Error: ${error.message}`);
    }

    hideLoading();
}

// Run Simulation (Double-Tap Logic)
async function runSimulation(userInput) {
    // AGENT 1: Monitor
    const monitorPrompt = `You are a psychological monitor analyzing a crisis negotiation.

SCENARIO: Sarah is a 24-year-old ER patient, terrified of needles, hyperventilating.
Current Tension: ${state.tension}/100

User (Responder) said: "${userInput}"

ANALYSIS RULES:
- If user validates feelings ("I understand you're scared") → Decrease tension by 15-20
- If user uses soft tone, empathy, patience → Decrease tension by 10-15
- If user gives orders ("Calm down", "Just relax") → Increase tension by 15-20
- If user uses logic/facts without empathy → Increase tension by 5-10
- If user is dismissive or rude → Increase tension by 25-30

Output ONLY valid JSON (no markdown):
{"new_tension": <number 0-100>, "reasoning": "<brief explanation>", "technique_used": "<validation/logic/dismissal/empathy>"}`;

    const monitorResult = await callGemini(monitorPrompt);

    // Parse monitor response
    let monitorData;
    try {
        const cleanJson = monitorResult.replace(/```json/g, '').replace(/```/g, '').trim();
        monitorData = JSON.parse(cleanJson);
        state.tension = Math.max(0, Math.min(100, monitorData.new_tension));

        // Log
        addAgentLog('Monitor', monitorData);
    } catch (e) {
        console.error('Monitor parsing error:', e);
        monitorData = { reasoning: 'Error analyzing response' };
    }

    // Update tension history
    state.tensionHistory.push(state.tension);
    if (state.tensionHistory.length > 20) {
        state.tensionHistory.shift();
    }
    updateTensionDisplay();

    // AGENT 2: Actor
    const actorPrompt = `You are Sarah, a 24-year-old patient in the ER. You are TERRIFIED of needles.

CURRENT STATE:
- Tension Level: ${state.tension}/100
- Physical: Hyperventilating, shaking, sweating
- Mental: Convinced the medicine is poison, paranoid

BEHAVIOR RULES:
- If Tension > 80: SCREAM (use ALL CAPS), stutter, refuse help, interrupt
- If Tension 50-80: Be skeptical, ask fearful questions, voice shaking
- If Tension 30-50: Still nervous but listening, speak softer
- If Tension < 30: Calm, cooperative, grateful

The responder just said: "${userInput}"

Respond as Sarah. Keep it SHORT (1-2 sentences max). ACT the emotion intensely.`;

    const actorResult = await callGemini(actorPrompt);

    // Add AI message
    addMessage('ai', actorResult);

    // Speak (TTS simulation - would need actual TTS API)
    speakText(actorResult);
}

// Call Gemini API
async function callGemini(prompt) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${state.apiKey}`;

    console.log('Calling Gemini API...');

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: prompt
                    }]
                }]
            })
        });

        const data = await response.json();
        console.log('API Response:', data);

        if (!response.ok) {
            console.error('API Error:', data);
            throw new Error(data.error?.message || 'API call failed. Check your API key and ensure it has Gemini API access enabled.');
        }

        if (!data.candidates || !data.candidates[0] || !data.candidates[0].content) {
            throw new Error('Invalid API response format');
        }

        return data.candidates[0].content.parts[0].text;
    } catch (error) {
        console.error('Gemini API Error:', error);
        throw error;
    }
}

// Add Message to UI
function addMessage(role, text) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${role}`;

    if (role === 'system') {
        messageDiv.innerHTML = `<div class="system-message"><p>${text}</p></div>`;
    } else {
        const label = role === 'user' ? '🧑 You' : '😰 Sarah';
        messageDiv.innerHTML = `
            <div class="message-label">${label}</div>
            <div class="message-content">${text}</div>
        `;
    }

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    state.messages.push({ role, text });
}

// Add Agent Log
function addAgentLog(agent, data) {
    const logsContent = document.getElementById('logsContent');

    // Remove empty message
    const emptyMsg = logsContent.querySelector('.logs-empty');
    if (emptyMsg) emptyMsg.remove();

    const logDiv = document.createElement('div');
    logDiv.className = 'log-entry';
    logDiv.innerHTML = `
        <h4>Turn ${state.agentLogs.length + 1} - ${agent}</h4>
        <pre>${JSON.stringify(data, null, 2)}</pre>
    `;

    logsContent.appendChild(logDiv);
    state.agentLogs.push({ agent, data });
}

// Text-to-Speech (Browser API)
function speakText(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = state.tension > 70 ? 1.2 : 0.9;
        utterance.pitch = state.tension > 70 ? 1.3 : 1.0;
        speechSynthesis.speak(utterance);
    }
}

// UI Helpers
function showLoading() {
    addMessage('system', '⏳ Sarah is responding...');
}

function hideLoading() {
    const messages = document.getElementById('messages');
    const loadingMsg = messages.querySelector('.system-message:last-child');
    if (loadingMsg && loadingMsg.textContent.includes('responding')) {
        loadingMsg.remove();
    }
}

function toggleBrief() {
    const brief = document.getElementById('briefContent');
    brief.classList.toggle('active');
}

function toggleLogs() {
    const logs = document.getElementById('agentLogs');
    logs.classList.toggle('active');
}

function resetSimulation() {
    if (confirm('Reset the simulation? This will clear all progress.')) {
        state.tension = 100;
        state.tensionHistory = Array(20).fill(100);
        state.messages = [];
        state.agentLogs = [];

        document.getElementById('messages').innerHTML = `
            <div class="system-message">
                <p>🎯 Simulation started. Sarah is in extreme distress. Use empathy to de-escalate.</p>
            </div>
        `;

        document.getElementById('logsContent').innerHTML = `
            <p class="logs-empty">Waiting for interaction...</p>
        `;

        updateTensionDisplay();
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Microphone (Placeholder - would need Web Speech API)
document.getElementById('micButton').addEventListener('click', () => {
    alert('🎙️ Voice input coming soon! For now, please use text input.');
    // In production, implement Web Speech API here
});
