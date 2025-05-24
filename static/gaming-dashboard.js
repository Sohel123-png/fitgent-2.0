/**
 * FitGen 2.0 - Gaming Dashboard JavaScript
 * This file handles all the interactive elements and animations for the gaming dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize circular progress
    initCircularProgress();
    
    // Initialize animations
    initAnimations();
    
    // Initialize navigation
    initNavigation();
    
    // Initialize game cards
    initGameCards();
});

/**
 * Initialize circular progress charts
 */
function initCircularProgress() {
    const circles = document.querySelectorAll('.stat-circle');
    
    circles.forEach(circle => {
        const value = parseInt(circle.getAttribute('data-value'));
        const max = parseInt(circle.getAttribute('data-max')) || 100;
        const percentage = (value / max) * 100;
        
        const circleProgress = circle.querySelector('.circle-progress');
        const radius = circleProgress.getAttribute('r');
        const circumference = 2 * Math.PI * radius;
        
        // Set the stroke-dasharray and stroke-dashoffset
        circleProgress.style.strokeDasharray = `${circumference} ${circumference}`;
        circleProgress.style.strokeDashoffset = circumference - (percentage / 100) * circumference;
        
        // Animate the value counter
        const valueElement = circle.querySelector('.circle-value');
        animateCounter(valueElement, 0, value, 1500);
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
 * Initialize animations for dashboard elements
 */
function initAnimations() {
    // Animate sidebar items
    const sidebarItems = document.querySelectorAll('.nav-item');
    sidebarItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            item.style.transition = 'all 0.3s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, 100 + (index * 50));
    });
    
    // Animate game cards
    const gameCards = document.querySelectorAll('.game-card');
    gameCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.3s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 300 + (index * 100));
    });
    
    // Animate stat items
    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            item.style.transition = 'all 0.3s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, 500 + (index * 100));
    });
    
    // Animate download items
    const downloadItems = document.querySelectorAll('.download-item');
    downloadItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            item.style.transition = 'all 0.3s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, 700 + (index * 100));
    });
}

/**
 * Initialize navigation functionality
 */
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all items
            navItems.forEach(navItem => {
                navItem.classList.remove('active');
            });
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Here you would typically handle navigation or content switching
            // For demo purposes, we'll just log the action
            console.log('Navigated to:', this.getAttribute('data-section'));
        });
    });
}

/**
 * Initialize game cards functionality
 */
function initGameCards() {
    const gameCards = document.querySelectorAll('.game-card');
    
    gameCards.forEach(card => {
        card.addEventListener('click', function() {
            const gameTitle = this.querySelector('.game-title').textContent;
            console.log('Selected game:', gameTitle);
            
            // Here you would typically handle game selection or details view
            // For demo purposes, we'll just add a visual feedback
            this.style.transform = 'translateY(-15px)';
            setTimeout(() => {
                this.style.transform = 'translateY(-10px)';
            }, 300);
        });
    });
}

/**
 * Update user statistics with new data
 * @param {Object} data - The new statistics data
 */
function updateUserStats(data) {
    // Update circular progress
    const statCircle = document.querySelector('.stat-circle');
    if (statCircle) {
        const circleValue = statCircle.querySelector('.circle-value');
        const circleProgress = statCircle.querySelector('.circle-progress');
        
        const newValue = data.playtime || 0;
        const max = parseInt(statCircle.getAttribute('data-max')) || 100;
        const percentage = (newValue / max) * 100;
        
        const radius = circleProgress.getAttribute('r');
        const circumference = 2 * Math.PI * radius;
        
        // Animate to new value
        animateCounter(circleValue, parseInt(circleValue.textContent.replace(',', '')), newValue, 1000);
        
        // Animate progress
        circleProgress.style.transition = 'stroke-dashoffset 1s ease';
        circleProgress.style.strokeDashoffset = circumference - (percentage / 100) * circumference;
    }
    
    // Update stat items
    if (data.stats) {
        Object.keys(data.stats).forEach(key => {
            const statItem = document.querySelector(`.stat-item[data-stat="${key}"] .stat-value`);
            if (statItem) {
                const currentValue = parseInt(statItem.textContent.replace(',', ''));
                animateCounter(statItem, currentValue, data.stats[key], 1000);
            }
        });
    }
}

// Export functions for external use
window.GamingDashboard = {
    updateUserStats,
    animateCounter,
    initCircularProgress
};
