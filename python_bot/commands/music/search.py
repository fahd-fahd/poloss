#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import wavelink
import asyncio
import re
from discord.ui import Button, View, Select

class SearchResultsView(View):
    """عرض نتائج البحث مع أزرار التحكم"""
    
    def __init__(self, bot, ctx, tracks, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
        self.tracks = tracks
        
        # إضافة قائمة للاختيار من بين النتائج
        self.add_item(self._create_select_menu())
    
    def _create_select_menu(self):
        """إنشاء قائمة منسدلة للاختيار من بين النتائج"""
        options = []
        
        for i, track in enumerate(self.tracks):
            # تقصير العنوان إذا كان طويلاً جداً
            title = track.title
            if len(title) > 80:
                title = title[:77] + "..."
            
            # إنشاء خيار لكل مسار
            options.append(
                discord.SelectOption(
                    label=f"{i+1}. {title}",
                    description=self._format_duration(track.duration),
                    value=str(i)
                )
            )
        
        select = discord.ui.Select(
            placeholder="اختر أغنية للتشغيل...",
            min_values=1,
            max_values=1,
            options=options
        )
        
        select.callback = self.select_callback
        
        return select
    
    async def select_callback(self, interaction: discord.Interaction):
        """معالجة اختيار أغنية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب البحث فقط.", ephemeral=True)
        
        # الحصول على المسار المختار
        track_idx = int(interaction.data["values"][0])
        selected_track = self.tracks[track_idx]
        
        # تعيين طالب الأغنية
        selected_track.requester = interaction.user
        
        # إضافة الأغنية للتشغيل
        await self._play_track(interaction, selected_track)
    
    @discord.ui.button(label="تشغيل الكل", emoji="▶️", style=discord.ButtonStyle.success)
    async def play_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر تشغيل جميع نتائج البحث"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب البحث فقط.", ephemeral=True)
        
        # التحقق من وجود المستخدم في قناة صوتية
        if not interaction.user.voice:
            return await interaction.response.send_message("يجب أن تكون في قناة صوتية.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # تعيين طالب الأغاني
        for track in self.tracks:
            track.requester = interaction.user
        
        # تشغيل الأغنية الأولى وإضافة الباقي إلى قائمة الانتظار
        first_track = self.tracks[0]
        remaining_tracks = self.tracks[1:]
        
        # تشغيل الأغنية الأولى
        success = await self._play_track(interaction, first_track, show_message=False)
        
        if not success:
            return
        
        # إضافة باقي الأغاني إلى قائمة الانتظار
        music_cog = self.bot.get_cog("MusicPlayer")
        if music_cog:
            for track in remaining_tracks:
                if interaction.guild.id not in music_cog.song_queue:
                    music_cog.song_queue[interaction.guild.id] = []
                
                music_cog.song_queue[interaction.guild.id].append(track)
        
        # إرسال رسالة تأكيد
        await interaction.followup.send(
            f"✅ تم إضافة {len(self.tracks)} أغنية إلى قائمة التشغيل.",
            ephemeral=True
        )
        
        # إيقاف عرض الأزرار
        self.stop()
    
    @discord.ui.button(label="إلغاء", emoji="❌", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر إلغاء البحث"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب البحث فقط.", ephemeral=True)
        
        await interaction.response.edit_message(
            content="❌ تم إلغاء البحث.",
            embed=None,
            view=None
        )
        
        # إيقاف عرض الأزرار
        self.stop()
    
    async def _play_track(self, interaction, track, show_message=True):
        """تشغيل المسار المحدد"""
        try:
            # الاتصال بالقناة الصوتية
            player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
        except Exception as e:
            if isinstance(e, wavelink.errors.NodeError):
                if show_message:
                    await interaction.response.send_message("❌ لم يتم الاتصال بخادم الموسيقى. يرجى المحاولة لاحقًا.", ephemeral=True)
                return False
            
            try:
                # محاولة الحصول على مشغل موجود
                player = wavelink.NodePool.get_node().get_player(interaction.guild.id)
                if not player:
                    if show_message:
                        await interaction.response.send_message(f"❌ حدث خطأ: {str(e)}", ephemeral=True)
                    return False
            except Exception as e:
                if show_message:
                    await interaction.response.send_message(f"❌ حدث خطأ: {str(e)}", ephemeral=True)
                return False
        
        # تخزين قناة النص للإشعارات
        player.text_channel = interaction.channel
        
        # الحصول على مرجع لنظام تشغيل الموسيقى
        music_cog = self.bot.get_cog("MusicPlayer")
        
        # إضافة الأغنية إلى قائمة الانتظار أو تشغيلها فورًا
        if player.is_playing():
            # إضافة الأغنية إلى قائمة الانتظار
            if music_cog:
                if interaction.guild.id not in music_cog.song_queue:
                    music_cog.song_queue[interaction.guild.id] = []
                
                music_cog.song_queue[interaction.guild.id].append(track)
            
            if show_message:
                embed = discord.Embed(
                    title="🎵 تمت إضافة الأغنية إلى قائمة الانتظار",
                    description=f"**{track.title}**",
                    color=discord.Color.green()
                )
                embed.add_field(name="المدة", value=self._format_duration(track.duration), inline=True)
                
                position = len(music_cog.song_queue[interaction.guild.id]) if music_cog else 1
                embed.add_field(name="الموقع في القائمة", value=f"#{position}", inline=True)
                
                embed.set_thumbnail(url=f"https://img.youtube.com/vi/{track.identifier}/maxresdefault.jpg")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            # تشغيل الأغنية مباشرة
            await player.play(track)
            
            if music_cog:
                music_cog.now_playing[interaction.guild.id] = track
            
            if show_message:
                embed = discord.Embed(
                    title="🎵 بدأ تشغيل",
                    description=f"**{track.title}**",
                    color=discord.Color.blue()
                )
                embed.add_field(name="المدة", value=self._format_duration(track.duration), inline=True)
                embed.set_thumbnail(url=f"https://img.youtube.com/vi/{track.identifier}/maxresdefault.jpg")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # إيقاف عرض الأزرار
        self.stop()
        return True
    
    def _format_duration(self, milliseconds):
        """تنسيق المدة من مللي ثانية إلى صيغة دقائق:ثواني"""
        seconds = milliseconds // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"

class MusicSearch(commands.Cog):
    """أوامر البحث عن الموسيقى"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name="بحث",
        aliases=["search", "yt", "يوتيوب"],
        description="البحث عن أغاني في YouTube"
    )
    async def search(self, ctx, *, query: str = None):
        """
        البحث عن أغاني في YouTube
        
        المعلمات:
            query (str): كلمات البحث
        
        أمثلة:
            !بحث despacito
            !search arabic songs
        """
        if not query:
            embed = discord.Embed(
                title="❌ خطأ في الأمر",
                description=f"يرجى تحديد كلمات البحث.\n"
                           f"مثال: `!بحث despacito`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من وجود المستخدم في قناة صوتية
        if not ctx.author.voice:
            embed = discord.Embed(
                title="❌ خطأ",
                description="يجب أن تكون في قناة صوتية لاستخدام هذا الأمر.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # رسالة انتظار
        loading_msg = await ctx.send("🔍 جاري البحث في YouTube...")
        
        try:
            # البحث عن الأغاني في YouTube
            search_query = f"ytsearch5:{query}"  # البحث عن 5 نتائج فقط
            tracks = await wavelink.NodePool.get_node().get_tracks(wavelink.YouTubeTrack, search_query)
            
            if not tracks:
                return await loading_msg.edit(content="❌ لم يتم العثور على نتائج للبحث.")
            
            # إنشاء رسالة مضمنة مع نتائج البحث
            embed = discord.Embed(
                title=f"🔍 نتائج البحث عن: {query}",
                description="اختر أغنية من القائمة أدناه للتشغيل:",
                color=discord.Color.blue()
            )
            
            # إضافة النتائج
            for i, track in enumerate(tracks, 1):
                embed.add_field(
                    name=f"{i}. {track.title}",
                    value=f"المدة: {self._format_duration(track.duration)}",
                    inline=False
                )
            
            # إنشاء واجهة التفاعل
            view = SearchResultsView(self.bot, ctx, tracks)
            
            await loading_msg.edit(content=None, embed=embed, view=view)
            
        except Exception as e:
            await loading_msg.edit(content=f"❌ حدث خطأ أثناء البحث: {str(e)}")
            print(f"خطأ في أمر البحث: {str(e)}")
    
    @commands.command(
        name="شغل_تالي",
        aliases=["playnext", "شغل_بعدها"],
        description="تشغيل أغنية بعد الأغنية الحالية مباشرة"
    )
    async def play_next(self, ctx, *, query: str = None):
        """
        تشغيل أغنية بعد الأغنية الحالية مباشرة
        
        المعلمات:
            query (str): اسم الأغنية أو رابط YouTube
        
        أمثلة:
            !شغل_تالي despacito
            !playnext https://www.youtube.com/watch?v=dQw4w9WgXcQ
        """
        if not query:
            embed = discord.Embed(
                title="❌ خطأ في الأمر",
                description=f"يرجى تحديد اسم الأغنية أو الرابط.\n"
                           f"مثال: `!شغل_تالي despacito`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من وجود المستخدم في قناة صوتية
        if not ctx.author.voice:
            embed = discord.Embed(
                title="❌ خطأ",
                description="يجب أن تكون في قناة صوتية لاستخدام هذا الأمر.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # رسالة انتظار
        loading_msg = await ctx.send("🔍 جاري البحث عن الأغنية...")
        
        # البحث عن الأغنية
        url_regex = r"https?://(www\.)?(youtube\.com|youtu\.be)/watch\?v=([a-zA-Z0-9_-]+)"
        
        try:
            if re.match(url_regex, query):
                # إذا كان الإدخال رابط يوتيوب
                tracks = await wavelink.NodePool.get_node().get_tracks(wavelink.YouTubeTrack, query)
                track = tracks[0]
            else:
                # إذا كان الإدخال اسم أغنية
                search_query = f"ytsearch:{query}"
                tracks = await wavelink.NodePool.get_node().get_tracks(wavelink.YouTubeTrack, search_query)
                if not tracks:
                    return await loading_msg.edit(content="❌ لم يتم العثور على نتائج للبحث.")
                track = tracks[0]
            
            # تعيين مطلوب الأغنية
            track.requester = ctx.author
            
            # الحصول على مرجع لنظام تشغيل الموسيقى
            music_cog = self.bot.get_cog("MusicPlayer")
            
            if not music_cog:
                return await loading_msg.edit(content="❌ لم يتم العثور على نظام تشغيل الموسيقى.")
            
            # التحقق من وجود تشغيل حالي
            player = wavelink.NodePool.get_node().get_player(ctx.guild.id)
            
            if not player:
                # إذا لم يكن هناك مشغل، قم باستخدام أمر التشغيل العادي
                play_cmd = self.bot.get_command("شغل")
                if play_cmd:
                    await loading_msg.delete()
                    return await ctx.invoke(play_cmd, query=query)
                else:
                    return await loading_msg.edit(content="❌ لم يتم العثور على أمر التشغيل.")
            
            # إضافة الأغنية في بداية قائمة الانتظار
            if ctx.guild.id not in music_cog.song_queue:
                music_cog.song_queue[ctx.guild.id] = []
            
            music_cog.song_queue[ctx.guild.id].insert(0, track)
            
            embed = discord.Embed(
                title="🎵 تمت إضافة الأغنية بعد الأغنية الحالية",
                description=f"**{track.title}**",
                color=discord.Color.green()
            )
            embed.add_field(name="المدة", value=self._format_duration(track.duration), inline=True)
            embed.add_field(name="مطلوبة بواسطة", value=ctx.author.mention, inline=True)
            embed.set_thumbnail(url=f"https://img.youtube.com/vi/{track.identifier}/maxresdefault.jpg")
            
            await loading_msg.edit(content=None, embed=embed)
            
        except Exception as e:
            await loading_msg.edit(content=f"❌ حدث خطأ أثناء محاولة تشغيل الأغنية: {str(e)}")
            print(f"خطأ في أمر التشغيل التالي: {str(e)}")
    
    def _format_duration(self, milliseconds):
        """تنسيق المدة من مللي ثانية إلى صيغة دقائق:ثواني"""
        seconds = milliseconds // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"

async def setup(bot):
    """إعداد الصنف"""
    await bot.add_cog(MusicSearch(bot)) 