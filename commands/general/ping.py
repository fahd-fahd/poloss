#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import time

class Ping(commands.Cog):
    """أوامر التشخيص والحالة"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name="بنج",
        aliases=["ping", "latency", "زمن_الاستجابة"],
        description="عرض زمن استجابة البوت"
    )
    async def ping(self, ctx):
        """
        قياس زمن استجابة البوت والاتصال بـ Discord API
        """
        # قياس الوقت المستغرق لإرسال رسالة والحصول على رد
        start_time = time.time()
        message = await ctx.send("جاري قياس زمن الاستجابة...")
        end_time = time.time()
        
        # حساب زمن الاستجابة بالمللي ثانية
        message_latency = round((end_time - start_time) * 1000)
        
        # الحصول على زمن استجابة Discord API من البوت
        api_latency = round(self.bot.latency * 1000)
        
        # إنشاء رسالة مضمنة لعرض النتائج
        embed = discord.Embed(
            title="🏓 بنج",
            description="قياس زمن استجابة البوت",
            color=discord.Color.green() if api_latency < 200 else discord.Color.orange()
        )
        
        # إضافة معلومات زمن الاستجابة
        embed.add_field(
            name="⏱️ زمن الرسالة",
            value=f"**{message_latency}** مللي ثانية",
            inline=True
        )
        
        embed.add_field(
            name="🌐 زمن Discord API",
            value=f"**{api_latency}** مللي ثانية",
            inline=True
        )
        
        # إضافة رمز تعبيري بناءً على زمن الاستجابة
        status_emoji = "🟢" if api_latency < 100 else "🟡" if api_latency < 200 else "🔴"
        embed.add_field(
            name="📊 الحالة",
            value=f"{status_emoji} " + (
                "ممتاز" if api_latency < 100 else
                "جيد" if api_latency < 200 else
                "بطيء"
            ),
            inline=True
        )
        
        # إضافة تذييل بمعلومات النسخة
        embed.set_footer(text=f"Discord.py v{discord.__version__}")
        
        # تحديث الرسالة السابقة بالرسالة المضمنة
        await message.edit(content=None, embed=embed)

async def setup(bot):
    """إعداد الأمر وإضافته إلى البوت"""
    await bot.add_cog(Ping(bot)) 