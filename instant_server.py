#!/usr/bin/env python3
"""
FitGent 2.0 - Instant Live Server
Creates immediate live links for your app!
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading
import time
import os

def create_live_demo():
    """Create a live demo page"""
    demo_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏃‍♂️ FitGent 2.0 - Live Demo</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .pulse { animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    </style>
</head>
<body class="bg-gray-50">
    <div class="gradient-bg text-white min-h-screen">
        <div class="container mx-auto px-6 py-16">
            <div class="text-center">
                <h1 class="text-6xl font-bold mb-4">🏃‍♂️ FitGent 2.0</h1>
                <p class="text-2xl mb-8">AI-Powered Fitness Platform</p>
                <div class="pulse bg-green-500 text-white px-6 py-3 rounded-full inline-block mb-8">
                    🟢 LIVE DEMO RUNNING
                </div>
                
                <div class="grid md:grid-cols-3 gap-8 mt-12">
                    <div class="bg-white/10 backdrop-blur-lg p-8 rounded-xl">
                        <div class="text-4xl mb-4">🎨</div>
                        <h3 class="text-xl font-bold mb-4">Frontend Dashboard</h3>
                        <a href="http://localhost:3000" target="_blank" 
                           class="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors inline-block">
                            Open Dashboard
                        </a>
                    </div>
                    
                    <div class="bg-white/10 backdrop-blur-lg p-8 rounded-xl">
                        <div class="text-4xl mb-4">🔧</div>
                        <h3 class="text-xl font-bold mb-4">Backend API</h3>
                        <a href="http://localhost:5000" target="_blank" 
                           class="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-colors inline-block">
                            View API
                        </a>
                    </div>
                    
                    <div class="bg-white/10 backdrop-blur-lg p-8 rounded-xl">
                        <div class="text-4xl mb-4">📱</div>
                        <h3 class="text-xl font-bold mb-4">Share Demo</h3>
                        <button onclick="shareDemo()" 
                                class="bg-purple-500 text-white px-6 py-3 rounded-lg hover:bg-purple-600 transition-colors">
                            Share Link
                        </button>
                    </div>
                </div>
                
                <div class="mt-16 bg-white/10 backdrop-blur-lg p-8 rounded-xl">
                    <h2 class="text-2xl font-bold mb-6">🚀 Key Features</h2>
                    <div class="grid md:grid-cols-2 gap-6 text-left">
                        <div>
                            <h4 class="font-bold mb-2">⌚ Smartwatch Integration</h4>
                            <p>Google Fit, Apple Health, Mi Band support</p>
                        </div>
                        <div>
                            <h4 class="font-bold mb-2">🤖 AI Health Engine</h4>
                            <p>Personalized recommendations & wellness score</p>
                        </div>
                        <div>
                            <h4 class="font-bold mb-2">🎮 Gaming Dashboard</h4>
                            <p>Achievements, leaderboards, anime animations</p>
                        </div>
                        <div>
                            <h4 class="font-bold mb-2">💬 AI Chatbot</h4>
                            <p>Fitness guidance and mental wellness support</p>
                        </div>
                    </div>
                </div>
                
                <div class="mt-12">
                    <h3 class="text-xl font-bold mb-4">💻 Tech Stack</h3>
                    <div class="flex justify-center space-x-4 flex-wrap">
                        <span class="bg-blue-500 px-4 py-2 rounded-full">React 19</span>
                        <span class="bg-green-500 px-4 py-2 rounded-full">Flask</span>
                        <span class="bg-purple-500 px-4 py-2 rounded-full">TypeScript</span>
                        <span class="bg-pink-500 px-4 py-2 rounded-full">Tailwind CSS</span>
                        <span class="bg-yellow-500 px-4 py-2 rounded-full">Google Fit API</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function shareDemo() {
            const url = window.location.href;
            const text = "🚀 Check out FitGent 2.0 - AI-powered fitness platform! #FitnessApp #AI #React #Python";
            
            if (navigator.share) {
                navigator.share({ title: 'FitGent 2.0', text: text, url: url });
            } else {
                navigator.clipboard.writeText(url);
                alert('Demo link copied to clipboard!\\n\\nShare this link: ' + url);
            }
        }
        
        // Auto-check server status
        setInterval(() => {
            fetch('http://localhost:5000').then(() => {
                document.getElementById('backend-status').textContent = '🟢 Online';
            }).catch(() => {
                document.getElementById('backend-status').textContent = '🔴 Offline';
            });
            
            fetch('http://localhost:3000').then(() => {
                document.getElementById('frontend-status').textContent = '🟢 Online';
            }).catch(() => {
                document.getElementById('frontend-status').textContent = '🔴 Offline';
            });
        }, 5000);
    </script>
</body>
</html>"""
    
    os.makedirs("live_demo", exist_ok=True)
    with open("live_demo/index.html", "w", encoding="utf-8") as f:
        f.write(demo_html)
    
    return "live_demo"

def start_server(port=8080):
    """Start the live demo server"""
    demo_dir = create_live_demo()
    
    class DemoHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=demo_dir, **kwargs)
    
    def run():
        server = HTTPServer(('localhost', port), DemoHandler)
        print(f"🌐 Live demo server started at: http://localhost:{port}")
        server.serve_forever()
    
    server_thread = threading.Thread(target=run, daemon=True)
    server_thread.start()
    
    return f"http://localhost:{port}"

def main():
    print("🚀 FitGent 2.0 - Starting Instant Live Server...")
    print("="*50)
    
    # Start demo server
    demo_url = start_server(8080)
    
    print("\n🎉 LIVE DEMO READY!")
    print("="*25)
    print(f"🔗 Demo URL: {demo_url}")
    print(f"🔗 Backend: http://localhost:5000")
    print(f"🔗 Frontend: http://localhost:3000")
    
    print("\n📱 SHARE THESE LINKS:")
    print("• Copy and send to friends")
    print("• Add to LinkedIn profile")
    print("• Include in portfolio")
    print("• Show to employers")
    
    # Open in browser
    print(f"\n🌐 Opening {demo_url} in browser...")
    time.sleep(2)
    webbrowser.open(demo_url)
    
    print("\n✅ Server is running! Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")

if __name__ == "__main__":
    main()
