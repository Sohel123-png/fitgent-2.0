// FitGen 2.0 - Anime Character Library

document.addEventListener('DOMContentLoaded', function() {
    // Character definitions
    const characters = {
        // Main mascot
        mascot: {
            name: 'Fitto',
            image: 'https://i.imgur.com/JYd6Gj3.png',
            poses: {
                default: 'https://i.imgur.com/JYd6Gj3.png',
                happy: 'https://i.imgur.com/8kCSLmm.png',
                workout: 'https://i.imgur.com/JYd6Gj3.png',
                tired: 'https://i.imgur.com/JYd6Gj3.png',
                motivated: 'https://i.imgur.com/8kCSLmm.png'
            },
            animations: ['float', 'pulse', 'bounce'],
            quotes: [
                "Let's crush today's workout!",
                "Your fitness journey begins with a single step!",
                "Stay hydrated and motivated!",
                "You're doing amazing! Keep it up!",
                "Remember, progress is progress, no matter how small!"
            ]
        },
        
        // Workout trainer
        trainer: {
            name: 'Kazu',
            image: 'https://i.imgur.com/8kCSLmm.png',
            poses: {
                default: 'https://i.imgur.com/8kCSLmm.png',
                coaching: 'https://i.imgur.com/8kCSLmm.png',
                demonstrating: 'https://i.imgur.com/8kCSLmm.png',
                stretching: 'https://i.imgur.com/8kCSLmm.png',
                celebrating: 'https://i.imgur.com/8kCSLmm.png'
            },
            animations: ['bounce', 'pulse', 'slide'],
            quotes: [
                "One more rep! You can do it!",
                "Form is key - quality over quantity!",
                "Push your limits, but listen to your body!",
                "Great job on maintaining proper form!",
                "Remember to breathe through each exercise!"
            ]
        },
        
        // Nutrition advisor
        nutritionist: {
            name: 'Miki',
            image: 'https://i.imgur.com/JYd6Gj3.png',
            poses: {
                default: 'https://i.imgur.com/JYd6Gj3.png',
                cooking: 'https://i.imgur.com/JYd6Gj3.png',
                explaining: 'https://i.imgur.com/JYd6Gj3.png',
                measuring: 'https://i.imgur.com/JYd6Gj3.png',
                tasting: 'https://i.imgur.com/JYd6Gj3.png'
            },
            animations: ['float', 'fade', 'spin'],
            quotes: [
                "Balanced nutrition is the foundation of fitness!",
                "Remember to eat your colorful veggies!",
                "Protein helps your muscles recover and grow!",
                "Stay hydrated - water is your best friend!",
                "Meal prep is key to consistent healthy eating!"
            ]
        }
    };
    
    // Animation definitions
    const animations = {
        float: `
            @keyframes float {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
                100% { transform: translateY(0px); }
            }
        `,
        pulse: `
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
        `,
        bounce: `
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-20px); }
                60% { transform: translateY(-10px); }
            }
        `,
        fade: `
            @keyframes fade {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
        `,
        slide: `
            @keyframes slide {
                0% { transform: translateX(-10px); }
                50% { transform: translateX(10px); }
                100% { transform: translateX(-10px); }
            }
        `,
        spin: `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `
    };
    
    // Add animation styles to document
    const addAnimationStyles = () => {
        const style = document.createElement('style');
        let styleContent = '';
        
        for (const [name, css] of Object.entries(animations)) {
            styleContent += css;
            styleContent += `
                .anime-${name} {
                    animation: ${name} 3s ease-in-out infinite;
                }
            `;
        }
        
        style.textContent = styleContent;
        document.head.appendChild(style);
    };
    
    // Create a character element
    const createCharacter = (type, options = {}) => {
        const character = characters[type];
        if (!character) return null;
        
        const pose = options.pose || 'default';
        const animation = options.animation || character.animations[0];
        const position = options.position || 'top-right';
        const size = options.size || 'medium';
        const quote = options.quote || (options.randomQuote ? character.quotes[Math.floor(Math.random() * character.quotes.length)] : null);
        
        // Create container
        const container = document.createElement('div');
        container.className = `anime-character anime-character-${type} position-${position} size-${size}`;
        if (animation) {
            container.classList.add(`anime-${animation}`);
        }
        
        // Create image
        const img = document.createElement('img');
        img.src = character.poses[pose];
        img.alt = character.name;
        container.appendChild(img);
        
        // Add quote bubble if needed
        if (quote) {
            const bubble = document.createElement('div');
            bubble.className = 'quote-bubble';
            bubble.textContent = quote;
            container.appendChild(bubble);
            
            // Add styles for quote bubble
            const style = document.createElement('style');
            style.textContent = `
                .quote-bubble {
                    position: absolute;
                    background: white;
                    border-radius: 20px;
                    padding: 10px 15px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                    max-width: 200px;
                    top: 0;
                    left: 100%;
                    margin-left: 10px;
                    font-size: 14px;
                    opacity: 0;
                    transform: translateY(-10px);
                    animation: bubbleIn 0.3s forwards 0.5s;
                    z-index: 10;
                }
                
                .quote-bubble:before {
                    content: '';
                    position: absolute;
                    left: -10px;
                    top: 15px;
                    border-width: 10px 10px 10px 0;
                    border-style: solid;
                    border-color: transparent white transparent transparent;
                }
                
                @keyframes bubbleIn {
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        return container;
    };
    
    // Initialize
    addAnimationStyles();
    
    // Expose to global scope
    window.FitGenAnime = {
        createCharacter,
        characters
    };
});
