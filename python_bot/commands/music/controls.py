#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import wavelink
import asyncio
from discord.ui import Button, View

class VolumeView(View):
    """عرض أزرار التحكم في الصوت"""
    
    def __init__(self, bot, ctx, player, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
        self.player = player
        self.current_volume = player.volume
    
    @discord.ui.button(emoji="🔉", style=discord.ButtonStyle.secondary)
    async def volume_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        """خفض الصوت"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب الأمر فقط.", ephemeral=True)
            
        # خفض الصوت بنسبة 10%
        new_volume = max(0, self.player.volume - 10)
        await self.player.set_volume(new_volume)
        self.current_volume = new_volume
        
        # تحديث رسالة الصوت
        embed = discord.Embed(
            title="🔊 مستوى الصوت",
            description=f"تم تعديل مستوى الصوت إلى **{new_volume}%**",
            color=discord.Color.blue()
        )
        embed.add_field(name="الحالة", value=self._create_volume_bar(new_volume), inline=False)
        
        await interaction.response.edit_message(embed=embed)
    
    @discord.ui.button(emoji="🔊", style=discord.ButtonStyle.secondary)
    async def volume_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        """رفع الصوت"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب الأمر فقط.", ephemeral=True)
            
        # رفع الصوت بنسبة 10%
        new_volume = min(100, self.player.volume + 10)
        await self.player.set_volume(new_volume)
        self.current_volume = new_volume
        
        # تحديث رسالة الصوت
        embed = discord.Embed(
            title="🔊 مستوى الصوت",
            description=f"تم تعديل مستوى الصوت إلى **{new_volume}%**",
            color=discord.Color.blue()
        )
        embed.add_field(name="الحالة", value=self._create_volume_bar(new_volume), inline=False)
        
        await interaction.response.edit_message(embed=embed)
    
    @discord.ui.button(emoji="🔇", style=discord.ButtonStyle.danger)
    async def volume_mute(self, interaction: discord.Interaction, button: discord.ui.Button):
        """كتم الصوت"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب الأمر فقط.", ephemeral=True)
        
        if self.player.volume > 0:
            # حفظ مستوى الصوت الحالي وكتم الصوت
            self.current_volume = self.player.volume
            await self.player.set_volume(0)
            button.emoji = "🔈"
            button.label = "إلغاء الكتم"
        else:
            # استعادة مستوى الصوت
            await self.player.set_volume(self.current_volume)
            button.emoji = "🔇"
            button.label = None
        
        # تحديث رسالة الصوت
        embed = discord.Embed(
            title="🔊 مستوى الصوت",
            description=f"تم تعديل مستوى الصوت إلى **{self.player.volume}%**",
            color=discord.Color.blue()
        )
        embed.add_field(name="الحالة", value=self._create_volume_bar(self.player.volume), inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    def _create_volume_bar(self, volume):
        """إنشاء شريط مرئي لمستوى الصوت"""
        filled_blocks = int(volume / 10)
        empty_blocks = 10 - filled_blocks
        
        bar = "▰" * filled_blocks + "▱" * empty_blocks
        return f"{bar} {volume}%"

class NowPlayingView(View):
    """عرض أزرار التحكم للأغنية الحالية"""
    
    def __init__(self, bot, ctx, player, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
        self.player = player
    
    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.primary)
    async def previous_song(self, interaction: discord.Interaction, button: discord.ui.Button):
        """الرجوع للأغنية السابقة"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب الأمر فقط.", ephemeral=True)
        
        # الحصول على مرجع لنظام تشغيل الموسيقى
        music_cog = self.bot.get_cog("MusicPlayer")
        if not music_cog:
            return await interaction.response.send_message("لم يتم العثور على نظام تشغيل الموسيقى.", ephemeral=True)
        
        # التحقق من وجود أغنية سابقة
        if not hasattr(music_cog, 'previous_track') or not music_cog.previous_track.get(interaction.guild.id):
            return await interaction.response.send_message("لا توجد أغنية سابقة للرجوع إليها.", ephemeral=True)
        
        # تشغيل الأغنية السابقة
        prev_track = music_cog.previous_track[interaction.guild.id]
        await self.player.play(prev_track)
        
        await interaction.response.send_message("⏮️ تم الرجوع إلى الأغنية السابقة.", ephemeral=True)
    
    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.primary)
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        """إيقاف مؤقت / استئناف التشغيل"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب الأمر فقط.", ephemeral=True)
        
        if self.player.is_paused():
            await self.player.resume()
            await interaction.response.send_message("▶️ تم استئناف التشغيل.", ephemeral=True)
        else:
            await self.player.pause()
            await interaction.response.send_message("⏸️ تم إيقاف التشغيل مؤقتًا.", ephemeral=True)
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.primary)
    async def skip_song(self, interaction: discord.Interaction, button: discord.ui.Button):
        """تخطي الأغنية الحالية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب الأمر فقط.", ephemeral=True)
        
        await self.player.stop()
        await interaction.response.send_message("⏭️ تم تخطي الأغنية الحالية.", ephemeral=True)
    
    @discord.ui.button(emoji="🔊", style=discord.ButtonStyle.secondary)
    async def volume_control(self, interaction: discord.Interaction, button: discord.ui.Button):
        """التحكم في مستوى الصوت"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب الأمر فقط.", ephemeral=True)
        
        embed = discord.Embed(
            title="🔊 مستوى الصوت",
            description=f"المستوى الحالي: **{self.player.volume}%**\n"
                      f"استخدم الأزرار أدناه لضبط مستوى الصوت.",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="الحالة", value=self._create_volume_bar(self.player.volume), inline=False)
        
        volume_view = VolumeView(self.bot, self.ctx, self.player)
        await interaction.response.send_message(embed=embed, view=volume_view, ephemeral=True)
    
    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger)
    async def stop_playing(self, interaction: discord.Interaction, button: discord.ui.Button):
        """إيقاف التشغيل ومغادرة القناة الصوتية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب الأمر فقط.", ephemeral=True)
        
        # الحصول على مرجع لنظام تشغيل الموسيقى
        music_cog = self.bot.get_cog("MusicPlayer")
        
        # إعادة تعيين قوائم الأغاني
        if music_cog:
            if interaction.guild.id in music_cog.song_queue:
                music_cog.song_queue[interaction.guild.id] = []
            
            if interaction.guild.id in music_cog.now_playing:
                del music_cog.now_playing[interaction.guild.id]
        
        # إيقاف التشغيل ومغادرة القناة
        await self.player.disconnect()
        
        await interaction.response.send_message("⏹️ تم إيقاف التشغيل ومغادرة القناة الصوتية.", ephemeral=True)
        
        # إيقاف عرض الأزرار
        self.stop()
    
    def _create_volume_bar(self, volume):
        """إنشاء شريط مرئي لمستوى الصوت"""
        filled_blocks = int(volume / 10)
        empty_blocks = 10 - filled_blocks
        
        bar = "▰" * filled_blocks + "▱" * empty_blocks
        return f"{bar} {volume}%"

class MusicControls(commands.Cog):
    """أوامر التحكم في مشغل الموسيقى"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name="الآن",
        aliases=["np", "nowplaying", "الان", "حاليا"],
        description="عرض معلومات الأغنية الحالية مع أزرار التحكم"
    )
    async def now_playing(self, ctx):
        """
        عرض معلومات الأغنية الحالية مع أزرار التحكم
        """
        # التحقق من وجود تشغيل حالي
        player = wavelink.NodePool.get_node().get_player(ctx.guild.id)
        
        if not player or not player.is_playing():
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا توجد أغنية قيد التشغيل حاليًا.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # الحصول على مرجع لنظام تشغيل الموسيقى
        music_cog = self.bot.get_cog("MusicPlayer")
        
        if not music_cog or ctx.guild.id not in music_cog.now_playing:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا توجد معلومات عن الأغنية الحالية.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
            
        # الحصول على معلومات الأغنية الحالية
        current_track = music_cog.now_playing[ctx.guild.id]
        
        # إنشاء رسالة مضمنة مع معلومات الأغنية
        embed = discord.Embed(
            title="🎵 الآن يتم تشغيل",
            description=f"**{current_track.title}**",
            color=discord.Color.blue()
        )
        
        # إضافة معلومات إضافية
        embed.add_field(name="المدة", value=self._format_duration(current_track.duration), inline=True)
        
        if hasattr(current_track, "requester") and current_track.requester:
            embed.add_field(name="مطلوبة بواسطة", value=current_track.requester.mention, inline=True)
        
        # إضافة حالة التشغيل
        status = "قيد التشغيل ▶️" if not player.is_paused() else "متوقفة مؤقتًا ⏸️"
        embed.add_field(name="الحالة", value=status, inline=True)
        
        # إضافة مستوى الصوت
        embed.add_field(name="مستوى الصوت", value=f"{player.volume}%", inline=True)
        
        # إضافة قائمة الانتظار
        if ctx.guild.id in music_cog.song_queue and music_cog.song_queue[ctx.guild.id]:
            next_song = music_cog.song_queue[ctx.guild.id][0]
            embed.add_field(
                name="التالية",
                value=f"**{next_song.title}**",
                inline=False
            )
            embed.add_field(
                name="في قائمة الانتظار",
                value=f"{len(music_cog.song_queue[ctx.guild.id])} أغنية",
                inline=True
            )
        
        # إضافة صورة مصغرة
        if hasattr(current_track, "identifier"):
            embed.set_thumbnail(url=f"https://img.youtube.com/vi/{current_track.identifier}/maxresdefault.jpg")
        
        # إضافة أزرار التحكم
        view = NowPlayingView(self.bot, ctx, player)
        
        await ctx.send(embed=embed, view=view)
    
    @commands.command(
        name="صوت",
        aliases=["vol", "volume", "الصوت"],
        description="ضبط مستوى الصوت"
    )
    async def volume(self, ctx, level: int = None):
        """
        ضبط مستوى الصوت
        
        المعلمات:
            level (int): مستوى الصوت (0-100)
        
        أمثلة:
            !صوت 50
            !volume 75
        """
        # التحقق من وجود تشغيل حالي
        player = wavelink.NodePool.get_node().get_player(ctx.guild.id)
        
        if not player:
            embed = discord.Embed(
                title="❌ خطأ",
                description="البوت ليس متصلاً بأي قناة صوتية.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # إذا لم يتم تحديد مستوى، عرض المستوى الحالي مع أزرار التحكم
        if level is None:
            embed = discord.Embed(
                title="🔊 مستوى الصوت",
                description=f"المستوى الحالي: **{player.volume}%**\n"
                          f"استخدم الأزرار أدناه لضبط مستوى الصوت أو أرسل `!صوت [رقم]` لتحديد قيمة محددة.",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="الحالة", value=self._create_volume_bar(player.volume), inline=False)
            
            volume_view = VolumeView(self.bot, ctx, player)
            return await ctx.send(embed=embed, view=volume_view)
        
        # التحقق من صحة مستوى الصوت
        if not 0 <= level <= 100:
            embed = discord.Embed(
                title="❌ خطأ",
                description="يجب أن يكون مستوى الصوت بين 0 و 100.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # ضبط مستوى الصوت
        await player.set_volume(level)
        
        embed = discord.Embed(
            title="🔊 مستوى الصوت",
            description=f"تم ضبط مستوى الصوت على **{level}%**",
            color=discord.Color.green()
        )
        
        embed.add_field(name="الحالة", value=self._create_volume_bar(level), inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(
        name="تكرار",
        aliases=["loop", "repeat", "اعادة"],
        description="تفعيل/تعطيل وضع التكرار"
    )
    async def loop(self, ctx):
        """
        تفعيل أو تعطيل وضع تكرار الأغنية الحالية
        """
        # التحقق من وجود تشغيل حالي
        player = wavelink.NodePool.get_node().get_player(ctx.guild.id)
        
        if not player or not player.is_playing():
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا توجد أغنية قيد التشغيل حاليًا.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # تبديل حالة التكرار
        player.loop = not getattr(player, "loop", False)
        
        status = "تفعيل" if player.loop else "تعطيل"
        
        embed = discord.Embed(
            title="🔄 وضع التكرار",
            description=f"تم {status} وضع التكرار للأغنية الحالية.",
            color=discord.Color.green() if player.loop else discord.Color.red()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(
        name="خلط",
        aliases=["shuffle", "عشوائي"],
        description="خلط قائمة الأغاني"
    )
    async def shuffle(self, ctx):
        """
        خلط ترتيب الأغاني في قائمة الانتظار
        """
        # الحصول على مرجع لنظام تشغيل الموسيقى
        music_cog = self.bot.get_cog("MusicPlayer")
        
        if not music_cog:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لم يتم العثور على نظام تشغيل الموسيقى.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من وجود أغاني في قائمة الانتظار
        if not ctx.guild.id in music_cog.song_queue or not music_cog.song_queue[ctx.guild.id]:
            embed = discord.Embed(
                title="❌ خطأ",
                description="قائمة الانتظار فارغة.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # خلط قائمة الأغاني
        import random
        random.shuffle(music_cog.song_queue[ctx.guild.id])
        
        embed = discord.Embed(
            title="🔀 خلط القائمة",
            description=f"تم خلط {len(music_cog.song_queue[ctx.guild.id])} أغنية في قائمة الانتظار.",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(
        name="مسح_القائمة",
aliases=["مسح", "تفريغ_القائمة"],
        description="مسح قائمة الأغاني"
    )
    async def clear_queue(self, ctx):
        """
        مسح جميع الأغاني من قائمة الانتظار
        """
        # الحصول على مرجع لنظام تشغيل الموسيقى
        music_cog = self.bot.get_cog("MusicPlayer")
        
        if not music_cog:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لم يتم العثور على نظام تشغيل الموسيقى.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من وجود أغاني في قائمة الانتظار
        if not ctx.guild.id in music_cog.song_queue or not music_cog.song_queue[ctx.guild.id]:
            embed = discord.Embed(
                title="❌ خطأ",
                description="قائمة الانتظار فارغة بالفعل.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # حفظ عدد الأغاني التي تم مسحها
        queue_length = len(music_cog.song_queue[ctx.guild.id])
        
        # مسح قائمة الأغاني
        music_cog.song_queue[ctx.guild.id].clear()
        
        embed = discord.Embed(
            title="🗑️ مسح القائمة",
            description=f"تم مسح {queue_length} أغنية من قائمة الانتظار.",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
    
    def _format_duration(self, milliseconds):
        """تنسيق المدة من مللي ثانية إلى صيغة دقائق:ثواني"""
        seconds = milliseconds // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def _create_volume_bar(self, volume):
        """إنشاء شريط مرئي لمستوى الصوت"""
        filled_blocks = int(volume / 10)
        empty_blocks = 10 - filled_blocks
        
        bar = "▰" * filled_blocks + "▱" * empty_blocks
        return f"{bar} {volume}%"

async def setup(bot):
    """إعداد الصنف وإضافته إلى البوت"""
    await bot.add_cog(MusicControls(bot)) 