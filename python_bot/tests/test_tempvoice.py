#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار وظائف نظام الغرف الصوتية المؤقتة
"""

import unittest
import asyncio
import discord
from discord.ext import commands
import sys
import os
from pathlib import Path

# إضافة المجلد الرئيسي إلى مسار البحث
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

# استيراد الوحدة المراد اختبارها
from python_bot.commands.music.tempvoice import TempVoice, MusicControlView, MusicURLModal


class TestTempVoice(unittest.TestCase):
    """اختبار وظائف نظام الغرف الصوتية المؤقتة"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        self.bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
        self.cog = TempVoice(self.bot)
    
    def test_initialization(self):
        """اختبار التهيئة الأولية"""
        self.assertEqual(self.cog.create_channel_name, "إنشاء غرفة صوتية")
        self.assertEqual(self.cog.temp_channels, {})
        self.assertEqual(self.cog.song_queue, {})
        self.assertEqual(self.cog.now_playing, {})
    
    def test_format_duration(self):
        """اختبار تنسيق المدة الزمنية"""
        # اختبار مدة قصيرة (أقل من ساعة)
        duration_short = 125000  # 2:05 (دقيقتان و5 ثوان)
        self.assertEqual(self.cog._format_duration(duration_short), "2:05")
        
        # اختبار مدة طويلة (أكثر من ساعة)
        duration_long = 3665000  # 1:01:05 (ساعة ودقيقة و5 ثوان)
        self.assertEqual(self.cog._format_duration(duration_long), "1:01:05")
    
    # اختبارات إضافية تتطلب محاكاة بيئة Discord
    # ملاحظة: هذه الاختبارات تحتاج إلى مكتبات إضافية مثل unittest.mock
    # لمحاكاة كائنات Discord


class TestMusicControlView(unittest.TestCase):
    """اختبار واجهة التحكم بالموسيقى"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        self.bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
        self.view = MusicControlView(self.bot, 123456789, 987654321)
    
    def test_initialization(self):
        """اختبار التهيئة الأولية"""
        self.assertEqual(self.view.voice_channel_id, 123456789)
        self.assertEqual(self.view.text_channel_id, 987654321)
        self.assertIsNone(self.view.url_input)
        
        # التحقق من وجود زر التشغيل
        play_button = None
        for item in self.view.children:
            if item.custom_id == "temp_voice_play":
                play_button = item
                break
        
        self.assertIsNotNone(play_button)
        self.assertEqual(play_button.label, "تشغيل")
        self.assertEqual(play_button.style, discord.ButtonStyle.green)


if __name__ == "__main__":
    unittest.main() 