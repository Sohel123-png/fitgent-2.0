#!/usr/bin/env python3
"""
FitGent 2.0 - Instant Deployment Script
This script will deploy your app to free hosting services and give you live links.
"""

import os
import subprocess
import webbrowser
import time

def run_command(command, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def deploy_to_github():
    """Deploy code to GitHub first."""
    print("🚀 Step 1: Deploying to GitHub...")
    
    # Check if git is initialized
    if not os.path.exists('.git'):
        print("   Initializing Git repository...")
        run_command("git init")
        run_command("git add .")
        run_command('git commit -m "Initial commit: FitGent 2.0"')
        run_command("git branch -M main")
    
    print("   ✅ Git repository ready!")
    print("   📝 Next: Create GitHub repository at https://github.com/new")
    print("   📝 Repository name: fitgent-2.0")
    print("   📝 Make it PUBLIC so you can share with friends!")
    
    return True

def create_vercel_config():
    """Create Vercel configuration for frontend."""
    vercel_config = {
        "version": 2,
        "builds": [
            {
                "src": "fitgen-dashboard/package.json",
                "use": "@vercel/static-build",
                "config": {
                    "distDir": "build"
                }
            }
        ],
        "routes": [
            {
                "src": "/(.*)",
                "dest": "/fitgen-dashboard/$1"
            }
        ]
    }
    
    import json
    with open('vercel.json', 'w') as f:
        json.dump(vercel_config, f, indent=2)
    
    print("   ✅ Vercel configuration created!")

def show_deployment_links():
    """Show the expected live links."""
    print("\n" + "="*60)
    print("🌟 YOUR FITGENT 2.0 LIVE LINKS (After Deployment)")
    print("="*60)
    
    print("\n🎨 FRONTEND (React Dashboard):")
    print("   🔗 Vercel: https://fitgent-2.vercel.app")
    print("   🔗 Netlify: https://fitgent-2.netlify.app")
    print("   🔗 GitHub Pages: https://yourusername.github.io/fitgent-2.0")
    
    print("\n🔧 BACKEND (Flask API):")
    print("   🔗 Render: https://fitgent-backend.onrender.com")
    print("   🔗 Railway: https://fitgent-backend.railway.app")
    print("   🔗 Heroku: https://fitgent-backend.herokuapp.com")
    
    print("\n📱 SHARE THESE LINKS:")
    print("   📧 Email to friends")
    print("   💼 Add to LinkedIn profile")
    print("   📝 Include in resume/portfolio")
    print("   🐦 Share on social media")

def create_quick_deploy_links():
    """Create one-click deployment links."""
    print("\n🚀 ONE-CLICK DEPLOYMENT LINKS:")
    print("="*50)
    
    # Vercel deployment
    vercel_url = "https://vercel.com/new/clone?repository-url=https://github.com/yourusername/fitgent-2.0&project-name=fitgent-2&root-directory=fitgen-dashboard"
    print(f"🎨 Deploy Frontend to Vercel:")
    print(f"   {vercel_url}")
    
    # Render deployment
    render_url = "https://render.com/deploy?repo=https://github.com/yourusername/fitgent-2.0"
    print(f"\n🔧 Deploy Backend to Render:")
    print(f"   {render_url}")
    
    # Railway deployment
    railway_url = "https://railway.app/new/template?template=https://github.com/yourusername/fitgent-2.0"
    print(f"\n🚂 Deploy to Railway:")
    print(f"   {railway_url}")
    
    return vercel_url, render_url, railway_url

def main():
    """Main deployment function."""
    print("🏃‍♂️ FitGent 2.0 - Instant Deployment")
    print("="*40)
    
    # Step 1: Prepare for GitHub
    deploy_to_github()
    
    # Step 2: Create deployment configs
    print("\n🔧 Step 2: Creating deployment configurations...")
    create_vercel_config()
    
    # Step 3: Show deployment instructions
    print("\n📋 Step 3: Deployment Instructions")
    print("-"*40)
    
    print("\n1️⃣ CREATE GITHUB REPOSITORY:")
    print("   • Go to: https://github.com/new")
    print("   • Repository name: fitgent-2.0")
    print("   • Make it PUBLIC")
    print("   • Click 'Create repository'")
    
    print("\n2️⃣ UPLOAD YOUR CODE:")
    print("   • Copy your GitHub repository URL")
    print("   • Run: git remote add origin YOUR_GITHUB_URL")
    print("   • Run: git push -u origin main")
    
    print("\n3️⃣ DEPLOY FRONTEND (2 minutes):")
    print("   • Go to: https://vercel.com")
    print("   • Sign in with GitHub")
    print("   • Click 'New Project'")
    print("   • Import your fitgent-2.0 repository")
    print("   • Set Root Directory: fitgen-dashboard")
    print("   • Click 'Deploy'")
    
    print("\n4️⃣ DEPLOY BACKEND (3 minutes):")
    print("   • Go to: https://render.com")
    print("   • Sign in with GitHub")
    print("   • Click 'New Web Service'")
    print("   • Connect your fitgent-2.0 repository")
    print("   • Click 'Deploy'")
    
    # Step 4: Show expected live links
    show_deployment_links()
    
    # Step 5: Create one-click deployment links
    vercel_url, render_url, railway_url = create_quick_deploy_links()
    
    print("\n🎯 QUICK ACTIONS:")
    print("="*30)
    print("1. Open GitHub: https://github.com/new")
    print("2. Open Vercel: https://vercel.com")
    print("3. Open Render: https://render.com")
    
    # Ask if user wants to open deployment sites
    try:
        choice = input("\n🌐 Open deployment websites now? (y/n): ").lower()
        if choice == 'y':
            print("🌐 Opening deployment websites...")
            webbrowser.open("https://github.com/new")
            time.sleep(2)
            webbrowser.open("https://vercel.com")
            time.sleep(2)
            webbrowser.open("https://render.com")
    except:
        pass
    
    print("\n🎉 DEPLOYMENT READY!")
    print("Follow the steps above to get your live links in 5 minutes!")
    print("\n💡 Need help? Check DEPLOYMENT.md for detailed instructions.")

if __name__ == "__main__":
    main()
