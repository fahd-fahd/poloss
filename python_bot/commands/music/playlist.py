#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import datetime
import wavelink
from discord.ui import Button, View, Select

class PlaylistSelector(discord.ui.Select):
    """قائمة منسدلة لاختيار قائمة تشغيل"""
    
    def __init__(self, playlists, callback_func):
        self.callback_func = callback_func
        options = [
            discord.SelectOption(
                label=playlist["name"],
                description=f"{len(playlist['tracks'])} أغنية", 
                value=str(idx)
            ) for idx, playlist in enumerate(playlists)
        ]
        
        super().__init__(
            placeholder="اختر قائمة تشغيل...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        """عند اختيار قائمة تشغيل"""
        await self.callback_func(interaction, int(self.values[0]))

class PlaylistView(View):
    """عرض قوائم التشغيل مع الأزرار"""
    
    def __init__(self, bot, playlists, ctx, timeout=180):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.playlists = playlists
        self.ctx = ctx
        self.current_playlist = None
        
        # إضافة قائمة منسدلة للاختيار
        self.add_item(PlaylistSelector(playlists, self.on_playlist_select))
    
    async def on_playlist_select(self, interaction: discord.Interaction, playlist_idx):
        """معالجة اختيار قائمة تشغيل"""
        self.current_playlist = self.playlists[playlist_idx]
        
        embed = discord.Embed(
            title=f"🎵 قائمة التشغيل: {self.current_playlist['name']}",
            description=f"عدد الأغاني: {len(self.current_playlist['tracks'])}",
            color=discord.Color.blue()
        )
        
        # عرض الأغاني (بحد أقصى 10)
        track_list = ""
        for i, track in enumerate(self.current_playlist['tracks'][:10], 1):
            track_list += f"**{i}.** {track['title']} ({track['duration']})\n"
        
        # إذا كان هناك أكثر من 10 أغاني
        if len(self.current_playlist['tracks']) > 10:
            track_list += f"\n*...و {len(self.current_playlist['tracks']) - 10} أغاني أخرى*"
        
        embed.add_field(name="📋 الأغاني", value=track_list, inline=False)
        embed.set_footer(text="استخدم الأزرار أدناه للتحكم في قائمة التشغيل")
        
        await interaction.response.edit_message(embed=embed)
    
    @discord.ui.button(label="▶️ تشغيل الكل", style=discord.ButtonStyle.success)
    async def play_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر تشغيل كل الأغاني في القائمة"""
        if self.current_playlist is None:
            return await interaction.response.send_message("يرجى اختيار قائمة تشغيل أولاً.", ephemeral=True)
        
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب القائمة فقط.", ephemeral=True)
        
        # التحقق من وجود المستخدم في قناة صوتية
        if not interaction.user.voice:
            return await interaction.response.send_message("يجب أن تكون في قناة صوتية.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # الاتصال بالقناة الصوتية
            player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
        except Exception as e:
            try:
                # محاولة الحصول على مشغل موجود
                player = wavelink.NodePool.get_node().get_player(interaction.guild.id)
                if not player:
                    return await interaction.followup.send(f"حدث خطأ: {str(e)}", ephemeral=True)
            except Exception as e:
                return await interaction.followup.send(f"حدث خطأ: {str(e)}", ephemeral=True)
        
        # تخزين قناة النص للإشعارات
        player.text_channel = interaction.channel
        
        # الحصول على مرجع لنظام تشغيل الموسيقى
        music_cog = self.bot.get_cog("MusicPlayer")
        if not music_cog:
            return await interaction.followup.send("لم يتم العثور على نظام تشغيل الموسيقى.", ephemeral=True)
        
        # إضافة الأغاني إلى قائمة الانتظار
        for track_data in self.current_playlist['tracks']:
            try:
                search_query = f"ytsearch:{track_data['title']}"
                tracks = await wavelink.NodePool.get_node().get_tracks(wavelink.YouTubeTrack, search_query)
                if tracks:
                    track = tracks[0]
                    track.requester = interaction.user
                    
                    if not player.is_playing():
                        # تشغيل الأغنية الأولى مباشرة
                        await player.play(track)
                        music_cog.now_playing[interaction.guild.id] = track
                    else:
                        # إضافة بقية الأغاني إلى قائمة الانتظار
                        if interaction.guild.id not in music_cog.song_queue:
                            music_cog.song_queue[interaction.guild.id] = []
                        
                        music_cog.song_queue[interaction.guild.id].append(track)
            except Exception as e:
                print(f"خطأ في إضافة أغنية: {str(e)}")
        
        await interaction.followup.send(f"تمت إضافة {len(self.current_playlist['tracks'])} أغنية إلى قائمة التشغيل.", ephemeral=True)
    
    @discord.ui.button(label="🔄 تحديث", style=discord.ButtonStyle.primary)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر تحديث قوائم التشغيل"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لطالب القائمة فقط.", ephemeral=True)
        
        # إعادة تحميل القوائم
        user_id = interaction.user.id
        if hasattr(self.bot, 'db'):
            playlists_collection = self.bot.db.playlists
            playlists = await playlists_collection.find({"user_id": user_id}).to_list(length=100)
            self.playlists = playlists
        
        embed = discord.Embed(
            title="📋 قوائم التشغيل",
            description=f"تم العثور على {len(self.playlists)} قائمة تشغيل",
            color=discord.Color.blue()
        )
        
        if not self.playlists:
            embed.description = "لا توجد قوائم تشغيل متاحة. قم بإنشاء قائمة تشغيل باستخدام الأمر `!قائمة_جديدة`."
        
        # تحديث العرض
        self.clear_items()
        self.add_item(PlaylistSelector(self.playlists, self.on_playlist_select))
        self.add_item(button)  # إعادة إضافة زر التحديث
        self.add_item(self.play_all)  # إعادة إضافة زر التشغيل
        
        await interaction.response.edit_message(embed=embed, view=self)

class Playlist(commands.Cog):
    """نظام قوائم تشغيل الموسيقى"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name="قوائم_التشغيل",
        aliases=["playlists", "قوائمي", "قائمة_تشغيل"],
        description="عرض قوائم التشغيل الخاصة بك"
    )
    async def playlists(self, ctx):
        """
        عرض قوائم التشغيل الخاصة بك
        """
        # الحصول على قوائم التشغيل من قاعدة البيانات
        user_id = ctx.author.id
        playlists = []
        
        if hasattr(self.bot, 'db'):
            playlists_collection = self.bot.db.playlists
            playlists = await playlists_collection.find({"user_id": user_id}).to_list(length=100)
        
        embed = discord.Embed(
            title="📋 قوائم التشغيل",
            description=f"تم العثور على {len(playlists)} قائمة تشغيل",
            color=discord.Color.blue()
        )
        
        if not playlists:
            embed.description = "لا توجد قوائم تشغيل متاحة. قم بإنشاء قائمة تشغيل باستخدام الأمر `!قائمة_جديدة`."
        
        view = PlaylistView(self.bot, playlists, ctx)
        await ctx.send(embed=embed, view=view)
    
    @commands.command(
        name="قائمة_جديدة",
        aliases=["newplaylist", "create_playlist", "انشاء_قائمة"],
        description="إنشاء قائمة تشغيل جديدة"
    )
    async def create_playlist(self, ctx, *, name: str = None):
        """
        إنشاء قائمة تشغيل جديدة
        
        المعلمات:
            name (str): اسم قائمة التشغيل
        
        أمثلة:
            !قائمة_جديدة أغاني مفضلة
            !create_playlist My Favorites
        """
        if not name:
            embed = discord.Embed(
                title="❌ خطأ في الأمر",
                description=f"يرجى تحديد اسم لقائمة التشغيل.\n"
                           f"مثال: `!قائمة_جديدة أغاني مفضلة`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من وجود قاعدة بيانات
        if not hasattr(self.bot, 'db'):
            embed = discord.Embed(
                title="❌ خطأ",
                description="قاعدة البيانات غير متصلة. لا يمكن حفظ قوائم التشغيل.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من عدم وجود قائمة بنفس الاسم
        playlists_collection = self.bot.db.playlists
        existing_playlist = await playlists_collection.find_one({
            "user_id": ctx.author.id,
            "name": name
        })
        
        if existing_playlist:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"لديك بالفعل قائمة تشغيل باسم '{name}'.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # إنشاء قائمة جديدة
        new_playlist = {
            "user_id": ctx.author.id,
            "name": name,
            "tracks": [],
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        
        # حفظ في قاعدة البيانات
        await playlists_collection.insert_one(new_playlist)
        
        embed = discord.Embed(
            title="✅ تم إنشاء قائمة التشغيل",
            description=f"تم إنشاء قائمة التشغيل '{name}' بنجاح.\n"
                       f"استخدم الأمر `!اضف_اغنية {name} اسم الأغنية` لإضافة أغاني.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.command(
        name="اضف_اغنية",
        aliases=["add_to_playlist", "اضافة_اغنية", "أضف"],
        description="إضافة أغنية إلى قائمة تشغيل"
    )
    async def add_to_playlist(self, ctx, playlist_name: str = None, *, song_name: str = None):
        """
        إضافة أغنية إلى قائمة تشغيل
        
        المعلمات:
            playlist_name (str): اسم قائمة التشغيل
            song_name (str): اسم الأغنية
        
        أمثلة:
            !اضف_اغنية أغاني مفضلة despacito
            !add_to_playlist My Favorites Shape of You
        """
        if not playlist_name or not song_name:
            embed = discord.Embed(
                title="❌ خطأ في الأمر",
                description=f"يرجى تحديد اسم قائمة التشغيل واسم الأغنية.\n"
                           f"مثال: `!اضف_اغنية أغاني_مفضلة despacito`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من وجود قاعدة بيانات
        if not hasattr(self.bot, 'db'):
            embed = discord.Embed(
                title="❌ خطأ",
                description="قاعدة البيانات غير متصلة. لا يمكن حفظ قوائم التشغيل.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # البحث عن قائمة التشغيل
        playlists_collection = self.bot.db.playlists
        playlist = await playlists_collection.find_one({
            "user_id": ctx.author.id,
            "name": playlist_name
        })
        
        if not playlist:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"لم يتم العثور على قائمة تشغيل باسم '{playlist_name}'.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # رسالة انتظار
        loading_msg = await ctx.send("🔍 جاري البحث عن الأغنية...")
        
        try:
            # البحث عن الأغنية في YouTube
            search_query = f"ytsearch:{song_name}"
            tracks = await wavelink.NodePool.get_node().get_tracks(wavelink.YouTubeTrack, search_query)
            
            if not tracks:
                return await loading_msg.edit(content="❌ لم يتم العثور على نتائج للبحث.")
            
            track = tracks[0]
            
            # إضافة معلومات الأغنية إلى قائمة التشغيل
            track_info = {
                "title": track.title,
                "url": track.uri,
                "duration": self._format_duration(track.duration),
                "added_at": datetime.datetime.utcnow().isoformat()
            }
            
            # تحديث قائمة التشغيل في قاعدة البيانات
            await playlists_collection.update_one(
                {"_id": playlist["_id"]},
                {"$push": {"tracks": track_info}}
            )
            
            embed = discord.Embed(
                title="✅ تمت الإضافة",
                description=f"تمت إضافة **{track.title}** إلى قائمة التشغيل **{playlist_name}**.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=f"https://img.youtube.com/vi/{track.identifier}/maxresdefault.jpg")
            
            await loading_msg.edit(content=None, embed=embed)
            
        except Exception as e:
            await loading_msg.edit(content=f"❌ حدث خطأ أثناء محاولة إضافة الأغنية: {str(e)}")
            print(f"خطأ في أمر إضافة الأغنية: {str(e)}")
    
    @commands.command(
        name="حذف_قائمة",
        aliases=["delete_playlist", "حذف_قائمة_تشغيل"],
        description="حذف قائمة تشغيل"
    )
    async def delete_playlist(self, ctx, *, playlist_name: str = None):
        """
        حذف قائمة تشغيل
        
        المعلمات:
            playlist_name (str): اسم قائمة التشغيل
        
        أمثلة:
            !حذف_قائمة أغاني مفضلة
            !delete_playlist My Favorites
        """
        if not playlist_name:
            embed = discord.Embed(
                title="❌ خطأ في الأمر",
                description=f"يرجى تحديد اسم قائمة التشغيل المراد حذفها.\n"
                           f"مثال: `!حذف_قائمة أغاني_مفضلة`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من وجود قاعدة بيانات
        if not hasattr(self.bot, 'db'):
            embed = discord.Embed(
                title="❌ خطأ",
                description="قاعدة البيانات غير متصلة. لا يمكن حذف قوائم التشغيل.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # البحث عن قائمة التشغيل
        playlists_collection = self.bot.db.playlists
        playlist = await playlists_collection.find_one({
            "user_id": ctx.author.id,
            "name": playlist_name
        })
        
        if not playlist:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"لم يتم العثور على قائمة تشغيل باسم '{playlist_name}'.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # حذف قائمة التشغيل من قاعدة البيانات
        await playlists_collection.delete_one({"_id": playlist["_id"]})
        
        embed = discord.Embed(
            title="✅ تم الحذف",
            description=f"تم حذف قائمة التشغيل '{playlist_name}' بنجاح.",
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

async def setup(bot):
    """إعداد الصنف وإضافته إلى البوت"""
    await bot.add_cog(Playlist(bot)) 