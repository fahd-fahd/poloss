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
            # قائمة العقد متوافقة مع إصدار wavelink المثبت
            nodes = [
                # العقدة الاساسية - Lavalink قياسي
                wavelink.Node(
                    uri="http://lavalink.clxud.dev:2333",
                    password="youshallnotpass",
                    identifier="Main-Node"
                ),
                # العقدة الثانية
                wavelink.Node(
                    uri="http://lava.link:80",
                    password="anything as a password",
                    identifier="Public-Node"
                ),
                # عقدة احتياطية
                wavelink.Node(
                    uri="http://node.rexking.xyz:2333", 
                    password="RexLavalinkServer", 
                    identifier="Backup-Node-1"
                ),
                # عقدة محلية
                wavelink.Node(
                    uri="http://localhost:2333",  # للتشغيل المحلي إذا كان متاحًا
                    password="youshallnotpass",
                    identifier="Local-Node"
                )
            ]
            
            # محاولة الاتصال بجميع العقد
            await wavelink.NodePool.connect(client=self.bot, nodes=nodes)
            
            print(f"✅ تم الاتصال بعقد Wavelink")
            connected_nodes = 0
            for i, node in enumerate(wavelink.NodePool.get_node().pool.nodes):
                connected_nodes += 1
                print(f"  ✓ متصل بـ: {node.identifier} ({node.uri})")
            
            print(f"  ℹ️ عدد العقد المتصلة: {connected_nodes}/{len(nodes)}")
            
            # تسجيل معالجات الأحداث لمتابعة المسارات
            self.bot.add_listener(self.on_wavelink_track_start, "on_wavelink_track_start")
            self.bot.add_listener(self.on_wavelink_track_end, "on_wavelink_track_end")
            
            # السماح للمستخدمين بمعرفة أن النظام جاهز
            for guild in self.bot.guilds:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        if "general" in channel.name or "chat" in channel.name or "عام" in channel.name:
                            try:
                                await channel.send("🎵 تم تجهيز نظام الصوت! يمكنك الآن استخدام أوامر الموسيقى.", delete_after=10)
                                break
                            except:
                                pass
            
        except Exception as e:
            print(f"❌ خطأ أثناء الاتصال بـ Lavalink: {str(e)}")
            print("جاري المحاولة باستخدام طريقة بديلة...")
            
            # محاولة الاتصال بكل عقدة على حدة
            connected = False
            
            # قائمة بالعقد البديلة للمحاولة
            fallback_nodes = [
                ("http://lavalink.clxud.dev:2333", "youshallnotpass", "Fallback-1"),
                ("http://lava.link:80", "anything as a password", "Fallback-4"),
                ("http://node.rexking.xyz:2333", "RexLavalinkServer", "Fallback-3"),
                ("http://46.4.104.234:2333", "discord123", "Fallback-6"),
                ("http://localhost:2333", "youshallnotpass", "Local")
            ]
            
            for uri, password, identifier in fallback_nodes:
                try:
                    node = wavelink.Node(
                        uri=uri,
                        password=password,
                        identifier=identifier
                    )
                    
                    # محاولة الاتصال بالعقدة
                    await wavelink.NodePool.connect(client=self.bot, nodes=[node])
                    print(f"✅ تم الاتصال بعقدة بديلة: {identifier} ({uri})")
                    connected = True
                    break
                    
                except Exception as e2:
                    print(f"❌ فشل الاتصال بالعقدة البديلة {identifier}: {str(e2)}")
            
            if not connected:
                print("⚠️ فشلت جميع محاولات الاتصال بالعقد. قد لا تعمل ميزات الصوت بشكل صحيح.")
                
                # محاولة أخيرة باستخدام عقدة محلية
                try:
                    node = wavelink.Node(
                        uri="http://127.0.0.1:2333",
                        password="youshallnotpass",
                        identifier="Emergency-Local"
                    )
                    await wavelink.NodePool.connect(client=self.bot, nodes=[node])
                    print("✅ تم الاتصال بعقدة محلية للطوارئ")
                except Exception as e:
                    print(f"❌ فشل الاتصال بالعقدة المحلية: {str(e)}")
                    print("ℹ️ تأكد من تثبيت Java وتشغيل Lavalink.jar")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player, track):
        """يتم استدعاؤها عند بدء تشغيل مسار"""
        print(f"🎵 بدء تشغيل المسار: {track.title}")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player, track, reason):
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
        تشغيل محتوى صوتي من رابط أو كلمات بحث
        الاستخدام:
        - !شغل [رابط YouTube]
        - !شغل [كلمات بحث]
        """
        # التحقق من صحة المعلمات
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
        loading_msg = await ctx.send("🔍 جاري تحليل المحتوى...")
        
        # الانضمام للقناة الصوتية
        voice_channel = ctx.author.voice.channel
        
        # محاولة الوصول إلى عقدة
        node = await self._get_node(loading_msg)
        if not node:
            return
        
        # الاتصال بالقناة الصوتية
        try:
            player = await self._get_or_create_player(ctx, node, voice_channel, loading_msg)
            if not player:
                return
            
            # تعيين القناة النصية للإشعارات
            player.text_channel = ctx.channel
        except Exception as e:
            return await loading_msg.edit(content=f"❌ حدث خطأ أثناء محاولة الاتصال بالقناة الصوتية: {str(e)}")
        
        # تحسين التعامل مع الروابط
        try:
            # تنظيف الرابط من الأخطاء الشائعة
            cleaned_query = query.strip()
            
            # معالجة الروابط التي تم نسخها مع علامات اقتباس
            if cleaned_query.startswith('"') and cleaned_query.endswith('"'):
                cleaned_query = cleaned_query[1:-1]
            
            # إصلاح الروابط التي تحتوي على مسافات
            if "http" in cleaned_query and " " in cleaned_query:
                url_parts = cleaned_query.split()
                for part in url_parts:
                    if part.startswith("http"):
                        cleaned_query = part
                        await loading_msg.edit(content=f"ℹ️ تم تصحيح الرابط: {cleaned_query}")
                        break
            
            # معالجة الاستعلام (رابط أو بحث)
            track = await self._resolve_track(ctx, cleaned_query, node, loading_msg)
            if not track:
                return
            
            # ضبط الخصائص الإضافية للمسار
            track.requester = ctx.author
            
            # إضافة المحتوى إلى قائمة الانتظار أو تشغيله فورًا
            if player.is_playing():
                return await self._add_to_queue(ctx, player, track, loading_msg)
            else:
                return await self._play_track(ctx, player, track, loading_msg)
            
        except Exception as e:
            await loading_msg.edit(content=f"❌ حدث خطأ أثناء محاولة تشغيل المحتوى: {str(e)}")
            print(f"خطأ في أمر التشغيل: {str(e)}")
    
    async def _get_node(self, message):
        """الحصول على عقدة نشطة"""
        try:
            # محاولة الحصول على عقدة بعدة طرق
            try:
                # الطريقة الرئيسية: استخدام NodePool.get_node()
                node = wavelink.NodePool.get_node()
                if node:
                    return node
            except Exception as e:
                print(f"فشل الحصول على عقدة: {str(e)}")
            
            # إذا وصلنا إلى هنا، حاول الاتصال مرة أخرى
            await self.connect_nodes()
            
            # محاولة أخيرة للحصول على عقدة
            node = wavelink.NodePool.get_node()
            if node:
                return node
            
            # لم نتمكن من الحصول على عقدة
            await message.edit(content="❌ لم يتم الاتصال بخادم الموسيقى. يرجى المحاولة لاحقًا.")
            return None
        except Exception as e:
            await message.edit(content=f"❌ حدث خطأ أثناء الاتصال بخادم الموسيقى: {str(e)}")
            return None

    async def _get_or_create_player(self, ctx, node, voice_channel, message):
        """إنشاء أو الحصول على مشغل موجود"""
        try:
            # محاولة الحصول على مشغل موجود
            try:
                player = node.get_player(ctx.guild.id)
                
                # إذا كان المشغل موجود ولكنه في قناة مختلفة
                if player and player.channel and player.channel.id != voice_channel.id:
                    # محاولة الانتقال إلى القناة الجديدة
                    try:
                        await player.move_to(voice_channel)
                        return player
                    except Exception as e:
                        print(f"خطأ أثناء الانتقال إلى القناة: {str(e)}")
                        # في حالة الخطأ، قم بفصل المشغل وإنشاء مشغل جديد
                        await player.disconnect()
                        player = None
                
                # إذا كان المشغل موجودًا بالفعل في القناة الصحيحة
                if player:
                    return player
            except Exception as e:
                print(f"خطأ أثناء البحث عن مشغل موجود: {str(e)}")
            
            # إنشاء مشغل جديد
            try:
                player = await voice_channel.connect(cls=wavelink.Player)
                # ضبط خصائص المشغل
                player.text_channel = ctx.channel
                
                # ضبط مستوى الصوت الافتراضي
                await player.set_volume(70)
                
                return player
            except Exception as e:
                await message.edit(content=f"❌ حدث خطأ أثناء الاتصال بالقناة الصوتية: {str(e)}")
                return None
        except Exception as e:
            await message.edit(content=f"❌ حدث خطأ أثناء إعداد المشغل: {str(e)}")
            return None

    async def _resolve_track(self, ctx, query, node, message):
        """تحليل الاستعلام للحصول على المسار"""
        # تحسين التعرف على الروابط
        
        # التحقق مما إذا كان الاستعلام رابطًا
        url_pattern = re.compile(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
        is_url = bool(url_pattern.match(query))
        
        # معالجة URLs الخاصة
        if is_url:
            await message.edit(content=f"🔍 تحليل الرابط: {query[:50]}{'...' if len(query) > 50 else ''}")
            
            # تحسين روابط YouTube - تعامل مع عدة أنماط
            if 'youtube.com' in query or 'youtu.be' in query:
                return await self._resolve_youtube(query, node, message)
            
            # تحسين روابط SoundCloud
            elif 'soundcloud.com' in query:
                return await self._resolve_soundcloud(query, node, message)
            
            # تحسين روابط Spotify
            elif 'spotify.com' in query:
                return await self._resolve_spotify(query, node, message)
            
            # تحسين لروابط استضافة الملفات الشائعة
            elif any(x in query.lower() for x in ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.mp4', '.aac']):
                return await self._resolve_direct_file(query, node, message)
            
            # روابط أخرى
            else:
                return await self._resolve_generic_url(query, node, message)
        else:
            # إذا لم يكن رابطًا، قم بالبحث في يوتيوب مع تحسين النتائج
            await message.edit(content=f"🔍 جاري البحث في YouTube عن: {query[:40]}{'...' if len(query) > 40 else ''}")
            return await self._search_youtube(query, node, message)

    async def _resolve_youtube(self, url, node, message):
        """معالجة روابط يوتيوب"""
        # تنظيف الرابط من المعلمات غير الضرورية
        clean_url = url.split('&')[0]  # إزالة المعلمات بعد العلامة &
        
        # استخراج معرف الفيديو إذا كان ذلك ممكنًا
        video_id = None
        
        # نمط للروابط القياسية مثل youtube.com/watch?v=ID
        watch_pattern = re.compile(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})')
        match = watch_pattern.search(clean_url)
        if match:
            video_id = match.group(1)
            # إعادة تشكيل الرابط بتنسيق قياسي
            clean_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # مسار التنفيذ الأساسي
        try:
            # محاولة 1: استخدام الرابط المنظف مع YouTubeTrack
            tracks = await wavelink.YouTubeTrack.search(clean_url)
            if tracks:
                await message.edit(content=f"✅ تم العثور على المحتوى: {tracks[0].title}")
                return tracks[0]
        except Exception as e:
            print(f"فشل تحليل YouTube بالطريقة 1: {str(e)}")
        
        # محاولة 2: استخدام معرف الفيديو مباشرة إذا تم استخراجه
        if video_id:
            try:
                direct_url = f"https://www.youtube.com/watch?v={video_id}"
                tracks = await wavelink.YouTubeTrack.search(direct_url)
                if tracks:
                    await message.edit(content=f"✅ تم العثور على المحتوى (بمعرف الفيديو المباشر): {tracks[0].title}")
                    return tracks[0]
            except Exception as e:
                print(f"فشل تحليل YouTube بالطريقة 2 (معرف الفيديو المباشر): {str(e)}")
        
        # محاولة 3: استخدام node.get_tracks
        try:
            tracks = await node.get_tracks(clean_url)
            if tracks:
                await message.edit(content=f"✅ تم العثور على المحتوى (باستخدام node): {tracks[0].title}")
                return tracks[0]
        except Exception as e:
            print(f"فشل تحليل YouTube بالطريقة 3: {str(e)}")
        
        # محاولة 4: استخدام ytsearch مباشرة
        if video_id:
            try:
                search_query = f"ytsearch:{video_id}"
                tracks = await node.get_tracks(search_query)
                if tracks:
                    await message.edit(content=f"✅ تم العثور على المحتوى (باستخدام معرف البحث): {tracks[0].title}")
                    return tracks[0]
            except Exception as e:
                print(f"فشل تحليل YouTube بالطريقة 4: {str(e)}")
        
        # محاولة 5: استخدام نموذج بحث للنص المستخرج من الرابط
        try:
            # استخراج نص من الرابط بمحاولة الحصول على عنوان الفيديو من الرابط
            url_parts = url.split('/')
            if len(url_parts) > 3:
                search_text = url_parts[-1]
                # إذا كان الرابط يحتوي على معلمات، استخدم الجزء قبل علامة الاستفهام
                if '?' in search_text:
                    search_text = search_text.split('?')[0]
                # تنظيف النص
                search_text = search_text.replace('-', ' ').replace('_', ' ')
                
                # استخدام النص في بحث
                search_query = f"ytsearch:{search_text}"
                tracks = await node.get_tracks(search_query)
                if tracks:
                    await message.edit(content=f"✅ تم العثور على محتوى مشابه: {tracks[0].title}")
                    return tracks[0]
        except Exception as e:
            print(f"فشل تحليل YouTube بالطريقة 5: {str(e)}")
        
        # إذا وصلنا إلى هنا، فقد فشلت جميع المحاولات
        await message.edit(content="❌ لم يتم العثور على محتوى صالح في رابط YouTube المحدد. تأكد من أن الرابط صحيح.")
        return None

    async def _resolve_soundcloud(self, url, node, message):
        """معالجة روابط ساوند كلاود"""
        try:
            # استخدام get_tracks
            tracks = await node.get_tracks(url)
            if tracks:
                await message.edit(content=f"✅ تم العثور على مسار SoundCloud: {tracks[0].title}")
                return tracks[0]
        except Exception as e:
            print(f"فشل تحليل SoundCloud بالطريقة 1: {str(e)}")
        
        # محاولة باستخدام scsearch
        try:
            search_query = f"scsearch:{url.split('/')[-1]}"
            tracks = await node.get_tracks(search_query)
            if tracks:
                await message.edit(content=f"✅ تم العثور على مسار SoundCloud بديل: {tracks[0].title}")
                return tracks[0]
        except Exception as e:
            print(f"فشل تحليل SoundCloud بالطريقة 2: {str(e)}")
        
        # إذا وصلنا إلى هنا، فقد فشلت جميع المحاولات، حاول البحث عن طريق يوتيوب
        await message.edit(content="⚠️ تعذر تحليل رابط SoundCloud. محاولة البحث عن محتوى مشابه...")
        try:
            title_part = url.split('/')[-1].replace('-', ' ')
            return await self._search_youtube(f"soundcloud {title_part}", node, message)
        except Exception:
            await message.edit(content="❌ لم يتم العثور على محتوى صالح في رابط SoundCloud المحدد.")
            return None

    async def _resolve_spotify(self, url, node, message):
        """معالجة روابط سبوتيفاي"""
        try:
            # استخدام DecodeSpotify
            decoded = await wavelink.Playable.search(url)
            if isinstance(decoded, wavelink.Playlist):
                # إذا كان الرابط لقائمة تشغيل، استخدم المسار الأول
                if decoded.tracks:
                    await message.edit(content=f"⚠️ تم اكتشاف قائمة تشغيل Spotify بها {len(decoded.tracks)} أغنية. سيتم تشغيل الأغنية الأولى فقط.")
                    return decoded.tracks[0]
            elif decoded:
                return decoded
        except Exception as e:
            print(f"فشل تحليل Spotify بالطريقة 1: {str(e)}")
        
        try:
            # البحث اليدوي عن طريق استخراج معلومات الأغنية (الاسم + الفنان)
            # استخرج المعرف من الرابط
            spotify_pattern = re.compile(r'spotify\.com/track/([a-zA-Z0-9]+)')
            match = spotify_pattern.search(url)
            if match:
                # استخدم المعرف في بحث يوتيوب
                return await self._search_youtube(f"spotify track {match.group(1)}", node, message)
        except Exception as e:
            print(f"فشل تحليل Spotify بالطريقة 2: {str(e)}")
        
        # إذا وصلنا إلى هنا، فقد فشلت جميع المحاولات، حاول البحث عن طريق يوتيوب
        await message.edit(content="⚠️ تعذر تحليل رابط Spotify. محاولة البحث عن محتوى مشابه...")
        try:
            title_part = url.split('/')[-1].replace('-', ' ')
            return await self._search_youtube(f"spotify {title_part}", node, message)
        except Exception:
            await message.edit(content="❌ لم يتم العثور على محتوى صالح في رابط Spotify المحدد.")
            return None

    async def _resolve_generic_url(self, url, node, message):
        """معالجة الروابط العامة"""
        await message.edit(content=f"🔍 جاري محاولة تشغيل الرابط: {url[:30]}...")
        
        # محاولة 1: استخدام Track عام
        try:
            tracks = await node.get_tracks(url)
            if tracks:
                await message.edit(content=f"✅ تم العثور على المحتوى: {tracks[0].title or 'محتوى صوتي'}")
                return tracks[0]
        except Exception as e:
            print(f"فشل تحليل الرابط العام بالطريقة 1: {str(e)}")
        
        # محاولة 2: استخدام ytsearch مع URL
        try:
            search_query = f"ytsearch:{url}"
            tracks = await node.get_tracks(search_query)
            if tracks:
                await message.edit(content=f"✅ تم العثور على بديل للرابط: {tracks[0].title}")
                return tracks[0]
        except Exception as e:
            print(f"فشل تحليل الرابط العام بالطريقة 2: {str(e)}")
        
        # محاولة 3: استخدام معالجات محددة حسب اسم المجال
        domain = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if domain:
            domain_name = domain.group(1).lower()
            
            # روابط Facebook
            if "facebook.com" in domain_name or "fb.com" in domain_name:
                await message.edit(content="⚠️ روابط Facebook غير مدعومة مباشرة. جاري البحث عن بديل...")
                # استخراج اسم الفيديو أو عنوان المحتوى
                title_match = re.search(r'/videos/[^/]+/([^/?]+)', url)
                search_term = title_match.group(1).replace('-', ' ') if title_match else "facebook video"
                return await self._search_youtube(search_term, node, message)
            
            # روابط مواقع التواصل الأخرى
            elif any(site in domain_name for site in ["instagram.com", "twitter.com", "x.com", "tiktok.com"]):
                await message.edit(content=f"⚠️ روابط {domain_name} غير مدعومة مباشرة. جاري البحث عن بديل...")
                # استخراج أي معرفات مفيدة من عنوان URL
                last_part = url.split('/')[-1]
                search_term = last_part.replace('-', ' ').replace('_', ' ')
                if len(search_term) > 3:
                    return await self._search_youtube(f"{domain_name} {search_term}", node, message)
                else:
                    return await self._search_youtube(f"{domain_name} video", node, message)
        
        # محاولة 4: فحص إذا كان الرابط يحتوي على معلومات m3u8 (بث مباشر)
        if url.endswith(".m3u8") or "m3u8" in url:
            try:
                # محاولة استخدام get_tracks مع تحديد خيار بث
                tracks = await node.get_tracks(url)
                if tracks:
                    await message.edit(content=f"✅ تم العثور على بث مباشر")
                    return tracks[0]
            except Exception as e:
                print(f"فشل تحليل البث المباشر: {str(e)}")
                await message.edit(content="❌ تعذر تشغيل البث المباشر. قد يكون تنسيق الرابط غير مدعوم.")
        
        # محاولة 5: استخراج نص من الرابط وبحث كآخر محاولة
        try:
            # استخراج نص من الرابط
            url_parts = url.split('/')
            last_part = url_parts[-1] if url_parts else ""
            
            # تنظيف النص
            search_text = last_part.replace('.html', '').replace('.php', '').replace('-', ' ').replace('_', ' ')
            
            # إذا كان البحث ثريًا بما يكفي، استخدمه للبحث
            if len(search_text) > 3 and not search_text.isdigit():
                await message.edit(content=f"⚠️ تعذر تشغيل الرابط مباشرة. جاري محاولة البحث عن: {search_text}")
                return await self._search_youtube(search_text, node, message)
        except Exception as e:
            print(f"فشل تحليل نص الرابط: {str(e)}")
        
        # إذا وصلنا إلى هنا، فقد فشلت جميع المحاولات
        await message.edit(content="❌ لم يتم العثور على محتوى صالح في الرابط المحدد. تأكد من صحة الرابط أو جرب رابطًا آخر.")
        return None

    async def _search_youtube(self, query, node, message):
        """البحث في يوتيوب"""
        original_query = query
        await message.edit(content=f"🔍 جاري البحث في YouTube عن: {query[:40]}{'...' if len(query) > 40 else ''}")
        
        # محاولة 1: استخدام YouTubeTrack.search
        try:
            tracks = await wavelink.YouTubeTrack.search(query)
            if tracks:
                track = tracks[0]  # الحصول على المسار الأول
                await message.edit(content=f"✅ تم العثور على: {track.title}")
                return track
        except Exception as e:
            print(f"فشل البحث في YouTube بالطريقة 1: {str(e)}")
        
        # محاولة 2: البحث عبر العقدة المحددة
        try:
            search_query = f"ytsearch:{query}"
            tracks = await node.get_tracks(search_query)
            if tracks:
                track = tracks[0]  # الحصول على المسار الأول
                await message.edit(content=f"✅ تم العثور على: {track.title}")
                return track
        except Exception as e:
            print(f"فشل البحث في YouTube بالطريقة 2: {str(e)}")
        
        # محاولة 3: تبسيط البحث
        if len(query.split()) > 2:
            # تبسيط الاستعلام باستخدام أول كلمتين فقط
            simplified_query = ' '.join(query.split()[:2])
            try:
                search_query = f"ytsearch:{simplified_query}"
                tracks = await node.get_tracks(search_query)
                if tracks:
                    track = tracks[0]
                    await message.edit(content=f"✅ تم العثور على نتيجة مشابهة: {track.title}")
                    return track
            except Exception as e:
                print(f"فشل البحث المبسط: {str(e)}")
        
        # محاولة 4: ترجمة الاستعلام إذا كان باللغة العربية
        if any('\u0600' <= c <= '\u06FF' for c in query):  # التحقق من وجود أحرف عربية
            try:
                # استخدام استعلام يحتوي على "arabic" لتحسين النتائج
                enhanced_query = f"arabic {' '.join(query.split()[:3])}"
                search_query = f"ytsearch:{enhanced_query}"
                tracks = await node.get_tracks(search_query)
                if tracks:
                    track = tracks[0]
                    await message.edit(content=f"✅ تم العثور على نتيجة للبحث العربي: {track.title}")
                    return track
            except Exception as e:
                print(f"فشل البحث باللغة العربية: {str(e)}")
        
        # إذا وصلنا إلى هنا، فقد فشلت جميع المحاولات
        await message.edit(content=f"❌ لم يتم العثور على نتائج للبحث: '{original_query}'.\nحاول استخدام كلمات بحث مختلفة أو رابط مباشر.")
        return None

    async def _add_to_queue(self, ctx, player, track, message):
        """إضافة المسار إلى قائمة الانتظار"""
        # إضافة المحتوى إلى قائمة الانتظار
        if ctx.guild.id not in self.song_queue:
            self.song_queue[ctx.guild.id] = []
        
        self.song_queue[ctx.guild.id].append(track)
        
        # إنشاء رسالة تأكيد
        embed = discord.Embed(
            title="🎵 تمت إضافة محتوى إلى قائمة الانتظار",
            description=f"**{track.title}**",
            color=discord.Color.green()
        )
        
        # إضافة معلومات إضافية
        embed.add_field(name="المدة", value=self._format_duration(track.duration), inline=True)
        embed.add_field(name="الموقع في القائمة", value=f"#{len(self.song_queue[ctx.guild.id])}", inline=True)
        embed.add_field(name="مطلوبة بواسطة", value=ctx.author.mention, inline=True)
        
        # إضافة صورة مصغرة
        if hasattr(track, 'identifier'):
            embed.set_thumbnail(url=f"https://img.youtube.com/vi/{track.identifier}/maxresdefault.jpg")
        
        # إرسال الرسالة
        await message.edit(content=None, embed=embed)
        return True

    async def _play_track(self, ctx, player, track, message):
        """تشغيل المسار مباشرة مع تحسين الأداء"""
        try:
            # ضبط خصائص المشغل إذا لم تكن موجودة
            if not hasattr(player, 'text_channel'):
                player.text_channel = ctx.channel
            
            # ضبط مستوى الصوت الافتراضي للتأكد من أن الصوت مسموع
            try:
                current_volume = getattr(player, 'volume', 0)
                if current_volume <= 10:  # إذا كان الصوت منخفضًا جدًا
                    await player.set_volume(70)
            except Exception as e:
                print(f"لا يمكن ضبط مستوى الصوت: {str(e)}")
            
            # محاولة تشغيل المسار
            try:
                await player.play(track)
                # تسجيل المسار الحالي
                self.now_playing[ctx.guild.id] = track
            except Exception as e:
                print(f"خطأ في تشغيل المسار: {str(e)}")
                # محاولة إعادة الاتصال ثم تشغيل
                try:
                    print("محاولة إعادة الاتصال بالقناة الصوتية...")
                    voice_channel = ctx.author.voice.channel
                    await player.disconnect()
                    player = await voice_channel.connect(cls=wavelink.Player)
                    player.text_channel = ctx.channel
                    await player.set_volume(70)
                    await player.play(track)
                    self.now_playing[ctx.guild.id] = track
                except Exception as e2:
                    print(f"فشلت محاولة إعادة الاتصال: {str(e2)}")
                    await message.edit(content=f"❌ حدث خطأ أثناء تشغيل المسار: {str(e)}. فشلت محاولة إعادة الاتصال.")
                    return False
            
            # إنشاء رسالة تأكيد
            embed = discord.Embed(
                title="🎵 الآن يتم تشغيل",
                description=f"**{track.title}**",
                color=discord.Color.blue()
            )
            
            # إضافة معلومات إضافية
            embed.add_field(name="المدة", value=self._format_duration(track.duration), inline=True)
            embed.add_field(name="مطلوبة بواسطة", value=ctx.author.mention, inline=True)
            
            # إضافة صورة مصغرة للفيديو
            thumbnail_url = None
            
            # محاولة الحصول على صورة مصغرة من معرف YouTube
            if hasattr(track, 'identifier') and track.identifier:
                thumbnail_url = f"https://img.youtube.com/vi/{track.identifier}/maxresdefault.jpg"
                embed.set_thumbnail(url=thumbnail_url)
            
            # استخراج معرف الفيديو من الرابط إذا كان متاحًا
            elif hasattr(track, 'uri') and self._is_youtube_url(track.uri):
                youtube_id = self._extract_youtube_id(track.uri)
                if youtube_id:
                    thumbnail_url = f"https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg"
                    embed.set_thumbnail(url=thumbnail_url)
            
            # إضافة نوع المصدر
            source_type = self._get_source_type(track.uri if hasattr(track, 'uri') else "")
            if source_type:
                embed.add_field(name="المصدر", value=source_type, inline=True)
            
            # إضافة رابط مباشر إذا كان متاحًا
            if hasattr(track, 'uri') and track.uri:
                # إضافة زر للرابط الأصلي
                view = discord.ui.View()
                view.add_item(discord.ui.Button(
                    label="فتح الرابط الأصلي",
                    url=track.uri,
                    style=discord.ButtonStyle.url
                ))
                
                # إنشاء أزرار التحكم
                music_view = MusicButtons(self.bot, ctx)
                for item in music_view.children:
                    view.add_item(item)
                
                # إرسال الرسالة
                await message.edit(content=None, embed=embed, view=view)
            else:
                # إنشاء أزرار التحكم بدون رابط
                view = MusicButtons(self.bot, ctx)
                await message.edit(content=None, embed=embed, view=view)
            
            return True
        except Exception as e:
            await message.edit(content=f"❌ حدث خطأ أثناء تشغيل المسار: {str(e)}")
            print(f"خطأ في تشغيل المسار: {str(e)}")
            return False
    
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

    async def _resolve_direct_file(self, url, node, message):
        """معالجة روابط الملفات المباشرة"""
        await message.edit(content=f"🔍 جاري تحليل ملف صوتي مباشر...")
        
        try:
            # استخدام node.get_tracks
            tracks = await node.get_tracks(url)
            if tracks:
                await message.edit(content=f"✅ تم تحليل الملف الصوتي: {tracks[0].title or 'ملف صوتي مباشر'}")
                return tracks[0]
        except Exception as e:
            print(f"فشل تحليل الملف المباشر: {str(e)}")
            await message.edit(content="❌ تعذر تحليل الملف الصوتي. تأكد من أن الرابط صحيح ويشير إلى ملف صوتي مدعوم.")
            return None

async def setup(bot):
    """إعداد الصنف"""
    await bot.add_cog(MusicPlayer(bot)) 