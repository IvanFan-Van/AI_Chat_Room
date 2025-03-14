// Current loaded chat data
let currentChatData = null;
// Current selected chat file path
let currentChatFilePath = '';
// Poll interval in milliseconds (2 seconds)
const pollInterval = 2000;
// Flag to toggle thought bubbles
let showThoughts = false;
// Dark mode state
let darkMode = false;
// Polling timer ID
let pollingTimer = null;

// Function to scan log directories and get available chat files
async function scanLogDirectories() {
    try {
        // Fetch the log directory listing using new API
        const response = await fetch('/api/logs');
        
        if (!response.ok) {
            throw new Error(`Failed to fetch logs: ${response.status}`);
        }
        
        const logFiles = await response.json();
        return logFiles;
        
    } catch (error) {
        console.error('Error scanning log directories:', error);
        return [];
    }
}

// Function to populate log selection modal
async function populateLogSelection() {
    const logsContainer = document.getElementById('logs-container');
    logsContainer.innerHTML = '<div class="loader"></div><p>正在加载聊天记录...</p>';
    
    const logFiles = await scanLogDirectories();
    
    if (logFiles.length === 0) {
        logsContainer.innerHTML = '<p>未找到聊天记录，请确保log目录存在并包含有效的聊天文件。</p>';
        return;
    }
    
    logsContainer.innerHTML = '';
    
    logFiles.forEach(log => {
        const logItem = document.createElement('div');
        logItem.className = 'log-item';
        logItem.dataset.path = log.path;
        
        const formattedDate = new Date(log.timestamp).toLocaleString('zh-CN');
        
        logItem.innerHTML = `
            <div class="log-info">
                <div class="log-id">会话: ${log.id}</div>
                <div class="log-date">时间: ${formattedDate}</div>
                <div class="log-participants">参与者: ${log.participants.join(', ')}</div>
                <div class="log-preview">${log.firstMessage}</div>
            </div>
            <div class="log-actions">
                <button class="button select-log">查看</button>
            </div>
        `;
        
        logItem.querySelector('.select-log').addEventListener('click', () => {
            selectLogFile(log.path);
        });
        
        logsContainer.appendChild(logItem);
    });
}

// Function to select a log file and load the chat
function selectLogFile(path) {
    currentChatFilePath = path;
    
    // Hide modal and show chat container
    document.getElementById('log-selection-modal').style.display = 'none';
    document.querySelector('.container').style.display = '';
    
    // Load the selected chat data
    loadChatData();
    
    // Start polling for updates
    startPolling();
}

// Function to show log selection modal
function showLogSelectionModal() {
    document.getElementById('log-selection-modal').style.display = 'flex';
    document.querySelector('.container').style.display = 'none';
    populateLogSelection();
    
    // Stop polling when modal is shown
    stopPolling();
}

// Function to start polling
function startPolling() {
    // Clear existing timer if any
    stopPolling();
    
    // Start new polling timer
    pollingTimer = setInterval(loadChatData, pollInterval);
}

// Function to stop polling
function stopPolling() {
    if (pollingTimer) {
        clearInterval(pollingTimer);
        pollingTimer = null;
    }
}

// Function to fetch and process the chat data
async function loadChatData() {
    if (!currentChatFilePath) {
        console.error('No chat file selected');
        return;
    }
    
    try {
        const response = await fetch(currentChatFilePath);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch chat data: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Check if the data has changed
        if (!currentChatData || JSON.stringify(data) !== JSON.stringify(currentChatData)) {
            currentChatData = data;
            displayChatData(data);
            document.getElementById('status').textContent = '状态: 已更新';
            document.getElementById('status').style.backgroundColor = 'var(--status-good)';
            
            // Show update notification
            showNotification('聊天已更新');
        }
    } catch (error) {
        console.error('Error loading chat data:', error);
        document.getElementById('status').textContent = '状态: 连接错误';
        document.getElementById('status').style.backgroundColor = 'var(--status-bad)';
    }
}

// Function to display chat data
function displayChatData(data) {
    // Display session information
    document.getElementById('session-id').textContent = `会话ID: ${data.session_id}`;
    document.getElementById('timestamp').textContent = `时间: ${formatDateTime(data.timestamp)}`;
    document.getElementById('participants').textContent = `参与者: ${data.participants.join(', ')}`;
    document.getElementById('background').textContent = data.background;
    
    // Display messages
    const chatMessagesElement = document.getElementById('chat-messages');
    chatMessagesElement.innerHTML = '';
    
    // Display all messages (or filter if needed)
    filteredMessages = data.messages.filter(message => message.decision === "yes" || message.sender === "system");
    filteredMessages.forEach(message => {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.sender.toLowerCase()}`;
        
        const bubbleElement = document.createElement('div');
        bubbleElement.className = 'bubble';
        bubbleElement.textContent = message.content;
        
        const metaElement = document.createElement('div');
        metaElement.className = 'meta';
        metaElement.textContent = `${message.sender} • ${formatTime(message.timestamp)}`;
        
        messageElement.appendChild(bubbleElement);
        messageElement.appendChild(metaElement);
        
        // Add thought bubble if available and if showThoughts is enabled
        if (showThoughts && message.thought) {
            const thoughtElement = document.createElement('div');
            thoughtElement.className = 'thought';
            
            const thoughtIcon = document.createElement('span');
            thoughtIcon.className = 'thought-icon';
            thoughtIcon.innerHTML = '💭';
            
            const thoughtContent = document.createElement('span');
            thoughtContent.className = 'thought-content';
            thoughtContent.textContent = message.thought;
            
            thoughtElement.appendChild(thoughtIcon);
            thoughtElement.appendChild(thoughtContent);
            messageElement.appendChild(thoughtElement);
        }
        
        chatMessagesElement.appendChild(messageElement);
    });
    
    // Scroll to the bottom of the chat
    chatMessagesElement.scrollTop = chatMessagesElement.scrollHeight;
}

// Helper function to format datetime
function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN');
}

// Helper function to format time only (for messages)
function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
}

// Show notification
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Remove after animation
    setTimeout(() => {
        notification.classList.add('fadeout');
        setTimeout(() => notification.remove(), 500);
    }, 2000);
}

// Toggle thought bubbles
function toggleThoughts() {
    showThoughts = !showThoughts;
    if (currentChatData) {
        displayChatData(currentChatData);
    }
    
    const thoughtsToggle = document.getElementById('thoughts-toggle');
    thoughtsToggle.textContent = showThoughts ? '隐藏想法' : '显示想法';
}

// Toggle dark mode
function toggleDarkMode() {
    darkMode = !darkMode;
    document.body.classList.toggle('dark-mode');
    
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    darkModeToggle.textContent = darkMode ? '☀️ 浅色模式' : '🌙 深色模式';
    
    // Save preference
    localStorage.setItem('darkMode', darkMode);
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    // Load dark mode preference
    if (localStorage.getItem('darkMode') === 'true') {
        darkMode = true;
        document.body.classList.add('dark-mode');
        if (document.getElementById('dark-mode-toggle')) {
            document.getElementById('dark-mode-toggle').textContent = '☀️ 浅色模式';
        }
    }
    
    // Add event listeners for toggles
    if (document.getElementById('thoughts-toggle')) {
        document.getElementById('thoughts-toggle').addEventListener('click', toggleThoughts);
    }
    
    if (document.getElementById('dark-mode-toggle')) {
        document.getElementById('dark-mode-toggle').addEventListener('click', toggleDarkMode);
    }
    
    if (document.getElementById('change-log')) {
        document.getElementById('change-log').addEventListener('click', showLogSelectionModal);
    }
    
    // Start with log selection
    showLogSelectionModal();
});
