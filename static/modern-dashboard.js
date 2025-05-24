/**
 * FitGen 2.0 - Modern Dashboard JavaScript
 * This file handles all the interactive elements and animations for the modern dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize progress circles
    initProgressCircles();
    
    // Initialize chat functionality
    initChatAssistant();
    
    // Initialize meal planner tabs
    initMealTabs();
    
    // Initialize leaderboard tabs
    initLeaderboardTabs();
});

/**
 * Initialize circular progress indicators
 */
function initProgressCircles() {
    const circles = document.querySelectorAll('.progress-circle');
    
    circles.forEach(circle => {
        const value = parseInt(circle.getAttribute('data-value'));
        const max = parseInt(circle.getAttribute('data-max')) || 100;
        const percentage = (value / max) * 100;
        
        const circleProgress = circle.querySelector('.progress-circle-value');
        const radius = circleProgress.getAttribute('r');
        const circumference = 2 * Math.PI * radius;
        
        // Set the stroke-dasharray and stroke-dashoffset
        circleProgress.style.strokeDasharray = `${circumference} ${circumference}`;
        circleProgress.style.strokeDashoffset = circumference - (percentage / 100) * circumference;
        
        // Animate the value counter
        const valueElement = circle.querySelector('.progress-value');
        if (valueElement) {
            animateCounter(valueElement, 0, value, 1000);
        }
    });
}

/**
 * Animate a counter from start to end value
 * @param {HTMLElement} element - The element to update
 * @param {number} start - Starting value
 * @param {number} end - Ending value
 * @param {number} duration - Animation duration in milliseconds
 */
function animateCounter(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = Math.floor(progress * (end - start) + start);
        element.textContent = value.toLocaleString();
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

/**
 * Initialize chat assistant functionality
 */
function initChatAssistant() {
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');
    const chatContainer = document.getElementById('chatContainer');
    
    if (!chatInput || !sendButton || !chatContainer) return;
    
    // Sample responses for demo purposes
    const responses = [
        "Try drinking more water throughout the day to stay hydrated!",
        "A 30-minute walk can boost your mood and energy levels.",
        "Remember to take short breaks if you've been sitting for a long time.",
        "Great progress today! Keep up the good work!",
        "Have you tried meditation? It can help reduce stress and improve focus."
    ];
    
    // Function to send a message
    function sendMessage() {
        const message = chatInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        const userMessageHTML = `
            <div class="chat-message">
                <div class="chat-avatar">
                    <i class="fas fa-user"></i>
                </div>
                <div class="chat-bubble">
                    ${message}
                </div>
            </div>
        `;
        chatContainer.innerHTML += userMessageHTML;
        
        // Clear input
        chatInput.value = '';
        
        // Simulate assistant response after a short delay
        setTimeout(() => {
            // Get random response
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            
            // Add assistant message to chat
            const assistantMessageHTML = `
                <div class="chat-message">
                    <div class="chat-avatar" style="background-color: #3b82f6;">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="chat-bubble chat-response">
                        ${randomResponse}
                    </div>
                </div>
            `;
            chatContainer.innerHTML += assistantMessageHTML;
            
            // Scroll to bottom of chat
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 1000);
        
        // Scroll to bottom of chat
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

/**
 * Initialize meal planner tabs
 */
function initMealTabs() {
    const tabs = document.querySelectorAll('.meal-tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Here you would typically show/hide content based on the selected tab
            console.log('Selected tab:', this.textContent.trim());
        });
    });
}

/**
 * Initialize leaderboard tabs
 */
function initLeaderboardTabs() {
    const tabs = document.querySelectorAll('.leaderboard-tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Here you would typically show/hide content based on the selected tab
            console.log('Selected leaderboard tab:', this.textContent.trim());
        });
    });
}

/**
 * Update progress circle with new value
 * @param {string} id - The ID of the progress circle element
 * @param {number} value - The new value
 */
function updateProgressCircle(id, value) {
    const circle = document.getElementById(id);
    if (!circle) return;
    
    const max = parseInt(circle.getAttribute('data-max')) || 100;
    circle.setAttribute('data-value', value);
    
    const percentage = (value / max) * 100;
    
    const circleProgress = circle.querySelector('.progress-circle-value');
    const radius = circleProgress.getAttribute('r');
    const circumference = 2 * Math.PI * radius;
    
    // Update the stroke-dashoffset
    circleProgress.style.strokeDashoffset = circumference - (percentage / 100) * circumference;
    
    // Update the value text
    const valueElement = circle.querySelector('.progress-value');
    if (valueElement) {
        animateCounter(valueElement, parseInt(valueElement.textContent.replace(',', '')), value, 500);
    }
}

// Export functions for external use
window.FitGenDashboard = {
    updateProgressCircle,
    animateCounter
};
