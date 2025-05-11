import discord
from discord.ext import commands
import wavelink
import asyncio
import re
from typing import Dict, Optional, Union, Set
import logging

# Setup logger
logger = logging.getLogger(__name__)

class MusicControlView(discord.ui.View):
    """واجهة التحكم بالصوت في الغرفة المؤقتة"""
    
    def __init__(self, bot, voice_channel_id, text_channel_id):
        super().__init__(timeout=None)  # No timeout - persistent view
        self.bot = bot
        self.voice_channel_id = voice_channel_id
        self.text_channel_id = text_channel_id
        self.url_input = None
    
    @discord.ui.button(label="تشغيل", style=discord.ButtonStyle.green, custom_id="temp_voice_play")
    async def play_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر تشغيل المحتوى الصوتي"""
        # Create modal for URL input
        modal = MusicURLModal(self.bot, self.voice_channel_id, self.text_channel_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="إغلاق الغرفة", style=discord.ButtonStyle.red, custom_id="temp_voice_close")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر إغلاق الغرفة الصوتية يدويًا"""
        # Get voice channel
        voice_channel = self.bot.get_channel(self.voice_channel_id)
        if not voice_channel:
            await interaction.response.send_message("❌ لم يتم العثور على الغرفة الصوتية.", ephemeral=True)
            return
        
        # Get text channel
        text_channel = self.bot.get_channel(self.text_channel_id)
        
        # Check if user is the creator or has manage channels permission
        guild = voice_channel.guild
        member = guild.get_member(interaction.user.id)
        
        if not member:
            await interaction.response.send_message("❌ حدث خطأ أثناء التحقق من صلاحياتك.", ephemeral=True)
            return
        
        # Check if user has permission to close the channel
        temp_voice_cog = self.bot.get_cog("TempVoice")
        is_creator = False
        
        if temp_voice_cog and guild.id in temp_voice_cog.channel_creators:
            if voice_channel.id in temp_voice_cog.channel_creators[guild.id]:
                creator_id = temp_voice_cog.channel_creators[guild.id][voice_channel.id]
                is_creator = (creator_id == interaction.user.id)
        
        if not (is_creator or member.guild_permissions.manage_channels):
            await interaction.response.send_message("❌ ليس لديك صلاحية إغلاق هذه الغرفة.", ephemeral=True)
            return
        
        # Disconnect bot if connected
        try:
            player = wavelink.Pool.get_node().get_player(guild.id)
            if player and player.channel and player.channel.id == voice_channel.id:
                await player.disconnect()
                
                # Clean up queue and now playing
                if temp_voice_cog:
                    if guild.id in temp_voice_cog.song_queue:
                        temp_voice_cog.song_queue[guild.id] = []
                    
                    if guild.id in temp_voice_cog.now_playing:
                        del temp_voice_cog.now_playing[guild.id]
        except Exception as e:
            logger.error(f"Error disconnecting player: {str(e)}")
        
        # Move all members out of the voice channel
        try:
            for member in voice_channel.members:
                await member.move_to(None)
        except Exception as e:
            logger.error(f"Error moving members: {str(e)}")
        
        # Delete channels
        try:
            await interaction.response.send_message("✅ جاري إغلاق الغرفة...", ephemeral=True)
            
            if text_channel:
                await text_channel.delete(reason="تم إغلاق الغرفة الصوتية المؤقتة يدويًا")
            
            await voice_channel.delete(reason="تم إغلاق الغرفة الصوتية المؤقتة يدويًا")
            
            # Remove from tracking
            if temp_voice_cog:
                if guild.id in temp_voice_cog.temp_channels and voice_channel.id in temp_voice_cog.temp_channels[guild.id]:
                    del temp_voice_cog.temp_channels[guild.id][voice_channel.id]
                    if not temp_voice_cog.temp_channels[guild.id]:
                        del temp_voice_cog.temp_channels[guild.id]
                
                # Remove from game channels
                if guild.id in temp_voice_cog.game_channels and voice_channel.id in temp_voice_cog.game_channels:
                    temp_voice_cog.game_channels.remove(voice_channel.id)
                
                # Remove from channel creators
                if guild.id in temp_voice_cog.channel_creators and voice_channel.id in temp_voice_cog.channel_creators[guild.id]:
                    del temp_voice_cog.channel_creators[guild.id][voice_channel.id]
            
            logger.info(f"Manually deleted temporary voice channel in {guild.name}")
        except Exception as e:
            logger.error(f"Error deleting temporary channels: {str(e)}")
            await interaction.followup.send(f"❌ حدث خطأ أثناء إغلاق الغرفة: {str(e)}", ephemeral=True)


class MusicURLModal(discord.ui.Modal, title="تشغيل محتوى صوتي"):
    """نافذة إدخال رابط المحتوى الصوتي"""
    
    url_input = discord.ui.TextInput(
        label="أدخل رابط التشغيل",
        placeholder="رابط YouTube أو أي رابط صوتي آخر",
        required=True,
        style=discord.TextStyle.short
    )
    
    def __init__(self, bot, voice_channel_id, text_channel_id):
        super().__init__()
        self.bot = bot
        self.voice_channel_id = voice_channel_id
        self.text_channel_id = text_channel_id
    
    async def on_submit(self, interaction: discord.Interaction):
        """عند تقديم النموذج"""
        await interaction.response.defer(ephemeral=True)
        
        url = self.url_input.value.strip()
        
        # Get voice channel
        voice_channel = self.bot.get_channel(self.voice_channel_id)
        if not voice_channel:
            await interaction.followup.send("❌ لم يتم العثور على الغرفة الصوتية.", ephemeral=True)
            return
        
        # Get text channel
        text_channel = self.bot.get_channel(self.text_channel_id)
        if not text_channel:
            await interaction.followup.send("❌ لم يتم العثور على غرفة الدردشة.", ephemeral=True)
            return
        
        # Check if URL is valid
        url_pattern = re.compile(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
        if not url_pattern.match(url):
            await interaction.followup.send("❌ الرابط غير صالح. يرجى إدخال رابط صحيح.", ephemeral=True)
            return
        
        # Connect to voice channel if not already connected
        try:
            # Check if already connected
            player = wavelink.Pool.get_node().get_player(voice_channel.guild.id)
            if not player:
                # Connect to voice channel
                player = await voice_channel.connect(cls=wavelink.Player)
            
            # Set text channel for notifications
            player.text_channel = text_channel
            
            # Search for track
            is_youtube = "youtube.com" in url or "youtu.be" in url
            
            # Process based on URL type
            if is_youtube:
                tracks = await wavelink.YouTubeTrack.search(url)
            else:
                tracks = await wavelink.Track.search(url)
            
            if not tracks:
                await interaction.followup.send("❌ لم يتم العثور على محتوى صالح للتشغيل في الرابط المحدد.", ephemeral=True)
                return
            
            track = tracks[0]
            track.requester = interaction.user
            
            # Play the track
            if player.playing:
                # Add to queue
                temp_voice_cog = self.bot.get_cog("TempVoice")
                if temp_voice_cog:
                    if not hasattr(temp_voice_cog, "song_queue"):
                        temp_voice_cog.song_queue = {}
                    
                    guild_id = voice_channel.guild.id
                    if guild_id not in temp_voice_cog.song_queue:
                        temp_voice_cog.song_queue[guild_id] = []
                    
                    temp_voice_cog.song_queue[guild_id].append(track)
                    
                    await interaction.followup.send(f"✅ تمت إضافة **{track.title}** إلى قائمة الانتظار.", ephemeral=True)
            else:
                # Play immediately
                await player.play(track)
                
                # Store currently playing track
                temp_voice_cog = self.bot.get_cog("TempVoice")
                if temp_voice_cog:
                    if not hasattr(temp_voice_cog, "now_playing"):
                        temp_voice_cog.now_playing = {}
                    
                    temp_voice_cog.now_playing[voice_channel.guild.id] = track
                
                # Create embed with track info
                embed = discord.Embed(
                    title="🎵 الآن يتم تشغيل",
                    description=f"**{track.title}**",
                    color=discord.Color.blue()
                )
                
                # Add duration and requester
                embed.add_field(name="المدة", value=self._format_duration(track.duration), inline=True)
                embed.add_field(name="مطلوبة بواسطة", value=interaction.user.mention, inline=True)
                
                # Add thumbnail if from YouTube
                if is_youtube and hasattr(track, 'identifier'):
                    embed.set_thumbnail(url=f"https://img.youtube.com/vi/{track.identifier}/maxresdefault.jpg")
                
                await text_channel.send(embed=embed)
                await interaction.followup.send("✅ تم بدء تشغيل المحتوى الصوتي.", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error playing track: {str(e)}")
            await interaction.followup.send(f"❌ حدث خطأ أثناء تشغيل المحتوى: {str(e)}", ephemeral=True)
    
    def _format_duration(self, duration_ms: int) -> str:
        """تنسيق مدة المحتوى الصوتي"""
        seconds = int(duration_ms / 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"


class TempVoice(commands.Cog):
    """نظام الغرف الصوتية المؤقتة"""
    
    def __init__(self, bot):
        self.bot = bot
        self.temp_channels: Dict[int, Dict[str, int]] = {}  # {guild_id: {voice_channel_id: text_channel_id}}
        self.create_channel_name = "إنشاء غرفة صوتية"
        self.song_queue = {}  # {guild_id: [tracks]}
        self.now_playing = {}  # {guild_id: track}
        self.game_channels: Set[int] = set()  # Set of voice channel IDs used for games
        self.channel_creators: Dict[int, Dict[int, int]] = {}  # {guild_id: {channel_id: creator_id}}
    
    @commands.Cog.listener()
    async def on_ready(self):
        """يتم استدعاؤها عندما يكون البوت جاهزاً"""
        logger.info("✅ تم تحميل نظام الغرف الصوتية المؤقتة")
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """يتم استدعاؤها عند تغيير حالة الصوت للعضو"""
        # Skip bot voice state updates
        if member.bot:
            return
        
        # Handle channel creation
        if after.channel and after.channel.name == self.create_channel_name:
            await self._create_temp_channel(member, after.channel)
        
        # Handle channel deletion
        if before.channel and not after.channel:
            # Check if this is a game channel
            if before.channel.id in self.game_channels:
                # Don't delete game channels when empty
                return
            
            await self._check_empty_channel(before.channel)
    
    async def _create_temp_channel(self, member: discord.Member, create_channel: discord.VoiceChannel):
        """إنشاء غرفة صوتية مؤقتة"""
        guild = member.guild
        
        try:
            # Create voice channel
            voice_channel = await guild.create_voice_channel(
                name=f"غرفة {member.display_name}",
                category=create_channel.category,
                reason="إنشاء غرفة صوتية مؤقتة"
            )
            
            # Set permissions for the creator
            await voice_channel.set_permissions(member, connect=True, speak=True)
            
            # Create text channel (visible only to the creator and the bot)
            text_channel = await guild.create_text_channel(
                name=f"تحكم-{member.display_name}",
                category=create_channel.category,
                reason="إنشاء غرفة نصية للتحكم بالغرفة الصوتية المؤقتة"
            )
            
            # Set permissions for the text channel
            await text_channel.set_permissions(guild.default_role, read_messages=False)
            await text_channel.set_permissions(member, read_messages=True, send_messages=True)
            await text_channel.set_permissions(self.bot.user, read_messages=True, send_messages=True)
            
            # Store channel IDs
            if guild.id not in self.temp_channels:
                self.temp_channels[guild.id] = {}
            
            self.temp_channels[guild.id][voice_channel.id] = text_channel.id
            
            # Store channel creator
            if guild.id not in self.channel_creators:
                self.channel_creators[guild.id] = {}
            
            self.channel_creators[guild.id][voice_channel.id] = member.id
            
            # Move member to the new voice channel
            await member.move_to(voice_channel)
            
            # Connect bot to the voice channel
            player = await voice_channel.connect(cls=wavelink.Player)
            player.text_channel = text_channel
            
            # Send welcome message with controls
            embed = discord.Embed(
                title=f"🎵 غرفة {member.display_name} الصوتية",
                description="أهلاً بك في غرفتك الصوتية المؤقتة!\nيمكنك استخدام الأزرار أدناه للتحكم بالمحتوى الصوتي.",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📝 تعليمات",
                value="1. أدخل رابط التشغيل في الحقل المخصص\n"
                      "2. اضغط على زر التشغيل\n"
                      "3. سيبدأ تشغيل المحتوى الصوتي في الغرفة\n"
                      "4. استخدم الأمر `!h` للألعاب لمنع إغلاق الغرفة تلقائيًا",
                inline=False
            )
            
            # Create view with controls
            view = MusicControlView(self.bot, voice_channel.id, text_channel.id)
            
            await text_channel.send(embed=embed, view=view)
            
            logger.info(f"Created temporary voice channel for {member.display_name} in {guild.name}")
            
        except Exception as e:
            logger.error(f"Error creating temporary voice channel: {str(e)}")
            # Move member back to the create channel if possible
            if member.voice:
                await member.move_to(create_channel)
    
    async def _check_empty_channel(self, channel: discord.VoiceChannel):
        """التحقق من الغرفة الصوتية إذا كانت فارغة"""
        # Wait a moment to ensure the channel is actually empty
        await asyncio.sleep(1)
        
        guild = channel.guild
        
        # Check if this is a temporary channel
        if guild.id in self.temp_channels and channel.id in self.temp_channels[guild.id]:
            # Check if the channel is empty (no non-bot members)
            if not any(not member.bot for member in channel.members):
                # Get associated text channel
                text_channel_id = self.temp_channels[guild.id][channel.id]
                text_channel = guild.get_channel(text_channel_id)
                
                # Disconnect bot if connected
                try:
                    player = wavelink.Pool.get_node().get_player(guild.id)
                    if player and player.channel and player.channel.id == channel.id:
                        await player.disconnect()
                        
                        # Clean up queue and now playing
                        if guild.id in self.song_queue:
                            self.song_queue[guild.id] = []
                        
                        if guild.id in self.now_playing:
                            del self.now_playing[guild.id]
                except Exception as e:
                    logger.error(f"Error disconnecting player: {str(e)}")
                
                # Delete channels
                try:
                    if text_channel:
                        await text_channel.delete(reason="الغرفة الصوتية المؤقتة أصبحت فارغة")
                    
                    await channel.delete(reason="الغرفة الصوتية المؤقتة أصبحت فارغة")
                    
                    # Remove from tracking
                    del self.temp_channels[guild.id][channel.id]
                    if not self.temp_channels[guild.id]:
                        del self.temp_channels[guild.id]
                    
                    # Remove from channel creators
                    if guild.id in self.channel_creators and channel.id in self.channel_creators[guild.id]:
                        del self.channel_creators[guild.id][channel.id]
                    
                    logger.info(f"Deleted empty temporary voice channel in {guild.name}")
                except Exception as e:
                    logger.error(f"Error deleting temporary channels: {str(e)}")
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track, reason):
        """عند انتهاء المسار"""
        guild_id = player.guild.id
        
        # Check if this is a temporary voice channel
        is_temp_channel = False
        for guild_data in self.temp_channels.values():
            if player.channel.id in guild_data:
                is_temp_channel = True
                break
        
        if not is_temp_channel:
            return
        
        # Check if there's content in the queue
        if guild_id in self.song_queue and self.song_queue[guild_id]:
            # Play next track in queue
            next_track = self.song_queue[guild_id].pop(0)
            await player.play(next_track)
            
            # Update current track
            self.now_playing[guild_id] = next_track
            
            # Send message with new track
            embed = discord.Embed(
                title="🎵 الآن يتم تشغيل",
                description=f"**{next_track.title}**",
                color=discord.Color.blue()
            )
            
            # Add duration and requester
            embed.add_field(name="المدة", value=self._format_duration(next_track.duration), inline=True)
            embed.add_field(name="مطلوبة بواسطة", value=next_track.requester.mention, inline=True)
            
            # Add thumbnail if from YouTube
            is_youtube = hasattr(next_track, 'uri') and ("youtube.com" in next_track.uri or "youtu.be" in next_track.uri)
            if is_youtube and hasattr(next_track, 'identifier'):
                embed.set_thumbnail(url=f"https://img.youtube.com/vi/{next_track.identifier}/maxresdefault.jpg")
            
            channel = player.text_channel
            if channel:
                await channel.send(embed=embed)
        else:
            # No additional content
            if guild_id in self.now_playing:
                del self.now_playing[guild_id]
    
    def _format_duration(self, duration_ms: int) -> str:
        """تنسيق مدة المحتوى الصوتي"""
        seconds = int(duration_ms / 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    @commands.command(
        name="إنشاء_غرفة",
        aliases=["create_voice", "temp_voice", "غرفة_صوتية"],
        description="إنشاء قناة إنشاء الغرف الصوتية المؤقتة"
    )
    @commands.has_permissions(administrator=True)
    async def create_voice_channel(self, ctx):
        """إنشاء قناة إنشاء الغرف الصوتية المؤقتة"""
        guild = ctx.guild
        
        try:
            # Check if channel already exists
            for channel in guild.voice_channels:
                if channel.name == self.create_channel_name:
                    await ctx.send(f"❌ قناة '{self.create_channel_name}' موجودة بالفعل!")
                    return
            
            # Create the channel
            channel = await guild.create_voice_channel(
                name=self.create_channel_name,
                reason="إنشاء قناة إنشاء الغرف الصوتية المؤقتة"
            )
            
            await ctx.send(f"✅ تم إنشاء قناة '{self.create_channel_name}' بنجاح!\n"
                          f"عندما يدخل أي عضو إلى هذه القناة، سيتم إنشاء غرفة صوتية مؤقتة له.")
            
        except Exception as e:
            await ctx.send(f"❌ حدث خطأ أثناء إنشاء القناة: {str(e)}")
    
    @commands.command(
        name="h",
        aliases=["game", "لعبة", "العاب"],
        description="تحويل الغرفة الصوتية إلى غرفة ألعاب (لا تغلق تلقائيًا)"
    )
    async def game_mode(self, ctx):
        """تحويل الغرفة الصوتية إلى غرفة ألعاب (لا تغلق تلقائيًا)"""
        # Check if user is in a voice channel
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ يجب أن تكون متصلاً بغرفة صوتية لاستخدام هذا الأمر.")
            return
        
        voice_channel = ctx.author.voice.channel
        guild_id = ctx.guild.id
        
        # Check if this is a temporary channel
        is_temp_channel = False
        if guild_id in self.temp_channels and voice_channel.id in self.temp_channels[guild_id]:
            is_temp_channel = True
        
        if not is_temp_channel:
            await ctx.send("❌ هذا الأمر متاح فقط في الغرف الصوتية المؤقتة.")
            return
        
        # Check if user is the creator or has manage channels permission
        is_creator = False
        if guild_id in self.channel_creators and voice_channel.id in self.channel_creators[guild_id]:
            creator_id = self.channel_creators[guild_id][voice_channel.id]
            is_creator = (creator_id == ctx.author.id)
        
        if not (is_creator or ctx.author.guild_permissions.manage_channels):
            await ctx.send("❌ يجب أن تكون منشئ الغرفة أو تملك صلاحيات إدارة القنوات لاستخدام هذا الأمر.")
            return
        
        # Add to game channels
        self.game_channels.add(voice_channel.id)
        
        # Send confirmation
        embed = discord.Embed(
            title="🎮 وضع الألعاب",
            description="تم تفعيل وضع الألعاب لهذه الغرفة. لن يتم إغلاقها تلقائيًا عند خروج الأعضاء منها.",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📝 ملاحظة",
            value="لإغلاق الغرفة يدويًا، استخدم زر 'إغلاق الغرفة' في غرفة التحكم.",
            inline=False
        )
        
        await ctx.send(embed=embed)


async def setup(bot):
    """إعداد الإضافة"""
    await bot.add_cog(TempVoice(bot))
