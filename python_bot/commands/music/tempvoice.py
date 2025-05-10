
import discord
from discord.ext import commands
import wavelink
from discord import app_commands
import asyncio

# نموذج إدخال الرابط
class LinkModal(discord.ui.Modal, title="أدخل رابط التشغيل"):
    link = discord.ui.TextInput(
        label="رابط التشغيل",
        placeholder="أدخل رابط YouTube أو أي رابط صوتي آخر",
        required=True,
    )

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        self.view.link = self.link.value
        await interaction.response.defer()
        await self.view.play_button.callback(interaction)

# واجهة التحكم بالتشغيل
class MusicControlView(discord.ui.View):
    def __init__(self, cog, voice_channel_id, text_channel_id):
        super().__init__(timeout=None)
        self.cog = cog
        self.voice_channel_id = voice_channel_id
        self.text_channel_id = text_channel_id
        self.link = None

    @discord.ui.button(label="تشغيل", style=discord.ButtonStyle.green, custom_id="play_button")
    async def play_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # إذا لم يتم إدخال الرابط بعد، افتح النموذج
        if self.link is None:
            await interaction.response.send_modal(LinkModal(self))
            return

        # تحقق من وجود البوت في الروم الصوتي
        guild = interaction.guild
        voice_channel = guild.get_channel(self.voice_channel_id)
        
        if not voice_channel:
            await interaction.response.send_message("لم يتم العثور على الروم الصوتي.", ephemeral=True)
            return

        # تحقق من اتصال البوت
        voice_client = discord.utils.get(self.cog.bot.voice_clients, guild=guild)
        if voice_client is None or voice_client.channel.id != self.voice_channel_id:
            try:
                voice_client = await voice_channel.connect(cls=wavelink.Player)
            except Exception as e:
                await interaction.response.send_message(f"حدث خطأ أثناء الاتصال: {e}", ephemeral=True)
                return

        # تشغيل الرابط
        try:
            await interaction.response.defer()
            
            # تحقق من صحة الرابط وابحث عنه
            try:
                tracks = await wavelink.YouTubeTrack.search(self.link)
                if not tracks:
                    await interaction.followup.send("لم يتم العثور على نتائج للرابط المدخل.", ephemeral=True)
                    return
                track = tracks[0]
            except Exception as e:
                await interaction.followup.send(f"حدث خطأ أثناء البحث عن الرابط: {e}", ephemeral=True)
                return
            
            # تشغيل المسار
            await voice_client.play(track)
            
            # إرسال رسالة تأكيد
            embed = discord.Embed(
                title="🎵 يتم التشغيل الآن",
                description=f"**{track.title}**",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=track.thumbnail)
            embed.add_field(name="المدة", value=f"{int(track.duration // 60)}:{int(track.duration % 60):02d}")
            embed.add_field(name="طلب بواسطة", value=interaction.user.mention)
            
            await interaction.followup.send(embed=embed)
            
            # إعادة تعيين الرابط
            self.link = None
            
        except Exception as e:
            await interaction.followup.send(f"حدث خطأ أثناء التشغيل: {e}", ephemeral=True)

class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # قاموس لتخزين معلومات الغرف المؤقتة: {user_id: {"voice_id": voice_channel_id, "text_id": text_channel_id}}
        self.user_voice_rooms = {}
        # قاموس لتخزين معلومات واجهات التحكم: {text_channel_id: MusicControlView}
        self.control_views = {}

    @commands.Cog.listener()
    async def on_ready(self):
        # إعادة تسجيل واجهات التحكم بعد إعادة تشغيل البوت
        self.bot.add_view(MusicControlView(self, None, None))
        
        # الاتصال بخادم Lavalink
        try:
            # استخدام خادم Lavalink عام
            nodes = [
                wavelink.Node(
                    uri="https://lavalink.lexnet.cc",  # خادم Lavalink عام
                    password="lexn3tl4v4l1nk"         # كلمة المرور للخادم العام
                ),
                # يمكن إضافة خوادم أخرى كاحتياطي
                wavelink.Node(
                    uri="https://lavalink.devz.cloud",
                    password="devz.cloud"
                ),
                wavelink.Node(
                    uri="https://lavalink.api.xgstudios.net",
                    password="xgstudios.net"
                )
            ]
            await wavelink.Pool.connect(nodes=nodes, client=self.bot)
            print("[TempVoice] تم الاتصال بخادم Lavalink بنجاح")
        except Exception as e:
            print(f"[TempVoice] خطأ في الاتصال بخادم Lavalink: {e}")
            # محاولة الاتصال بخادم محلي إذا فشل الاتصال بالخوادم العامة
            try:
                local_node = wavelink.Node(
                    uri="http://localhost:2333",
                    password="youshallnotpass"
                )
                await wavelink.Pool.connect(nodes=[local_node], client=self.bot)
                print("[TempVoice] تم الاتصال بخادم Lavalink المحلي بنجاح")
            except Exception as e2:
                print(f"[TempVoice] خطأ في الاتصال بخادم Lavalink المحلي: {e2}")
                print("[TempVoice] لا يمكن الاتصال بأي خادم Lavalink. لن تعمل ميزة تشغيل الموسيقى.")



    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        create_channel_name = "إنشاء غرفة صوتية"
        
        # 1. إنشاء غرفة صوتية مؤقتة عند دخول المستخدم لقناة الإنشاء
        if after.channel and after.channel.name == create_channel_name:
            # إنشاء الغرفة الصوتية
            category = after.channel.category
            channel_name = f"غرفة {member.display_name}"
            
            # إنشاء الغرفة الصوتية
            temp_voice_channel = await guild.create_voice_channel(
                name=channel_name,
                category=category,
                reason=f"غرفة مؤقتة لـ {member.display_name}"
            )
            
            # إنشاء غرفة نصية خاصة
            temp_text_channel = await guild.create_text_channel(
                name=f"تحكم-{member.display_name}",
                category=category,
                reason=f"غرفة تحكم لـ {member.display_name}"
            )
            
            # تعيين صلاحيات الغرفة النصية
            # إخفاء الغرفة عن الجميع
            await temp_text_channel.set_permissions(guild.default_role, read_messages=False)
            # السماح للمستخدم بالوصول
            await temp_text_channel.set_permissions(member, read_messages=True, send_messages=True)
            # السماح للبوت بالوصول
            await temp_text_channel.set_permissions(guild.me, read_messages=True, send_messages=True)
            
            # نقل المستخدم للغرفة الجديدة
            await member.move_to(temp_voice_channel)
            
            # تخزين معلومات الغرف
            self.user_voice_rooms[member.id] = {
                "voice_id": temp_voice_channel.id,
                "text_id": temp_text_channel.id
            }
            
            # إنشاء واجهة التحكم
            view = MusicControlView(self, temp_voice_channel.id, temp_text_channel.id)
            self.control_views[temp_text_channel.id] = view
            
            # إرسال رسالة الترحيب مع واجهة التحكم
            embed = discord.Embed(
                title=f"🎵 مرحباً بك في غرفتك الخاصة",
                description="استخدم الأزرار أدناه للتحكم بالموسيقى",
                color=discord.Color.blue()
            )
            embed.add_field(name="أدخل رابط التشغيل", value="اضغط على زر التشغيل لإدخال رابط YouTube أو أي رابط صوتي آخر")
            embed.set_footer(text="سيتم حذف الغرفة تلقائياً عند خروج جميع الأعضاء منها")
            
            await temp_text_channel.send(embed=embed, view=view)
            
            # دخول البوت للغرفة الصوتية
            try:
                # تحقق إذا كان البوت متصل بغرفة أخرى
                if guild.me.voice and guild.me.voice.channel:
                    # إذا كان متصل بغرفة أخرى، افصله أولاً
                    voice_client = guild.voice_client
                    if voice_client:
                        await voice_client.disconnect(force=True)
                
                # اتصال البوت بالغرفة الجديدة
                await temp_voice_channel.connect(cls=wavelink.Player)
            except Exception as e:
                await temp_text_channel.send(f"حدث خطأ أثناء اتصال البوت: {e}")
        
        # 2. حذف الغرفة عند خروج جميع الأعضاء
        if before.channel:
            # تحقق إذا كانت غرفة مؤقتة (بالبحث في القاموس)
            temp_voice_channels = [room_data["voice_id"] for room_data in self.user_voice_rooms.values()]
            
            if before.channel.id in temp_voice_channels and len(before.channel.members) == 0:
                # البحث عن معلومات الغرفة
                user_id = None
                for uid, room_data in self.user_voice_rooms.items():
                    if room_data["voice_id"] == before.channel.id:
                        user_id = uid
                        break
                
                if user_id:
                    room_data = self.user_voice_rooms[user_id]
                    
                    # حذف الغرفة الصوتية
                    voice_channel = guild.get_channel(room_data["voice_id"])
                    if voice_channel:
                        await voice_channel.delete(reason="الغرفة المؤقتة أصبحت فارغة")
                    
                    # حذف الغرفة النصية
                    text_channel = guild.get_channel(room_data["text_id"])
                    if text_channel:
                        await text_channel.delete(reason="الغرفة المؤقتة أصبحت فارغة")
                    
                    # حذف معلومات الغرفة من القاموس
                    del self.user_voice_rooms[user_id]
                    
                    # حذف واجهة التحكم
                    if room_data["text_id"] in self.control_views:
                        del self.control_views[room_data["text_id"]]

async def setup(bot):
    await bot.add_cog(TempVoice(bot))
