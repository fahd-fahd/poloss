#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Voice Assistant Installation Script
This script will install all the necessary dependencies for the voice assistant.
"""

import os
import sys
import subprocess
import platform
import shutil

def print_header(text):
    """Print a header with the given text."""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def check_python_version():
    """Check if Python version is at least 3.8."""
    print_header("Checking Python version")
    if sys.version_info < (3, 8):
        print("❌ Error: This bot requires Python 3.8 or higher.")
        print(f"Current version: Python {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version}")
    return True

def check_ffmpeg():
    """Check if FFmpeg is installed."""
    print_header("Checking FFmpeg")
    try:
        result = subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("✅ FFmpeg is installed.")
            return True
        else:
            print("❌ FFmpeg check failed.")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg is not installed. Please install FFmpeg from https://ffmpeg.org/download.html")
        if platform.system() == "Windows":
            print("For Windows, you can download it from: https://www.gyan.dev/ffmpeg/builds/")
        elif platform.system() == "Darwin":  # macOS
            print("For macOS, you can install it using Homebrew: brew install ffmpeg")
        elif platform.system() == "Linux":
            print("For Linux, you can install it using your package manager:")
            print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
            print("  Fedora: sudo dnf install ffmpeg")
            print("  Arch Linux: sudo pacman -S ffmpeg")
        return False

def install_dependencies():
    """Install required Python dependencies."""
    print_header("Installing Python dependencies")
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], check=True, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("❌ pip is not available. Please install pip.")
        sys.exit(1)
    
    # Install dependencies
    requirements_file = "voice_assistant_requirements.txt"
    if not os.path.exists(requirements_file):
        print(f"❌ {requirements_file} not found. Creating it...")
        with open(requirements_file, "w") as f:
            f.write("""discord.py>=2.3.2
SpeechRecognition>=3.10.0
openai-whisper>=20231117
azure-cognitiveservices-speech>=1.31.0
pydub>=0.25.1
yt-dlp>=2023.11.14
PyNaCl>=1.5.0
numpy>=1.24.0
ffmpeg-python>=0.2.0
python-dotenv>=1.0.0
""")
        print(f"✅ Created {requirements_file}")
    
    print(f"📦 Installing dependencies from {requirements_file}...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_file], check=True)
        print("✅ Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create a .env file if it doesn't exist."""
    print_header("Setting up environment variables")
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"⚠️ {env_file} file already exists. Skip this step? (Y/n)")
        response = input().strip().lower()
        if response != "n":
            print(f"✅ Using existing {env_file} file.")
            return True
    
    print(f"📝 Creating {env_file} file...")
    
    # Get Discord bot token
    print("\nEnter your Discord bot token (or press Enter to skip):")
    discord_token = input().strip()
    
    # Get Azure TTS key
    print("\nEnter your Azure Speech Services key (or press Enter to skip):")
    azure_key = input().strip()
    
    # Get Azure region
    print("\nEnter Azure region (default: eastus):")
    azure_region = input().strip() or "eastus"
    
    # Create .env file
    with open(env_file, "w") as f:
        f.write(f"# Discord Bot Configuration\n")
        f.write(f"DISCORD_BOT_TOKEN={discord_token}\n\n")
        f.write(f"# Azure Speech Services (for Text-to-Speech)\n")
        f.write(f"AZURE_TTS_KEY={azure_key}\n")
        f.write(f"AZURE_REGION={azure_region}\n\n")
        f.write(f"# Whisper Speech Recognition Settings\n")
        f.write(f"WHISPER_MODEL=small\n")
        f.write(f"USE_GOOGLE_STT=False\n\n")
        f.write(f"# Bot Settings\n")
        f.write(f"COMMAND_PREFIX=!\n")
    
    print(f"✅ Created {env_file} file.")
    return True

def main():
    """Main function."""
    print_header("Voice Assistant Installation")
    print("This script will install all necessary dependencies for the Discord Voice Assistant.")
    
    # Check Python version
    check_python_version()
    
    # Check FFmpeg
    ffmpeg_installed = check_ffmpeg()
    if not ffmpeg_installed:
        print("⚠️ FFmpeg is required for audio processing. Please install it and run this script again.")
        print("⚠️ The installation will continue, but the bot won't work without FFmpeg.")
    
    # Install dependencies
    install_dependencies()
    
    # Create .env file
    create_env_file()
    
    print_header("Installation Complete")
    print("✅ Voice Assistant has been set up successfully!")
    print("\nTo start using the Voice Assistant:")
    print("1. Make sure you have configured your .env file with your Discord bot token and Azure TTS key")
    print("2. Start your Discord bot")
    print("3. Join a voice channel and use the '!استمع' command to start voice recognition")
    
    print("\nFor more information, refer to VOICE_ASSISTANT_README.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 