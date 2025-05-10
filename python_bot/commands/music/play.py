#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import datetime
import re
import wavelink
from discord.ui import Button, View
import urllib.parse

class MusicButtons(View):
    """فئة أزرار التحكم بالموسيقى"""
    
    def __init__(self, bot, ctx, timeout=180):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
    
    @discord.ui.button(label="⏯️ تشغيل/إيقاف", style=discord.ButtonStyle.primary)
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر التشغيل والإيقاف المؤقت"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب المحتوى فقط.", ephemeral=True)
        
        player = self.bot.wavelink.get_player(interaction.guild.id)
        if not player:
            return await interaction.response.send_message("لا يوجد محتوى قيد التشغيل حاليًا.", ephemeral=True)
            
        if player.is_paused():
            await player.resume()
            await interaction.response.send_message("▶️ تم استئناف التشغيل.", ephemeral=True)
        else:
            await player.pause()
            await interaction.response.send_message("⏸️ تم إيقاف التشغيل مؤقتًا.", ephemeral=True)
    
    @discord.ui.button(label="⏭️ التالي", style=discord.ButtonStyle.primary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر تخطي المحتوى الحالي"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب المحتوى فقط.", ephemeral=True)
            
        player = self.bot.wavelink.get_player(interaction.guild.id)
        if not player:
            return await interaction.response.send_message("لا يوجد محتوى قيد التشغيل حاليًا.", ephemeral=True)
            
        await player.stop()
        await interaction.response.send_message("⏭️ تم تخطي المحتوى الحالي.", ephemeral=True)
    
    @discord.ui.button(label="🔄 تكرار", style=discord.ButtonStyle.secondary)
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر تكرار المحتوى"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب المحتوى فقط.", ephemeral=True)
            
        player = self.bot.wavelink.get_player(interaction.guild.id)
        if not player:
            return await interaction.response.send_message("لا يوجد محتوى قيد التشغيل حاليًا.", ephemeral=True)
            
        try:
            player.loop = not getattr(player, 'loop', False)
            loop_status = "تشغيل" if player.loop else "إيقاف"
            await interaction.response.send_message(f"🔄 تم {loop_status} وضع التكرار.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"حدث خطأ: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="⏹️ إيقاف", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر إيقاف التشغيل ومغادرة القناة"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب المحتوى فقط.", ephemeral=True)
            
        player = self.bot.wavelink.get_player(interaction.guild.id)
        if not player:
            return await interaction.response.send_message("لا يوجد محتوى قيد التشغيل حاليًا.", ephemeral=True)
            
        await player.disconnect()
        await interaction.response.send_message("⏹️ تم إيقاف التشغيل ومغادرة القناة الصوتية.", ephemeral=True)
        self.stop()  # إيقاف العرض (الأزرار)

class MusicPlayer(commands.Cog):
    """نظام تشغيل الصوت"""
    
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.now_playing = {}
        # تغيير هنا: استخدام setup_hook بدلاً من bot.loop.create_task
        # سنستخدم أسلوب Cog.listener لاستدعاء الدالة عند جاهزية البوت

    # إضافة هذه الدالة لمعالجة حدث جاهزية البوت
    @commands.Cog.listener()
    async def on_ready(self):
        """يتم استدعاؤها عندما يكون البوت جاهزاً"""
        await self.connect_nodes()
    async def connect_nodes(self):
        """الاتصال بخوادم Wavelink"""
        try:
            await wavelink.Pool.connect(
                client=self.bot,
                nodes=[
                    wavelink.Node(
                        uri="https://freelavalink.ga:443",
                        password="www.freelavalink.ga",
                        secure=True
                    )
                ]
            )
        except Exception as e:
            print(f"خطأ أثناء الاتصال بـ Lavalink: {str(e)}")
        """عند اتصال عقدة Wavelink"""
        print(f'تم الاتصال بعقدة Wavelink: {node.identifier}')
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track, reason):
        """عند انتهاء المسار"""
        guild_id = player.guild.id
        
        # التحقق من وضع التكرار
        if getattr(player, 'loop', False):
            # إعادة تشغيل نفس المسار
            await player.play(track)
            return
            
        # التحقق من وجود محتوى في قائمة الانتظار
        if guild_id in self.song_queue and self.song_queue[guild_id]:
            # تشغيل المحتوى التالي في القائمة
            next_track = self.song_queue[guild_id].pop(0)
            await player.play(next_track)
            
            # تحديث المحتوى الحالي
            self.now_playing[guild_id] = next_track
            
            # إرسال رسالة بالمحتوى الجديد
            embed = discord.Embed(
                title="🎵 الآن يتم تشغيل",
                description=f"**{next_track.title}**",
                color=discord.Color.blue()
            )
            embed.add_field(name="المدة", value=self._format_duration(next_track.duration), inline=True)
            embed.add_field(name="مطلوبة بواسطة", value=next_track.requester.mention, inline=True)
            
            # محاولة إضافة صورة مصغرة إذا كان المحتوى من يوتيوب
            if hasattr(next_track, 'identifier') and self._is_youtube_url(next_track.uri):
                embed.set_thumbnail(url=f"https://img.youtube.com/vi/{next_track.identifier}/maxresdefault.jpg")
            
            channel = player.guild.get_channel(player.text_channel.id)
            if channel:
                await channel.send(embed=embed)
        else:
            # لا يوجد محتوى إضافي
            if guild_id in self.now_playing:
                del self.now_playing[guild_id]
    
    def _is_youtube_url(self, url):
        """التحقق مما إذا كان الرابط من يوتيوب"""
        if not url:
            return False
        youtube_pattern = re.compile(r'https?://(?:www\.)?(?:youtube\.com|youtu\.be)')
        return bool(youtube_pattern.match(url))
    
    def _extract_youtube_id(self, url):
        """استخراج معرف الفيديو من رابط يوتيوب"""
        if not url:
            return None
        
        # أنماط مختلفة لروابط يوتيوب
        patterns = [
            r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    @commands.command(
        name="شغل",
        aliases=["play", "p", "تشغيل", "url", "رابط", "بث"],
        description="تشغيل محتوى صوتي من أي رابط"
    )
    async def play(self, ctx, *, query: str = None):
        """
        تشغيل محتوى صوتي من أي رابط
        
        المعلمات:
            query (str): رابط الملف الصوتي أو كلمات البحث
        
        أمثلة:
            !شغل https://example.com/audio.mp3
            !بث http://stream.example.com/live
            !تشغيل https://www.youtube.com/watch?v=dQw4w9WgXcQ
            !رابط https://soundcloud.com/example/track
        """
        if not query:
            embed = discord.Embed(
                title="❌ خطأ في الأمر",
                description=f"يرجى تحديد رابط للتشغيل أو كلمات للبحث.\n"
                           f"مثال: `!شغل https://example.com/audio.mp3` أو `!شغل despacito`",
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
        loading_msg = await ctx.send("🔍 جاري تحميل المحتوى...")
        
        # الاتصال بالقناة الصوتية
        try:
            player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        except Exception as e:
            if isinstance(e, wavelink.errors.NodeError):
                return await loading_msg.edit(content="❌ لم يتم الاتصال بخادم الموسيقى. يرجى المحاولة لاحقًا.")
            
            # محاولة الحصول على مشغل موجود
            player = wavelink.NodePool.get_node().get_player(ctx.guild.id)
            if not player:
                return await loading_msg.edit(content=f"❌ حدث خطأ: {str(e)}")
        
        # تخزين قناة النص للإشعارات
        player.text_channel = ctx.channel
        
        # التحقق مما إذا كان الاستعلام رابطًا مباشرًا
        url_pattern = re.compile(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
        
        try:
            if url_pattern.match(query):
                # تشغيل من الرابط مباشرة
                if self._is_youtube_url(query):
                    # إذا كان رابط يوتيوب
                    tracks = await wavelink.NodePool.get_node().get_tracks(wavelink.YouTubeTrack, query)
                else:
                    # أي رابط آخر
                    tracks = await wavelink.NodePool.get_node().get_tracks(wavelink.Track, query)
                
                if not tracks:
                    return await loading_msg.edit(content="❌ لم يتم العثور على محتوى صالح للتشغيل في الرابط المحدد.")
                
                track = tracks[0]
                thumbnail_id = self._extract_youtube_id(query) if self._is_youtube_url(query) else None
            else:
                # البحث في يوتيوب
                search_query = f"ytsearch:{query}"
                tracks = await wavelink.NodePool.get_node().get_tracks(wavelink.YouTubeTrack, search_query)
                
                if not tracks:
                    return await loading_msg.edit(content="❌ لم يتم العثور على نتائج للبحث.")
                
                track = tracks[0]
                thumbnail_id = track.identifier
            
            # تعيين مطلوب المحتوى
            track.requester = ctx.author
            
            # إضافة المحتوى إلى قائمة الانتظار أو تشغيله فورًا
            if player.is_playing():
                # إضافة المحتوى إلى قائمة الانتظار
                if ctx.guild.id not in self.song_queue:
                    self.song_queue[ctx.guild.id] = []
                
                self.song_queue[ctx.guild.id].append(track)
                
                embed = discord.Embed(
                    title="🎵 تمت إضافة محتوى إلى قائمة الانتظار",
                    description=f"**{track.title}**",
                    color=discord.Color.green()
                )
                embed.add_field(name="المدة", value=self._format_duration(track.duration), inline=True)
                embed.add_field(name="الموقع في القائمة", value=f"#{len(self.song_queue[ctx.guild.id])}", inline=True)
                embed.add_field(name="مطلوبة بواسطة", value=ctx.author.mention, inline=True)
                
                if thumbnail_id:
                    embed.set_thumbnail(url=f"https://img.youtube.com/vi/{thumbnail_id}/maxresdefault.jpg")
                
                await loading_msg.edit(content=None, embed=embed)
            else:
                # تشغيل المحتوى مباشرة
                await player.play(track)
                self.now_playing[ctx.guild.id] = track
                
                embed = discord.Embed(
                    title="🎵 الآن يتم تشغيل",
                    description=f"**{track.title}**",
                    color=discord.Color.blue()
                )
                embed.add_field(name="المدة", value=self._format_duration(track.duration), inline=True)
                embed.add_field(name="مطلوبة بواسطة", value=ctx.author.mention, inline=True)
                
                if thumbnail_id:
                    embed.set_thumbnail(url=f"https://img.youtube.com/vi/{thumbnail_id}/maxresdefault.jpg")
                
                # إضافة نوع المصدر إذا كان متاحًا
                source_type = self._get_source_type(query)
                if source_type:
                    embed.add_field(name="المصدر", value=source_type, inline=True)
                
                # إنشاء أزرار التحكم
                view = MusicButtons(self.bot, ctx)
                await loading_msg.edit(content=None, embed=embed, view=view)
                
        except Exception as e:
            await loading_msg.edit(content=f"❌ حدث خطأ أثناء محاولة تشغيل المحتوى: {str(e)}")
            print(f"خطأ في أمر التشغيل: {str(e)}")
    
    def _get_source_type(self, url):
        """تحديد نوع مصدر المحتوى"""
        if not url:
            return None
            
        domain_patterns = {
            r'youtube\.com|youtu\.be': 'YouTube',
            r'soundcloud\.com': 'SoundCloud',
            r'spotify\.com': 'Spotify',
            r'twitch\.tv': 'Twitch',
            r'bandcamp\.com': 'Bandcamp',
            r'vimeo\.com': 'Vimeo',
            r'dailymotion\.com': 'Dailymotion'
        }
        
        for pattern, name in domain_patterns.items():
            if re.search(pattern, url, re.IGNORECASE):
                return name
                
        # فحص امتداد الملف إذا كان موجوداً
        url_path = urllib.parse.urlparse(url).path.lower()
        file_extensions = {
            '.mp3': 'ملف صوتي MP3',
            '.wav': 'ملف صوتي WAV',
            '.ogg': 'ملف صوتي OGG',
            '.flac': 'ملف صوتي FLAC',
            '.m4a': 'ملف صوتي M4A',
            '.mp4': 'ملف فيديو MP4',
            '.m3u8': 'بث مباشر',
            '.pls': 'قائمة تشغيل'
        }
        
        for ext, name in file_extensions.items():
            if url_path.endswith(ext):
                return name
                
        return "رابط مباشر"
    
    @commands.command(
        name="قائمة_انتظار",
        aliases=["queue", "q", "طابور", "انتظار"],
        description="عرض قائمة المحتويات"
    )
    async def queue(self, ctx):
        """
        عرض قائمة المحتويات المنتظرة
        """
        guild_id = ctx.guild.id
        
        if guild_id not in self.song_queue or not self.song_queue[guild_id]:
            embed = discord.Embed(
                title="📋 قائمة التشغيل",
                description="القائمة فارغة. أضف محتوى باستخدام أمر `!شغل`.",
                color=discord.Color.blue()
            )
            return await ctx.send(embed=embed)
        
        # عرض المحتوى الحالي
        embed = discord.Embed(
            title="📋 قائمة التشغيل",
            color=discord.Color.blue()
        )
        
        # إضافة المحتوى الحالي
        if guild_id in self.now_playing:
            current_track = self.now_playing[guild_id]
            embed.add_field(
                name="🎵 الآن يتم تشغيل",
                value=f"**{current_track.title}** - {self._format_duration(current_track.duration)}\n"
                      f"مطلوبة بواسطة: {current_track.requester.mention}",
                inline=False
            )
        
        # إضافة قائمة الانتظار (بحد أقصى 10 محتويات)
        queue_text = ""
        for i, track in enumerate(self.song_queue[guild_id][:10], 1):
            queue_text += f"**{i}.** {track.title} - {self._format_duration(track.duration)}\n"
            queue_text += f"مطلوبة بواسطة: {track.requester.mention}\n\n"
        
        # إضافة عدد المحتويات المتبقية إذا كانت أكثر من 10
        remaining = len(self.song_queue[guild_id]) - 10
        if remaining > 0:
            queue_text += f"\n*و {remaining} محتويات أخرى...*"
        
        embed.add_field(name="📋 قائمة الانتظار", value=queue_text if queue_text else "قائمة الانتظار فارغة", inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(
        name="تخطي",
        aliases=["skip", "s", "تجاوز"],
        description="تخطي المحتوى الحالي"
    )
    async def skip(self, ctx):
        """
        تخطي المحتوى الحالي
        """
        player = wavelink.NodePool.get_node().get_player(ctx.guild.id)
        
        if not player or not player.is_playing():
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يوجد محتوى قيد التشغيل حاليًا.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # تخطي المحتوى
        await player.stop()
        
        embed = discord.Embed(
            title="⏭️ تم تخطي المحتوى الحالي",
            description="تم تخطي المحتوى الحالي وتشغيل التالي (إن وجدت).",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @commands.command(
        name="إيقاف",
        aliases=["stop", "توقف", "ايقاف"],
        description="إيقاف التشغيل ومغادرة القناة الصوتية"
    )
    async def stop(self, ctx):
        """
        إيقاف التشغيل ومغادرة القناة الصوتية
        """
        player = wavelink.NodePool.get_node().get_player(ctx.guild.id)
        
        if not player:
            embed = discord.Embed(
                title="❌ خطأ",
                description="البوت ليس متصلاً بأي قناة صوتية.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # إعادة تعيين قوائم التشغيل
        if ctx.guild.id in self.song_queue:
            self.song_queue[ctx.guild.id] = []
        
        if ctx.guild.id in self.now_playing:
            del self.now_playing[ctx.guild.id]
        
        # إيقاف التشغيل ومغادرة القناة
        await player.disconnect()
        
        embed = discord.Embed(
            title="⏹️ تم إيقاف التشغيل",
            description="تم إيقاف التشغيل ومغادرة القناة الصوتية.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @commands.command(
        name="توقف_مؤقت",
        aliases=["pause", "وقفة"],
        description="إيقاف مؤقت للمحتوى الحالي"
    )
    async def pause(self, ctx):
        """
        إيقاف مؤقت للمحتوى الحالي
        """
        player = wavelink.NodePool.get_node().get_player(ctx.guild.id)
        
        if not player or not player.is_playing():
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يوجد محتوى قيد التشغيل حاليًا.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من حالة التشغيل
        if player.is_paused():
            embed = discord.Embed(
                title="❌ خطأ",
                description="المحتوى متوقف مؤقتًا بالفعل. استخدم `!استمرار` لاستئناف التشغيل.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # إيقاف مؤقت
        await player.pause()
        
        embed = discord.Embed(
            title="⏸️ تم الإيقاف المؤقت",
            description="تم إيقاف المحتوى مؤقتًا. استخدم `!استمرار` لاستئناف التشغيل.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @commands.command(
        name="استمرار",
        aliases=["resume", "استكمال", "استئناف"],
        description="استئناف تشغيل المحتوى المتوقف مؤقتًا"
    )
    async def resume(self, ctx):
        """
        استئناف تشغيل المحتوى المتوقف مؤقتًا
        """
        player = wavelink.NodePool.get_node().get_player(ctx.guild.id)
        
        if not player:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يوجد محتوى قيد التشغيل حاليًا.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من حالة التشغيل
        if not player.is_paused():
            embed = discord.Embed(
                title="❌ خطأ",
                description="المحتوى قيد التشغيل بالفعل.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # استئناف التشغيل
        await player.resume()
        
        embed = discord.Embed(
            title="▶️ تم الاستئناف",
            description="تم استئناف تشغيل المحتوى.",
            color=discord.Color.blue()
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

async def setup(bot):
    """إعداد الصنف"""
    await bot.add_cog(MusicPlayer(bot)) 