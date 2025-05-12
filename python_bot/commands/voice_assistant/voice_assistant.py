#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import os
import io
import re
import wavelink
import speech_recognition as sr
import whisper
import azure.cognitiveservices.speech as speechsdk
from typing import Optional, List, Dict, Tuple
import tempfile
import numpy as np
import logging
import yt_dlp
import json
import time
from pydub import AudioSegment
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("voice_assistant.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("VoiceAssistant")

# Constants and configuration
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
AZURE_TTS_KEY = os.getenv("AZURE_TTS_KEY", "")
AZURE_REGION = os.getenv("AZURE_REGION", "eastus")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")  # small, medium, large models
USE_GOOGLE_STT = os.getenv("USE_GOOGLE_STT", "False").lower() == "true"

class VoiceAssistant(commands.Cog):
    """Discord Voice Assistant with voice recognition and TTS"""
    
    def __init__(self, bot):
        self.bot = bot
        self.voice_connections = {}  # guild_id -> VoiceConnection
        self.whisper_model = None
        self.recognizer = sr.Recognizer()
        self.is_listening = {}  # guild_id -> bool
        self.audio_queues = {}  # guild_id -> Queue
        self.should_stop = {}  # guild_id -> bool
        self.speakers = {
            "ar-SA": {
                "male": ["ar-SA-HamedNeural"],  # Arabic Saudi male voice
                "female": ["ar-SA-ZariyahNeural"]  # Arabic Saudi female voice
            },
            "en-US": {
                "male": ["en-US-GuyNeural"],
                "female": ["en-US-JennyNeural"]
            }
        }
        self.default_voice = "ar-SA-HamedNeural"  # Default voice - Arabic Saudi male
        self.command_patterns = {
            "play": [
                r"شغل (.+)",
                r"تشغيل (.+)",
                r"ابي اسمع (.+)",
                r"ابغى اسمع (.+)",
                r"حط لي (.+)",
                r"حط (.+)",
                r"شغلي (.+)",
                r"play (.+)"
            ],
            "stop": [
                r"وقف",
                r"توقف",
                r"أوقف",
                r"ايقاف",
                r"إيقاف",
                r"stop"
            ],
            "next": [
                r"التالي",
                r"التالية",
                r"الي بعده",
                r"الي بعدها",
                r"اللي بعده",
                r"اللي بعدها",
                r"next",
                r"skip"
            ],
            "pause": [
                r"وقف مؤقت",
                r"توقف مؤقت",
                r"إيقاف مؤقت",
                r"ايقاف مؤقت",
                r"pause"
            ],
            "resume": [
                r"كمل",
                r"استمر",
                r"استكمال",
                r"واصل",
                r"resume"
            ],
            "volume": [
                r"صوت (\d+)",
                r"مستوى الصوت (\d+)",
                r"حجم الصوت (\d+)",
                r"ارفع الصوت",
                r"نزل الصوت",
                r"volume (\d+)",
                r"جيب الصوت على (\d+)"
            ]
        }
        self.initialize_whisper()
    
    def initialize_whisper(self):
        """Initialize the Whisper model for speech recognition"""
        logger.info(f"Initializing Whisper model: {WHISPER_MODEL}")
        try:
            self.whisper_model = whisper.load_model(WHISPER_MODEL)
            logger.info(f"Whisper model loaded successfully: {WHISPER_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            logger.warning("Voice recognition with Whisper will not be available")
    
    async def azure_tts(self, text, filename=None, voice_name=None):
        """Generate speech from text using Azure Text-to-Speech"""
        if not AZURE_TTS_KEY or AZURE_TTS_KEY == "":
            logger.error("Azure TTS key is not configured")
            return None
        
        try:
            # Configure speech configuration
            speech_config = speechsdk.SpeechConfig(subscription=AZURE_TTS_KEY, region=AZURE_REGION)
            
            # Use default voice if none specified
            voice_name = voice_name or self.default_voice
            speech_config.speech_synthesis_voice_name = voice_name
            
            # Create temp file if filename not provided
            if not filename:
                fd, filename = tempfile.mkstemp(suffix='.wav')
                os.close(fd)
            
            # Configure audio output to a file
            audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)
            
            # Create speech synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            
            # Synthesize text to speech
            result = synthesizer.speak_text_async(text).get()
            
            # Check result
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info(f"Speech synthesis completed: {filename}")
                return filename
            else:
                logger.error(f"Speech synthesis failed: {result.reason}")
                if result.cancellation_details:
                    logger.error(f"Speech synthesis canceled: {result.cancellation_details.reason}")
                    if result.cancellation_details.reason == speechsdk.CancellationReason.Error:
                        logger.error(f"Error details: {result.cancellation_details.error_details}")
                return None
                
        except Exception as e:
            logger.error(f"Azure TTS error: {str(e)}")
            return None
    
    async def play_audio_file(self, voice_client, file_path):
        """Play an audio file in the voice channel"""
        if not voice_client or not voice_client.is_connected():
            logger.error("Cannot play audio: Voice client not connected")
            return False
        
        try:
            # Create the audio source from the file
            source = discord.FFmpegPCMAudio(file_path)
            
            # Play the audio in the voice channel
            if voice_client.is_playing():
                voice_client.stop()
            
            voice_client.play(source)
            
            # Wait for the audio to finish
            while voice_client.is_playing():
                await asyncio.sleep(0.5)
            
            return True
            
        except Exception as e:
            logger.error(f"Error playing audio file: {str(e)}")
            return False
    
    async def transcribe_with_whisper(self, audio_data, language="ar"):
        """Transcribe audio data using Whisper"""
        if not self.whisper_model:
            logger.error("Whisper model not initialized")
            return None
        
        try:
            # Convert audio data to a format compatible with Whisper
            # This assumes audio_data is in PCM format from Discord
            # We need to write it to a temporary file and read it back
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            # Write audio data to WAV file
            with open(temp_filename, 'wb') as f:
                f.write(audio_data)
            
            # Use Whisper to transcribe the audio
            result = self.whisper_model.transcribe(temp_filename, language=language)
            
            # Clean up the temporary file
            try:
                os.unlink(temp_filename)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {str(e)}")
            
            return result["text"].strip()
            
        except Exception as e:
            logger.error(f"Whisper transcription error: {str(e)}")
            return None
    
    async def transcribe_with_google(self, audio_data):
        """Transcribe audio data using Google Speech Recognition"""
        if not self.recognizer:
            return None
        
        try:
            # Convert audio data to a format compatible with speech_recognition
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            # Write audio data to WAV file
            with open(temp_filename, 'wb') as f:
                f.write(audio_data)
            
            # Read audio from the file
            with sr.AudioFile(temp_filename) as source:
                audio = self.recognizer.record(source)
            
            # Transcribe using Google
            text = self.recognizer.recognize_google(audio, language="ar-AR")
            
            # Clean up the temporary file
            try:
                os.unlink(temp_filename)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {str(e)}")
            
            return text.strip()
            
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            return None
            
        except sr.RequestError as e:
            logger.error(f"Google Speech Recognition service error: {str(e)}")
            return None
            
        except Exception as e:
            logger.error(f"Google transcription error: {str(e)}")
            return None
    
    def parse_command(self, text):
        """Parse voice command from transcribed text"""
        if not text:
            return None, None
        
        # Check for each command pattern
        for command, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # For commands that may have parameters
                    if len(match.groups()) > 0:
                        return command, match.group(1)
                    return command, None
        
        # No command found
        return None, None
    
    async def process_command(self, ctx, command, param):
        """Process the parsed command"""
        guild_id = ctx.guild.id
        voice_client = ctx.voice_client
        
        if not voice_client:
            return "لست متصل بقناة صوتية"
        
        if command == "play":
            if not param:
                return "لم أفهم ماذا تريد أن أشغل"
            
            # Generate response first
            response = f"أكيد، راح أشغل لك {param}"
            
            # Respond with TTS
            await self.respond_with_tts(ctx, response)
            
            # Play the requested song
            await self.play_song(ctx, param)
            return None
            
        elif command == "stop":
            # Stop the player
            player = self.bot.wavelink.get_player(guild_id)
            if player:
                await player.disconnect()
                return "تم إيقاف التشغيل"
            return "لا يوجد محتوى قيد التشغيل"
            
        elif command == "next":
            # Skip to next song
            player = self.bot.wavelink.get_player(guild_id)
            if player and player.is_playing():
                await player.stop()
                return "جاري تشغيل المحتوى التالي"
            return "لا يوجد محتوى قيد التشغيل"
            
        elif command == "pause":
            # Pause playback
            player = self.bot.wavelink.get_player(guild_id)
            if player and player.is_playing():
                await player.pause()
                return "تم إيقاف التشغيل مؤقتًا"
            return "لا يوجد محتوى قيد التشغيل"
            
        elif command == "resume":
            # Resume playback
            player = self.bot.wavelink.get_player(guild_id)
            if player and player.is_paused():
                await player.resume()
                return "تم استئناف التشغيل"
            return "المحتوى ليس متوقفًا مؤقتًا"
            
        elif command == "volume":
            # Set volume
            player = self.bot.wavelink.get_player(guild_id)
            if player:
                try:
                    volume = int(param) if param else 70
                    volume = max(0, min(100, volume))
                    await player.set_volume(volume)
                    return f"تم ضبط مستوى الصوت على {volume}%"
                except ValueError:
                    # Handle directional volume changes
                    if param in ["ارفع", "زود", "زيد"]:
                        current_volume = player.volume
                        new_volume = min(100, current_volume + 20)
                        await player.set_volume(new_volume)
                        return f"تم رفع مستوى الصوت إلى {new_volume}%"
                    elif param in ["نزل", "خفض", "قلل"]:
                        current_volume = player.volume
                        new_volume = max(0, current_volume - 20)
                        await player.set_volume(new_volume)
                        return f"تم خفض مستوى الصوت إلى {new_volume}%"
                    return "لم أفهم مستوى الصوت المطلوب"
            return "لا يوجد مشغل صوت نشط"
        
        # Unknown command
        return "لم أفهم الأمر"
    
    async def respond_with_tts(self, ctx, response_text):
        """Respond with text-to-speech in the voice channel"""
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            logger.error("Cannot respond: Not connected to voice channel")
            return
        
        try:
            # Create temporary file for TTS audio
            fd, temp_filename = tempfile.mkstemp(suffix='.wav')
            os.close(fd)
            
            # Generate TTS audio
            tts_file = await self.azure_tts(response_text, temp_filename)
            
            if not tts_file:
                logger.error("TTS generation failed")
                return
            
            # Play the TTS response
            await self.play_audio_file(ctx.voice_client, tts_file)
            
            # Clean up the temporary file
            try:
                os.unlink(temp_filename)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in voice response: {str(e)}")
    
    async def play_song(self, ctx, search_query):
        """Play a song based on the search query"""
        # Make sure we're connected to a voice channel
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            logger.error("Cannot play song: Not connected to voice channel")
            return
        
        try:
            # Get the music player cog
            music_cog = self.bot.get_cog("MusicPlayer")
            if not music_cog:
                logger.error("MusicPlayer cog not found")
                await ctx.send("⚠️ لم أتمكن من العثور على مشغل الموسيقى")
                return
            
            # Use the existing play command in the music cog
            # This will handle searching on YouTube, loading, and playing the track
            await music_cog.play(ctx, query=search_query)
            
        except Exception as e:
            logger.error(f"Error playing song: {str(e)}")
            await ctx.send(f"❌ حدث خطأ أثناء تشغيل الأغنية: {str(e)}")
    
    async def start_listening(self, ctx):
        """Start listening to voice input in a voice channel"""
        if not ctx.author.voice:
            await ctx.send("❌ يجب أن تكون في قناة صوتية لاستخدام هذا الأمر")
            return False
        
        guild_id = ctx.guild.id
        
        # Check if already listening in this guild
        if guild_id in self.is_listening and self.is_listening[guild_id]:
            await ctx.send("👂 أنا بالفعل أستمع في هذه القناة الصوتية")
            return False
        
        # Join the voice channel
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(voice_channel)
            voice_client = ctx.voice_client
        else:
            try:
                voice_client = await voice_channel.connect()
            except discord.ClientException as e:
                await ctx.send(f"❌ لم أتمكن من الانضمام إلى القناة الصوتية: {str(e)}")
                return False
        
        # Signal that we're listening
        self.is_listening[guild_id] = True
        self.should_stop[guild_id] = False
        
        # Initialize audio queue
        if guild_id not in self.audio_queues:
            self.audio_queues[guild_id] = asyncio.Queue()
        
        # Respond with TTS
        await self.respond_with_tts(ctx, "مرحباً، أنا الآن أستمع إلى طلباتك الصوتية. يمكنك طلب تشغيل أغنية مثل 'شغل أغنية نانسي يا سلام'")
        
        # Start the listener
        listener_task = asyncio.create_task(self._listen_to_voice(ctx, voice_client))
        
        # Start the processor
        processor_task = asyncio.create_task(self._process_voice_audio(ctx))
        
        return True
    
    async def stop_listening(self, ctx):
        """Stop listening to voice input"""
        guild_id = ctx.guild.id
        
        if guild_id not in self.is_listening or not self.is_listening[guild_id]:
            await ctx.send("❌ أنا لست في وضع الاستماع حاليًا")
            return False
        
        # Signal to stop listening
        self.should_stop[guild_id] = True
        self.is_listening[guild_id] = False
        
        # Respond with TTS
        await self.respond_with_tts(ctx, "حسناً، توقفت عن الاستماع. يمكنك استدعائي مرة أخرى باستخدام أمر استمع")
        
        return True
    
    async def _listen_to_voice(self, ctx, voice_client):
        """Listen to voice in the voice channel and queue audio packets"""
        guild_id = ctx.guild.id
        
        # Make sure we're connected and listening
        if not voice_client or not voice_client.is_connected() or not self.is_listening.get(guild_id, False):
            logger.error("Voice client not connected or not listening")
            return
        
        logger.info(f"Starting voice listening in guild {guild_id}")
        
        # Set up a sink to record audio
        sink = discord.sinks.WaveSink()
        
        # Start recording
        voice_client.start_recording(
            sink,
            self._recording_finished,
            ctx
        )
        
        # Wait until stop is requested
        while not self.should_stop.get(guild_id, True):
            await asyncio.sleep(0.5)
        
        # Stop recording
        voice_client.stop_recording()
        logger.info(f"Stopped voice listening in guild {guild_id}")
    
    async def _process_voice_audio(self, ctx):
        """Process the voice audio from the queue"""
        guild_id = ctx.guild.id
        
        logger.info(f"Starting voice audio processor for guild {guild_id}")
        
        # Process audio while we're still listening
        while self.is_listening.get(guild_id, False):
            try:
                # Get audio data from the queue (with timeout)
                try:
                    audio_data = await asyncio.wait_for(
                        self.audio_queues[guild_id].get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Skip processing if we're no longer listening
                if not self.is_listening.get(guild_id, False):
                    break
                
                # Transcribe the audio
                if USE_GOOGLE_STT:
                    transcript = await self.transcribe_with_google(audio_data)
                else:
                    transcript = await self.transcribe_with_whisper(audio_data)
                
                if not transcript:
                    logger.debug("No transcript detected")
                    continue
                
                logger.info(f"Transcribed: {transcript}")
                
                # Parse and process command
                command, param = self.parse_command(transcript)
                
                if command:
                    logger.info(f"Detected command: {command}, param: {param}")
                    
                    # Process the command
                    response = await self.process_command(ctx, command, param)
                    
                    # Respond if needed
                    if response:
                        await self.respond_with_tts(ctx, response)
                
            except Exception as e:
                logger.error(f"Error processing voice audio: {str(e)}")
                await asyncio.sleep(1)
        
        logger.info(f"Stopped voice audio processor for guild {guild_id}")
    
    def _recording_finished(self, sink, ctx):
        """Callback when a recording is finished"""
        # Check if we're still listening
        guild_id = ctx.guild.id
        if not self.is_listening.get(guild_id, False):
            return
        
        # Retrieve audio data for the bot's user
        for user_id, audio in sink.audio_data.items():
            # Skip the bot's own audio
            if user_id == self.bot.user.id:
                continue
            
            # Queue the audio data for processing
            if guild_id in self.audio_queues:
                asyncio.run_coroutine_threadsafe(
                    self.audio_queues[guild_id].put(audio.file.getvalue()),
                    self.bot.loop
                )
    
    @commands.command(
        name="استمع",
        aliases=["listen", "voice", "صوت"],
        description="بدء الاستماع للأوامر الصوتية"
    )
    async def listen_command(self, ctx):
        """بدء الاستماع للأوامر الصوتية في قناة صوتية"""
        success = await self.start_listening(ctx)
        if success:
            embed = discord.Embed(
                title="🎧 وضع الاستماع",
                description="بدأت الاستماع للأوامر الصوتية. يمكنك الآن التحدث بأوامر مثل:\n\n" +
                            "- شغل أغنية نانسي عجرم يا سلام\n" +
                            "- وقف\n" +
                            "- التالي\n" +
                            "- صوت 50",
                color=discord.Color.green()
            )
            embed.set_footer(text="استخدم أمر 'توقف' للخروج من وضع الاستماع")
            await ctx.send(embed=embed)
    
    @commands.command(
        name="توقف",
        aliases=["stop_listen", "قف"],
        description="إيقاف الاستماع للأوامر الصوتية"
    )
    async def stop_listen_command(self, ctx):
        """إيقاف الاستماع للأوامر الصوتية"""
        success = await self.stop_listening(ctx)
        if success:
            embed = discord.Embed(
                title="🔇 إيقاف الاستماع",
                description="توقفت عن الاستماع للأوامر الصوتية.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    """إعداد الصنف"""
    await bot.add_cog(VoiceAssistant(bot)) 