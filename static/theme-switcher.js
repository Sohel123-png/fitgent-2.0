// FitGen 2.0 - Theme Switcher for Apple-Inspired Design

document.addEventListener('DOMContentLoaded', function() {
    // Create theme toggle button
    const createThemeToggle = () => {
        const toggle = document.createElement('div');
        toggle.className = 'day-night-toggle';
        toggle.id = 'themeToggle';
        toggle.innerHTML = `
            <svg id="sunIcon" class="theme-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
            <svg id="moonIcon" class="theme-icon" style="display: none;" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
        `;
        
        // Add styles for the toggle
        const style = document.createElement('style');
        style.textContent = `
            .day-night-toggle {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background-color: #ffffff;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .day-night-toggle:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
            }
            
            .theme-icon {
                color: #007aff;
                transition: all 0.3s ease;
            }
            
            .day-night-toggle:hover .theme-icon {
                transform: rotate(30deg);
            }
            
            body.dark-mode {
                background-color: #000000;
                color: #ffffff;
            }
            
            body.dark-mode .day-night-toggle {
                background-color: #1c1c1e;
            }
            
            body.dark-mode .theme-icon {
                color: #0a84ff;
            }
            
            .theme-transition {
                transition: background-color 0.5s ease, color 0.5s ease;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .spin-animation {
                animation: spin 0.5s ease-in-out;
            }
        `;
        document.head.appendChild(style);
        
        return toggle;
    };
    
    // Add toggle to the page
    const toggle = createThemeToggle();
    document.body.appendChild(toggle);
    
    // Check for saved theme preference or system preference
    const savedTheme = localStorage.getItem('fitgen-theme');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Set initial theme
    if (savedTheme === 'dark' || (!savedTheme && prefersDarkScheme.matches)) {
        document.body.classList.add('dark-mode');
        document.getElementById('moonIcon').style.display = 'block';
        document.getElementById('sunIcon').style.display = 'none';
    }
    
    // Add transition class after initial load to enable smooth transitions
    setTimeout(() => {
        document.body.classList.add('theme-transition');
    }, 100);
    
    // Toggle theme function
    const toggleTheme = () => {
        // Add spin animation
        const activeIcon = document.body.classList.contains('dark-mode') 
            ? document.getElementById('moonIcon') 
            : document.getElementById('sunIcon');
        activeIcon.classList.add('spin-animation');
        
        // Toggle theme with a slight delay for animation
        setTimeout(() => {
            if (document.body.classList.contains('dark-mode')) {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('fitgen-theme', 'light');
                document.getElementById('sunIcon').style.display = 'block';
                document.getElementById('moonIcon').style.display = 'none';
            } else {
                document.body.classList.add('dark-mode');
                localStorage.setItem('fitgen-theme', 'dark');
                document.getElementById('moonIcon').style.display = 'block';
                document.getElementById('sunIcon').style.display = 'none';
            }
            
            // Remove animation class after transition
            setTimeout(() => {
                activeIcon.classList.remove('spin-animation');
            }, 500);
        }, 150);
        
        // Update anime characters based on theme
        updateAnimeCharacters();
    };
    
    // Update anime characters based on theme
    const updateAnimeCharacters = () => {
        const isDarkMode = document.body.classList.contains('dark-mode');
        const animeCharacters = document.querySelectorAll('.anime-character img');
        
        animeCharacters.forEach(character => {
            // Add a glow effect to anime characters in dark mode
            if (isDarkMode) {
                character.style.filter = 'drop-shadow(0 0 8px rgba(10, 132, 255, 0.6))';
            } else {
                character.style.filter = 'none';
            }
        });
    };
    
    // Add event listener to toggle
    toggle.addEventListener('click', toggleTheme);
    
    // Initial update for anime characters
    updateAnimeCharacters();
    
    // Listen for system theme changes
    prefersDarkScheme.addEventListener('change', (e) => {
        if (!localStorage.getItem('fitgen-theme')) {
            if (e.matches) {
                document.body.classList.add('dark-mode');
                document.getElementById('moonIcon').style.display = 'block';
                document.getElementById('sunIcon').style.display = 'none';
            } else {
                document.body.classList.remove('dark-mode');
                document.getElementById('sunIcon').style.display = 'block';
                document.getElementById('moonIcon').style.display = 'none';
            }
            updateAnimeCharacters();
        }
    });
});
