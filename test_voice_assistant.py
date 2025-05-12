#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Voice Assistant Test Script
This script performs tests to validate the voice assistant setup.
"""

import os
import sys
import subprocess
import importlib.util
import platform
import time

def print_header(text):
    """Print a header with the given text."""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def test_imports():
    """Test importing required modules."""
    print_header("Testing module imports")
    
    modules = [
        ("discord", "Discord.py is required for the bot"),
        ("speech_recognition", "SpeechRecognition is required for voice commands"),
        ("whisper", "OpenAI Whisper is required for speech-to-text"),
        ("azure.cognitiveservices.speech", "Azure Cognitive Services is required for TTS"),
        ("numpy", "Numpy is required for audio processing"),
        ("yt_dlp", "yt-dlp is required for YouTube downloads"),
        ("pydub", "Pydub is required for audio processing"),
        ("ffmpeg", "FFmpeg Python is required for audio conversion"),
        ("dotenv", "python-dotenv is required for environment variables"),
    ]
    
    all_passed = True
    for module_name, description in modules:
        try:
            # Try to import the module
            __import__(module_name)
            print(f"✅ {module_name}: Successfully imported")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            print(f"   {description}")
            all_passed = False
    
    return all_passed

def test_ffmpeg():
    """Test FFmpeg installation."""
    print_header("Testing FFmpeg")
    
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg is installed: {version}")
            return True
        else:
            print(f"❌ FFmpeg returned non-zero exit code: {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Failed to check FFmpeg: {e}")
        return False

def test_discord_token():
    """Test Discord bot token configuration."""
    print_header("Testing Discord token configuration")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ DISCORD_BOT_TOKEN not found in environment variables.")
        print("Please set up your .env file with a valid Discord bot token.")
        return False
    elif len(token) < 50:
        print("⚠️ DISCORD_BOT_TOKEN is set, but may not be valid (too short).")
        print("Please check that your token is correct.")
        return False
    else:
        print("✅ DISCORD_BOT_TOKEN is set.")
        return True

def test_azure_tts():
    """Test Azure TTS configuration."""
    print_header("Testing Azure TTS configuration")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    key = os.getenv("AZURE_TTS_KEY")
    region = os.getenv("AZURE_REGION")
    
    if not key:
        print("❌ AZURE_TTS_KEY not found in environment variables.")
        print("Text-to-speech functionality will not work.")
        return False
    else:
        print("✅ AZURE_TTS_KEY is set.")
    
    if not region:
        print("❌ AZURE_REGION not found in environment variables.")
        print("Using default region: eastus")
    else:
        print(f"✅ AZURE_REGION is set to: {region}")
    
    # Try to import the Azure Speech SDK
    try:
        import azure.cognitiveservices.speech as speechsdk
        print("✅ Azure Speech SDK imported successfully.")
        
        # Optional: Test creating a speech synthesizer (commented out to avoid API calls during test)
        # speech_config = speechsdk.SpeechConfig(subscription=key, region=region or "eastus")
        # synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        # print("✅ Speech synthesizer created successfully.")
        
        return True
    except Exception as e:
        print(f"❌ Azure Speech SDK error: {e}")
        return False

def test_whisper():
    """Test Whisper installation."""
    print_header("Testing Whisper installation")
    
    try:
        import whisper
        print("✅ Whisper imported successfully.")
        
        # Check if we can load a model (don't actually load it, as it's large)
        print("ℹ️ Whisper models will be downloaded on first use.")
        print("ℹ️ Available models: tiny, base, small, medium, large")
        print("ℹ️ Model loading not tested (to avoid large downloads during test).")
        
        return True
    except Exception as e:
        print(f"❌ Whisper error: {e}")
        return False

def test_voice_assistant_files():
    """Test Voice Assistant files."""
    print_header("Testing Voice Assistant files")
    
    files = [
        "python_bot/commands/voice_assistant/voice_assistant.py",
        "python_bot/commands/voice_assistant/__init__.py",
    ]
    
    all_found = True
    for file_path in files:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_found = False
    
    return all_found

def main():
    print_header("Voice Assistant Test Script")
    print("This script tests the voice assistant dependencies and configuration.")
    
    test_results = {
        "Imports": test_imports(),
        "FFmpeg": test_ffmpeg(),
        "Discord Token": test_discord_token(),
        "Azure TTS": test_azure_tts(),
        "Whisper": test_whisper(),
        "Voice Assistant Files": test_voice_assistant_files()
    }
    
    print_header("Test Results Summary")
    all_passed = True
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! The Voice Assistant is ready to use.")
        print("\nTo start the Voice Assistant:")
        print("1. Run your Discord bot")
        print("2. Join a voice channel and use the '!استمع' command")
    else:
        print("\n⚠️ Some tests failed. Please fix the issues before using the Voice Assistant.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 