// API base URL - use relative path to work from any host
const API_URL = '/api';

// Global state
let currentSessionId = null;
let currentTimezone = 'local'; // 'local' or 'utc'

// DOM elements
let chatMessages, chatInput, sendButton, totalCourses, courseTitles, timezoneSelect;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements after page loads
    chatMessages = document.getElementById('chatMessages');
    chatInput = document.getElementById('chatInput');
    sendButton = document.getElementById('sendButton');
    totalCourses = document.getElementById('totalCourses');
    courseTitles = document.getElementById('courseTitles');
    timezoneSelect = document.getElementById('timezoneSelect');

    // Restore timezone preference from localStorage
    const savedTimezone = localStorage.getItem('preferredTimezone');
    if (savedTimezone) {
        currentTimezone = savedTimezone;
        timezoneSelect.value = savedTimezone;
    }

    setupEventListeners();
    createNewSession();
    loadCourseStats();
});

// Event Listeners
function setupEventListeners() {
    // Chat functionality
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Timezone selector
    timezoneSelect.addEventListener('change', (e) => {
        currentTimezone = e.target.value;
        localStorage.setItem('preferredTimezone', currentTimezone);
        // Update timestamps in existing messages
        updateAllMessageTimestamps();
    });

    // New chat button
    document.getElementById('newChatButton').addEventListener('click', createNewSession);

    // Suggested questions
    document.querySelectorAll('.suggested-item').forEach(button => {
        button.addEventListener('click', (e) => {
            const question = e.target.getAttribute('data-question');
            chatInput.value = question;
            sendMessage();
        });
    });
}


// Chat Functions
async function sendMessage() {
    const query = chatInput.value.trim();
    if (!query) return;

    // Disable input
    chatInput.value = '';
    chatInput.disabled = true;
    sendButton.disabled = true;

    // Add user message
    addMessage(query, 'user');

    // Add loading message - create a unique container for it
    const loadingMessage = createLoadingMessage();
    chatMessages.appendChild(loadingMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch(`${API_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                session_id: currentSessionId
            })
        });

        if (!response.ok) throw new Error('Query failed');

        const data = await response.json();
        
        // Update session ID if new
        if (!currentSessionId) {
            currentSessionId = data.session_id;
        }

        // Replace loading message with response
        loadingMessage.remove();
        addMessage(data.answer, 'assistant', data.sources);

    } catch (error) {
        // Replace loading message with error
        loadingMessage.remove();
        const errorMsg = createErrorMessage(error.message);
        chatMessages.appendChild(errorMsg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } finally {
        chatInput.disabled = false;
        sendButton.disabled = false;
        chatInput.focus();
    }
}

function createLoadingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant loading-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="loading">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span class="loading-text">Thinking...</span>
        </div>
    `;
    return messageDiv;
}

function createErrorMessage(errorMsg) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message error-message-wrapper';

    const errorText = errorMsg === 'Query failed'
        ? 'Sorry, I encountered an error processing your query. Please try again.'
        : `Sorry, ${errorMsg}`;

    messageDiv.innerHTML = `
        <div class="error-message-container">
            <div class="error-icon">⚠️</div>
            <div class="error-content">
                <div class="error-title">Error</div>
                <div class="error-text">${escapeHtml(errorText)}</div>
                <button class="retry-button" onclick="document.getElementById('chatInput').focus()">Try another question</button>
            </div>
        </div>
    `;
    return messageDiv;
}

function formatTimestamp(date, timezone) {
    const options = {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    };

    if (timezone === 'utc') {
        options.timeZone = 'UTC';
    } else {
        // Use browser's local timezone (Intl.DateTimeFormat handles this automatically)
    }

    const formatter = new Intl.DateTimeFormat('en-US', options);
    const formattedDate = formatter.format(date);

    if (timezone === 'utc') {
        return `${formattedDate} UTC`;
    } else {
        return `${formattedDate} Local`;
    }
}

function addMessage(content, type, sources = null, isWelcome = false) {
    const messageId = Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}${isWelcome ? ' welcome-message' : ''}`;
    messageDiv.id = `message-${messageId}`;
    messageDiv.dataset.timestamp = new Date().toISOString();

    // Convert markdown to HTML for assistant messages
    const displayContent = type === 'assistant' ? marked.parse(content) : escapeHtml(content);

    let html = `<div class="message-content">${displayContent}</div>`;

    // Add timestamp
    const timestamp = formatTimestamp(new Date(), currentTimezone);
    html += `<div class="message-timestamp">${timestamp}</div>`;

    if (sources && sources.length > 0) {
        // Format sources as a list with optional links
        const formattedSources = sources.map(source => {
            // Handle both old format (string) and new format (object with title and url)
            if (typeof source === 'string') {
                return `<li class="source-item"><span class="source-title">${source}</span></li>`;
            } else if (source.url) {
                return `<li class="source-item"><a href="${source.url}" target="_blank" class="source-link">${source.title}</a></li>`;
            } else {
                return `<li class="source-item"><span class="source-title">${source.title}</span></li>`;
            }
        }).join('');

        html += `
            <details class="sources-collapsible">
                <summary class="sources-header">📚 Sources</summary>
                <ul class="sources-list">${formattedSources}</ul>
            </details>
        `;
    }

    messageDiv.innerHTML = html;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageId;
}

function updateAllMessageTimestamps() {
    const messages = chatMessages.querySelectorAll('.message');
    messages.forEach(message => {
        const timestamp = message.querySelector('.message-timestamp');
        if (timestamp && message.dataset.timestamp) {
            const originalDate = new Date(message.dataset.timestamp);
            const newTimestamp = formatTimestamp(originalDate, currentTimezone);
            timestamp.textContent = newTimestamp;
        }
    });
}

// Helper function to escape HTML for user messages
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Removed removeMessage function - no longer needed since we handle loading differently

async function createNewSession() {
    currentSessionId = null;
    chatMessages.innerHTML = '';
    addMessage('Welcome to the Course Materials Assistant! I can help you with questions about courses, lessons and specific content. What would you like to know?', 'assistant', null, true);
}

// Load course statistics
async function loadCourseStats() {
    try {
        console.log('Loading course stats...');
        const response = await fetch(`${API_URL}/courses`);
        if (!response.ok) throw new Error('Failed to load course stats');
        
        const data = await response.json();
        console.log('Course data received:', data);
        
        // Update stats in UI
        if (totalCourses) {
            totalCourses.textContent = data.total_courses;
        }
        
        // Update course titles
        if (courseTitles) {
            if (data.course_titles && data.course_titles.length > 0) {
                courseTitles.innerHTML = data.course_titles
                    .map(title => `<div class="course-title-item">${title}</div>`)
                    .join('');
            } else {
                courseTitles.innerHTML = '<span class="no-courses">No courses available</span>';
            }
        }
        
    } catch (error) {
        console.error('Error loading course stats:', error);
        // Set default values on error
        if (totalCourses) {
            totalCourses.textContent = '0';
        }
        if (courseTitles) {
            courseTitles.innerHTML = '<span class="error">Failed to load courses</span>';
        }
    }
}