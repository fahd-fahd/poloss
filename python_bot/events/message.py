#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import asyncio
import discord
from discord.ext import commands

from utils.prefix_helper import has_valid_prefix, get_used_prefix
from utils.user_settings import save_last_command

class MessageEvents(commands.Cog):
    """معالج أحداث الرسائل"""
    
    def __init__(self, bot):
        self.bot = bot
        self.prefix = os.getenv("PREFIX", "!")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """معالجة جميع الرسائل الواردة"""
        # تجاهل الرسائل الذاتية
        if message.author.bot:
            return
        
        # التحقق من وجود البادئة الصحيحة
        if not has_valid_prefix(message, self.bot.config):
            # معالجة المحادثة العادية - يمكن إضافة المزيد من المنطق هنا
            return
        
        # الحصول على البادئة المستخدمة في الرسالة
        used_prefix = get_used_prefix(message, self.bot.config)
        if not used_prefix:
            return
            
        # استخراج الأمر والمعلمات
        command_name, *args = message.content[len(used_prefix):].split()
        command_name = command_name.lower()
        
        # التحقق من القناة المسموح بها
        if not self._is_allowed_channel(message.channel.id):
            if self.bot.config.get('channels', {}).get('sendWarningMessage', True):
                warning_msg = self.bot.config.get('channels', {}).get(
                    'warningMessage', 
                    'عذراً، لا يمكنني الاستجابة للأوامر في هذه القناة.'
                )
                await message.reply(warning_msg, delete_after=5)
            return
        
        # حفظ الأمر في سجل المستخدم
        clean_command = message.content.strip()
        save_last_command(message.author.id, clean_command)
        
        # البوت سيعالج الأمر من خلال نظام الأوامر الأساسي
        # لا نحتاج إلى فعل أي شيء إضافي هنا
        # لأن البوت سيعالج الرسالة تلقائيًا بواسطة discord.py
    
    def _is_allowed_channel(self, channel_id):
        """التحقق مما إذا كانت القناة مسموح بها للأوامر"""
        # القنوات المسموح بها للأوامر
        channels_config = self.bot.config.get('channels', {})
        
        # إذا كان التقييد غير مفعل، اسمح بجميع القنوات
        if not channels_config.get('restrictToAllowedChannels', True):
            return True
        
        # تحويل channel_id إلى نص للمقارنة مع قائمة النصوص
        channel_id_str = str(channel_id)
        
        # التحقق من وجود القناة في قائمة القنوات المسموح بها
        allowed_channels = channels_config.get('allowedCommandChannels', [])
        
        # أيضًا التحقق من قائمة قنوات الدردشة
        allowed_chat_channels = channels_config.get('allowedChatChannels', [])
        
        return channel_id_str in allowed_channels or channel_id_str in allowed_chat_channels

async def setup(bot):
    """إعداد الصنف وإضافته إلى البوت"""
    await bot.add_cog(MessageEvents(bot)) 