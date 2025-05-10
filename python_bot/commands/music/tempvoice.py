
import discord
from discord.ext import commands
import wavelink

class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_voice_rooms = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        create_channel_name = "إنشاء غرفة صوتية"
        
        # تحقق من الروم المُحدد لإنشاء غرف مؤقتة
        if after.channel and after.channel.name == create_channel_name:
            category = after.channel.category
            channel_name = f"غرفة {member.display_name}"
            temp_channel = await guild.create_voice_channel(channel_name, category=category)
            
            await member.move_to(temp_channel)
            self.user_voice_rooms[member.id] = temp_channel.id

            # البوت يدخل معه
            bot_member = guild.me
            if bot_member.voice is None:
                vc = await temp_channel.connect(cls=wavelink.Player)
            else:
                vc = bot_member.voice.channel

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.name != "bot-commands" or message.author.bot:
            return
        
        if not message.content.startswith("http"):
            return
        
        guild = message.guild
        author = message.author

        # تحقق إذا عنده روم مؤقت مسجل
        temp_channel_id = self.user_voice_rooms.get(author.id)
        if temp_channel_id is None:
            await message.channel.send("أنت مو في روم مؤقت.")
            return

        # تحقق إذا البوت موجود في الروم
        voice_client = discord.utils.get(self.bot.voice_clients, guild=guild)
        if voice_client is None or voice_client.channel.id != temp_channel_id:
            await message.channel.send("البوت مو في نفس الروم.")
            return

        # شغل الرابط
        try:
            track = await wavelink.YouTubeTrack.search(message.content, return_first=True)
            await voice_client.play(track)
            await message.channel.send(f"يتم الآن تشغيل: {track.title}")
        except Exception as e:
            await message.channel.send(f"حدث خطأ أثناء التشغيل: {e}")

async def setup(bot):
    await bot.add_cog(TempVoice(bot))
