#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import re
import asyncio

class VoiceControl(commands.Cog):
    """التحكم بالقنوات الصوتية"""
    
    def __init__(self, bot):
        self.bot = bot
        self.volume_levels = {}  # تخزين مستويات الصوت لكل قناة
    
    @commands.command(
        name="صوت",
        aliases=["voice", "v", "انضمام_صوتي"],
        description="الانضمام إلى قناة صوتية أو التحكم بالصوت"
    )
    async def voice(self, ctx, *, channel_or_volume: str = None):
        """
        الانضمام إلى قناة صوتية أو ضبط مستوى الصوت
        
        المعلمات:
            channel_or_volume (str): اسم القناة أو معرفها أو مستوى الصوت (0-100)
        
        أمثلة:
            !صوت عام - للانضمام إلى قناة اسمها "عام"
            !صوت 50 - لضبط مستوى الصوت على 50%
        """
        # إذا لم يتم تحديد معلمات
        if not channel_or_volume:
            # التحقق مما إذا كان المستخدم في قناة صوتية
            if not ctx.author.voice:
                embed = discord.Embed(
                    title="❌ خطأ",
                    description="أنت لست في قناة صوتية! يرجى الانضمام إلى قناة صوتية أولاً أو تحديد اسم القناة.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
            
            # الانضمام إلى قناة المستخدم
            channel = ctx.author.voice.channel
            embed = await self._join_voice_channel(ctx, channel)
            return await ctx.send(embed=embed)
        
        # التحقق مما إذا كان المعلمة هي مستوى صوت
        if channel_or_volume.isdigit() or (channel_or_volume.startswith('-') and channel_or_volume[1:].isdigit()):
            # تغيير مستوى الصوت
            volume = int(channel_or_volume)
            embed = await self._set_volume(ctx, volume)
            return await ctx.send(embed=embed)
        
        # البحث عن القناة الصوتية
        channel = discord.utils.get(ctx.guild.voice_channels, name=channel_or_volume)
        
        # إذا لم يتم العثور على القناة، قد يكون معرف
        if not channel:
            try:
                # التحقق مما إذا كان معرف قناة
                if channel_or_volume.isdigit():
                    channel_id = int(channel_or_volume)
                    channel = discord.utils.get(ctx.guild.voice_channels, id=channel_id)
                
                # قد يكون منشن للقناة
                elif channel_or_volume.startswith('<#') and channel_or_volume.endswith('>'):
                    channel_id = int(channel_or_volume[2:-1])
                    channel = discord.utils.get(ctx.guild.voice_channels, id=channel_id)
            except:
                pass
        
        # إذا لم يتم العثور على القناة
        if not channel:
            embed = discord.Embed(
                title="❌ قناة غير موجودة",
                description=f"لم يتم العثور على قناة صوتية باسم أو معرف: {channel_or_volume}",
                color=discord.Color.red()
            )
            
            # عرض القنوات المتاحة
            voice_channels = ctx.guild.voice_channels
            if voice_channels:
                channels_list = "\n".join([f"• {vc.name}" for vc in voice_channels[:10]])
                if len(voice_channels) > 10:
                    channels_list += f"\n... و{len(voice_channels) - 10} قنوات أخرى"
                
                embed.add_field(
                    name="📢 القنوات الصوتية المتاحة:",
                    value=channels_list,
                    inline=False
                )
            
            return await ctx.send(embed=embed)
        
        # الانضمام إلى القناة المحددة
        embed = await self._join_voice_channel(ctx, channel)
        await ctx.send(embed=embed)
    
    @commands.command(
        name="صوت_دعوة",
        aliases=["voice_invite", "vi", "دعوة_صوت"],
        description="دعوة مستخدم إلى القناة الصوتية الحالية"
    )
    async def voice_invite(self, ctx, user: discord.Member = None):
        """
        دعوة مستخدم إلى القناة الصوتية الحالية
        
        المعلمات:
            user (discord.Member): المستخدم المراد دعوته
        """
        # التحقق من تحديد مستخدم
        if not user:
            embed = discord.Embed(
                title="❌ خطأ",
                description="يرجى تحديد المستخدم المراد دعوته إلى القناة الصوتية.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق مما إذا كان البوت في قناة صوتية
        if not ctx.guild.voice_client or not ctx.guild.voice_client.channel:
            # التحقق مما إذا كان المستخدم في قناة صوتية
            if not ctx.author.voice:
                embed = discord.Embed(
                    title="❌ خطأ",
                    description="أنت لست في قناة صوتية! يرجى الانضمام إلى قناة صوتية أولاً.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
            
            # الانضمام إلى قناة المستخدم
            channel = ctx.author.voice.channel
            await self._join_voice_channel(ctx, channel)
        
        # الحصول على القناة الصوتية الحالية
        voice_channel = ctx.guild.voice_client.channel
        
        # إنشاء رابط دعوة إلى القناة الصوتية
        try:
            # إنشاء دعوة للقناة الصوتية
            invite = await voice_channel.create_invite(
                max_age=60,  # 1 دقيقة
                max_uses=1,  # استخدام واحد فقط
                temporary=False,
                unique=True
            )
            
            # إرسال الدعوة إلى المستخدم
            embed = discord.Embed(
                title="🔊 دعوة إلى القناة الصوتية",
                description=f"{ctx.author.mention} يدعوك للانضمام إلى القناة الصوتية **{voice_channel.name}**",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📩 رابط الدعوة",
                value=f"[انقر هنا للانضمام]({invite.url})",
                inline=False
            )
            
            embed.set_footer(text="تنتهي صلاحية هذه الدعوة بعد دقيقة واحدة")
            
            # إرسال الدعوة إلى المستخدم في الخاص
            try:
                await user.send(embed=embed)
                
                # إرسال تأكيد إلى القناة
                confirm_embed = discord.Embed(
                    title="✅ تم إرسال الدعوة",
                    description=f"تم إرسال دعوة إلى {user.mention} للانضمام إلى القناة الصوتية **{voice_channel.name}**.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=confirm_embed)
            except discord.Forbidden:
                # إذا كان المستخدم لا يسمح بالرسائل الخاصة
                error_embed = discord.Embed(
                    title="❌ تعذر إرسال الدعوة",
                    description=f"تعذر إرسال الدعوة إلى {user.mention} لأنه لا يسمح بالرسائل الخاصة.\n\n"
                              f"رابط الدعوة: {invite.url}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=error_embed)
        
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ خطأ في الصلاحيات",
                description="ليس لدي صلاحية لإنشاء دعوة للقناة الصوتية.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ أثناء إنشاء الدعوة: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(
        name="غادر",
        aliases=["leave", "disconnect", "قطع"],
        description="مغادرة القناة الصوتية"
    )
    async def leave(self, ctx):
        """مغادرة القناة الصوتية الحالية"""
        # التحقق مما إذا كان البوت في قناة صوتية
        if not ctx.guild.voice_client:
            embed = discord.Embed(
                title="❌ خطأ",
                description="أنا لست في قناة صوتية!",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # الحصول على اسم القناة قبل المغادرة
        channel_name = ctx.guild.voice_client.channel.name
        
        # مغادرة القناة الصوتية
        await ctx.guild.voice_client.disconnect()
        
        # تنظيف البيانات
        if ctx.guild.id in self.volume_levels:
            del self.volume_levels[ctx.guild.id]
        
        # إرسال تأكيد
        embed = discord.Embed(
            title="👋 تمت المغادرة",
            description=f"تمت مغادرة القناة الصوتية **{channel_name}**.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    async def _join_voice_channel(self, ctx, channel):
        """الانضمام إلى قناة صوتية"""
        try:
            # إذا كان البوت متصلاً بالفعل
            if ctx.guild.voice_client:
                # إذا كان البوت في نفس القناة
                if ctx.guild.voice_client.channel.id == channel.id:
                    embed = discord.Embed(
                        title="ℹ️ معلومة",
                        description=f"أنا بالفعل في القناة الصوتية **{channel.name}**.",
                        color=discord.Color.blue()
                    )
                    
                    # إضافة معلومات مستوى الصوت
                    current_volume = self.volume_levels.get(ctx.guild.id, 100)
                    embed.add_field(
                        name="🔊 مستوى الصوت الحالي",
                        value=f"{current_volume}%",
                        inline=True
                    )
                    
                    return embed
                
                # الانتقال إلى القناة الجديدة
                await ctx.guild.voice_client.move_to(channel)
            else:
                # الانضمام إلى القناة
                await channel.connect()
            
            # تعيين مستوى الصوت الافتراضي
            self.volume_levels[ctx.guild.id] = 100
            
            # إعداد رسالة النجاح
            embed = discord.Embed(
                title="✅ تم الانضمام",
                description=f"تم الانضمام إلى القناة الصوتية **{channel.name}**.",
                color=discord.Color.green()
            )
            
            # إضافة معلومات القناة
            embed.add_field(
                name="👥 عدد الأعضاء",
                value=f"{len(channel.members) - 1} عضو",  # طرح 1 للبوت
                inline=True
            )
            
            embed.add_field(
                name="🔊 مستوى الصوت",
                value="100%",
                inline=True
            )
            
            return embed
        
        except discord.ClientException as e:
            return discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ أثناء الانضمام إلى القناة: {str(e)}",
                color=discord.Color.red()
            )
    
    async def _set_volume(self, ctx, volume):
        """ضبط مستوى الصوت"""
        # التحقق مما إذا كان البوت في قناة صوتية
        if not ctx.guild.voice_client:
            return discord.Embed(
                title="❌ خطأ",
                description="أنا لست في قناة صوتية! استخدم `!صوت [اسم القناة]` للانضمام أولاً.",
                color=discord.Color.red()
            )
        
        # التحقق من صحة مستوى الصوت
        if volume < 0:
            volume = 0
        elif volume > 100:
            volume = 100
        
        # تخزين مستوى الصوت
        self.volume_levels[ctx.guild.id] = volume
        
        # إذا كان البوت يشغل موسيقى، ضبط مستوى الصوت
        if hasattr(ctx.guild.voice_client, 'source') and ctx.guild.voice_client.source:
            ctx.guild.voice_client.source.volume = volume / 100
        
        # إنشاء رسالة تأكيد
        embed = discord.Embed(
            title="🔊 مستوى الصوت",
            description=f"تم ضبط مستوى الصوت على **{volume}%**.",
            color=discord.Color.blue()
        )
        
        # إضافة معلومات القناة
        embed.add_field(
            name="📢 القناة الصوتية",
            value=ctx.guild.voice_client.channel.name,
            inline=True
        )
        
        # إضافة شريط مستوى الصوت
        volume_bar = self._create_volume_bar(volume)
        embed.add_field(
            name="مستوى الصوت",
            value=volume_bar,
            inline=False
        )
        
        return embed
    
    def _create_volume_bar(self, volume):
        """إنشاء شريط مرئي لمستوى الصوت"""
        filled = int(volume / 5)  # 20 شريط كحد أقصى
        empty = 20 - filled
        
        bar = "▰" * filled + "▱" * empty
        return f"{bar} {volume}%"


async def setup(bot):
    """إعداد الأمر وإضافته إلى البوت"""
    await bot.add_cog(VoiceControl(bot)) 