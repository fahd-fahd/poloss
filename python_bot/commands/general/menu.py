#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
from discord import ui
import asyncio
import sys
import os
from pathlib import Path

# إضافة مسار البوت إلى مسار البحث
sys.path.append(str(Path(__file__).parent.parent.parent))

# استيراد وحدة الترجمة
try:
    from utils.translator import get_user_language, t
except ImportError:
    # دالة مؤقتة في حالة عدم وجود وحدة الترجمة
    def get_user_language(bot, user_id):
        return "ar"
    
    def t(key, language="ar"):
        return key

class MainMenuView(ui.View):
    """واجهة القائمة الرئيسية التفاعلية"""
    
    def __init__(self, bot, ctx, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
        # إضافة زر للتشغيل السريع
        self.add_item(QuickPlayButton())
        # إضافة زر الاختصارات الشاملة
        self.add_item(QuickShortcutsButton())
        # إضافة زر دخول الروم الصوتي
        self.add_item(JoinVoiceChannelButton())
    
    @ui.button(label="🎵 الموسيقى", style=discord.ButtonStyle.primary, emoji="🎵")
    async def music_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر قائمة الموسيقى"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إنشاء قائمة الموسيقى
        music_view = MusicMenuView(self.bot, self.ctx)
        
        # تحديث الرسالة بقائمة الموسيقى
        embed = discord.Embed(
            title="🎵 قائمة الموسيقى",
            description="اختر أحد خيارات الموسيقى أدناه أو استخدم الأوامر المباشرة:",
            color=discord.Color.blurple()
        )
        
        # إضافة معلومات عن الأوامر المباشرة
        embed.add_field(
            name="🔊 الأوامر السريعة",
            value="**!تشغيل** أو **!p** + رابط/اسم أغنية: لتشغيل موسيقى\n"
                  "**!إيقاف** أو **!s**: لإيقاف الموسيقى\n"
                  "**!تخطي** أو **!sk**: لتخطي الأغنية الحالية\n"
                  "**!صوت** أو **!v**: للتحكم بالصوت",
            inline=False
        )
        
        embed.set_footer(text="يمكنك استخدام أزرار التنقل أدناه أو الأوامر المباشرة")
        
        await interaction.response.edit_message(embed=embed, view=music_view)
    
    @ui.button(label="🎮 الألعاب", style=discord.ButtonStyle.success, emoji="🎮")
    async def games_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر قائمة الألعاب"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إنشاء قائمة الألعاب
        games_view = GamesMenuView(self.bot, self.ctx)
        
        # تحديث الرسالة بقائمة الألعاب
        embed = discord.Embed(
            title="🎮 قائمة الألعاب",
            description="اختر إحدى الألعاب أدناه أو استخدم الأوامر المباشرة:",
            color=discord.Color.green()
        )
        
        # إضافة معلومات عن الأوامر المباشرة
        embed.add_field(
            name="🎲 الأوامر السريعة",
            value="**!صيد** أو **!fish**: للعب الصيد\n"
                  "**!سباق** أو **!horserace**: للعب سباق الخيول\n"
                  "**!نرد** أو **!dice**: للعب النرد\n"
                  "**!بلاك_جاك** أو **!blackjack**: للعب بلاك جاك",
            inline=False
        )
        
        embed.set_footer(text="العب واربح المزيد من العملات!")
        
        await interaction.response.edit_message(embed=embed, view=games_view)
    
    @ui.button(label="💰 البنك", style=discord.ButtonStyle.secondary, emoji="💰")
    async def bank_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر قائمة البنك"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إنشاء قائمة البنك
        bank_view = BankMenuView(self.bot, self.ctx)
        
        # تحديث الرسالة بقائمة البنك
        embed = discord.Embed(
            title="💰 قائمة البنك",
            description="اختر أحد خيارات البنك أدناه أو استخدم الأوامر المباشرة:",
            color=discord.Color.gold()
        )
        
        # إضافة معلومات عن الأوامر المباشرة
        embed.add_field(
            name="💵 الأوامر السريعة",
            value="**!رصيد** أو **!balance**: لعرض رصيدك\n"
                  "**!يومي** أو **!daily**: للحصول على المكافأة اليومية\n"
                  "**!تحويل** أو **!transfer**: لتحويل الأموال\n"
                  "**!حماية** أو **!protection**: لحماية أموالك\n"
                  "**!سرقة** أو **!steal**: لمحاولة سرقة الآخرين",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ نظام الحماية",
            value="استخدم **!حماية** لشراء حماية من السرقة بثلاثة مستويات:\n"
                  "- 3 ساعات مقابل 2500 عملة\n"
                  "- 8 ساعات مقابل 5000 عملة\n"
                  "- 24 ساعة مقابل 15000 عملة",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=bank_view)
    
    @ui.button(label="🔗 انضمام لرابط", style=discord.ButtonStyle.primary, emoji="🔗", row=2)
    async def join_link_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر الانضمام لرابط دعوة"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إنشاء مودال للرابط
        class AllInOneInviteModal(ui.Modal, title="انضمام لرابط دعوة"):
            url_input = ui.TextInput(
                label="أدخل رابط الدعوة",
                placeholder="https://discord.gg/...",
                style=discord.TextStyle.short,
                required=True,
                max_length=200
            )
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                # رسالة الانتظار
                wait_embed = discord.Embed(
                    title="🔗 جاري الانضمام...",
                    description=f"جاري محاولة الانضمام إلى الرابط: `{self.url_input.value}`",
                    color=discord.Color.blue()
                )
                
                await modal_interaction.response.send_message(embed=wait_embed)
                
                # تنفيذ أمر الدعوة
                invite_command = self.bot.get_command('دعوة') or self.bot.get_command('invite')
                if invite_command:
                    invite_ctx = await self.bot.get_context(self.ctx.message)
                    try:
                        await invite_ctx.invoke(invite_command, invite_link=self.url_input.value)
                        
                        # تأكيد الانضمام
                        success_embed = discord.Embed(
                            title="✅ تم الانضمام بنجاح",
                            description=f"تم الانضمام إلى: `{self.url_input.value}`",
                            color=discord.Color.green()
                        )
                        
                        message = await modal_interaction.original_response()
                        try:
                            await message.edit(embed=success_embed)
                            # مسح الرسالة بعد 5 ثوانٍ
                            await asyncio.sleep(5)
                            await message.delete()
                        except:
                            pass
                    except Exception as e:
                        error_embed = discord.Embed(
                            title="❌ خطأ في الانضمام",
                            description=f"حدث خطأ أثناء محاولة الانضمام: `{str(e)}`",
                            color=discord.Color.red()
                        )
                        
                        message = await modal_interaction.original_response()
                        await message.edit(embed=error_embed)
                else:
                    error_embed = discord.Embed(
                        title="❌ خطأ",
                        description="عذراً، أمر الانضمام غير متاح حالياً.",
                        color=discord.Color.red()
                    )
                    
                    message = await modal_interaction.original_response()
                    await message.edit(embed=error_embed)
        
        # تخزين معرفات المستخدم والبوت للاستخدام في المودال
        self_bot = self.bot
        self_ctx = self.ctx
        
        # عرض المودال
        await interaction.response.send_modal(AllInOneInviteModal())
    
    @ui.button(label="❌ إغلاق", style=discord.ButtonStyle.danger, emoji="❌", row=1)
    async def close_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر إغلاق القائمة"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # حذف الرسالة
        await interaction.message.delete()
    
    async def on_timeout(self):
        """عند انتهاء مهلة القائمة"""
        # تعطيل جميع الأزرار
        for item in self.children:
            item.disabled = True
        
        # تحديث الرسالة
        try:
            await self.message.edit(view=self)
        except:
            pass


# إضافة زر دخول الروم الصوتي
class JoinVoiceChannelButton(ui.Button):
    """زر الانضمام إلى الروم الصوتي للمستخدم"""
    
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.success,
            label="🔊 دخول الروم الصوتي",
            emoji="🔊",
            row=2
        )
    
    async def callback(self, interaction: discord.Interaction):
        # التحقق من المستخدم
        view = self.view
        if interaction.user.id != view.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # التحقق ما إذا كان المستخدم في قناة صوتية
        if not interaction.user.voice:
            return await interaction.response.send_message(
                "أنت غير متواجد في أي روم صوتي! يرجى الانضمام إلى روم صوتي أولاً.",
                ephemeral=True
            )
        
        voice_channel = interaction.user.voice.channel
        
        # إنشاء رسالة توضيحية
        embed = discord.Embed(
            title="🔊 دخول الروم الصوتي",
            description=f"جاري الانضمام إلى الروم الصوتي: **{voice_channel.name}**",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # محاولة الانضمام للقناة الصوتية
        voice_cog = view.bot.get_cog('VoiceControl')
        if voice_cog:
            voice_ctx = await view.bot.get_context(view.ctx.message)
            voice_command = view.bot.get_command('صوت')
            if voice_command:
                try:
                    await voice_ctx.invoke(voice_command, channel_or_volume=str(voice_channel.id))
                    
                    # رسالة نجاح الانضمام
                    success_embed = discord.Embed(
                        title="✅ تم الانضمام بنجاح",
                        description=f"تم الانضمام إلى الروم الصوتي: **{voice_channel.name}**\n"
                                    f"يمكنك الآن استخدام أوامر الموسيقى مباشرة!",
                        color=discord.Color.green()
                    )
                    
                    # إضافة تلميح للاستخدام السريع
                    success_embed.add_field(
                        name="💡 تلميح سريع",
                        value="استخدم `!p` متبوعًا باسم الأغنية أو رابط يوتيوب للتشغيل مباشرة.",
                        inline=False
                    )
                    
                    await interaction.followup.send(embed=success_embed, ephemeral=True)
                except Exception as e:
                    error_embed = discord.Embed(
                        title="❌ خطأ في الانضمام",
                        description=f"حدث خطأ أثناء محاولة الانضمام إلى الروم الصوتي:\n`{str(e)}`",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=error_embed, ephemeral=True)
            else:
                await interaction.followup.send("عذراً، أمر الانضمام للروم الصوتي غير متاح حالياً.", ephemeral=True)
        else:
            await interaction.followup.send("عذراً، وحدة التحكم الصوتي غير متاحة حالياً.", ephemeral=True)
    
    async def on_timeout(self):
        """عند انتهاء مهلة القائمة"""
        # تعطيل جميع الأزرار
        for item in self.children:
            item.disabled = True
        
        # تحديث الرسالة
        try:
            await self.message.edit(view=self)
        except:
            pass


# إضافة زر للتشغيل السريع
class QuickPlayButton(ui.Button):
    """زر التشغيل السريع"""
    
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.success,
            label="▶️ تشغيل سريع للأغاني",
            emoji="▶️",
            row=1
        )
    
    async def callback(self, interaction: discord.Interaction):
        # التحقق من المستخدم
        view = self.view
        if interaction.user.id != view.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # التحقق ما إذا كان المستخدم في قناة صوتية
        if not interaction.user.voice:
            return await interaction.response.send_message(
                "يجب أن تكون في قناة صوتية أولاً!",
                ephemeral=True
            )
        
        # حذف رسالة القائمة
        await interaction.message.delete()
        
        # إنشاء مودال للرابط
        class URLModal(ui.Modal, title="تشغيل أغنية من رابط"):
            url_input = ui.TextInput(
                label="أدخل رابط أو اسم الأغنية",
                placeholder="https://www.youtube.com/... أو اسم الأغنية",
                style=discord.TextStyle.short,
                required=True,
                max_length=200
            )
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                # رسالة الانتظار
                wait_embed = discord.Embed(
                    title="🎵 جاري تشغيل الموسيقى...",
                    description=f"جاري تشغيل: `{self.url_input.value}`",
                    color=discord.Color.blue()
                )
                
                wait_embed.set_footer(text="يرجى الانتظار قليلاً...")
                await modal_interaction.response.send_message(embed=wait_embed)
                
                # محاولة الانضمام للقناة الصوتية أولاً إذا لم يكن البوت متصلاً
                voice_channel = interaction.user.voice.channel
                voice_cog = view.bot.get_cog('VoiceControl')
                if voice_cog:
                    voice_ctx = await view.bot.get_context(view.ctx.message)
                    voice_command = view.bot.get_command('صوت')
                    if voice_command and not (hasattr(view.ctx.guild, 'voice_client') and view.ctx.guild.voice_client):
                        try:
                            await voice_ctx.invoke(voice_command, channel_or_volume=str(voice_channel.id))
                        except Exception as e:
                            print(f"Error joining voice channel: {e}")
                
                # تنفيذ أمر التشغيل
                play_command = view.bot.get_command('تشغيل') or view.bot.get_command('play')
                if play_command:
                    ctx = await view.bot.get_context(view.ctx.message)
                    await ctx.invoke(play_command, query=self.url_input.value)
                    
                    # تأكيد التشغيل
                    success_embed = discord.Embed(
                        title="✅ تم التشغيل بنجاح",
                        description=f"تم تشغيل: `{self.url_input.value}`",
                        color=discord.Color.green()
                    )
                    success_embed.set_footer(text="استمتع بالموسيقى! استخدم !تخطي للانتقال للأغنية التالية")
                    
                    message = await modal_interaction.original_response()
                    try:
                        await message.edit(embed=success_embed)
                        # مسح الرسالة بعد 5 ثوانٍ
                        await asyncio.sleep(5)
                        await message.delete()
                    except:
                        pass
                else:
                    error_embed = discord.Embed(
                        title="❌ خطأ",
                        description="عذراً، أمر التشغيل غير متاح حالياً.",
                        color=discord.Color.red()
                    )
                    
                    message = await modal_interaction.original_response()
                    await message.edit(embed=error_embed)
        
        # عرض المودال
        await interaction.response.send_modal(URLModal())


class MusicMenuView(ui.View):
    """واجهة قائمة الموسيقى التفاعلية"""
    
    def __init__(self, bot, ctx, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
    
    @ui.button(label="▶️ تشغيل موسيقى", style=discord.ButtonStyle.success, emoji="▶️", row=0)
    async def play_music_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر تشغيل الموسيقى"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # التحقق ما إذا كان المستخدم في قناة صوتية
        if not interaction.user.voice:
            return await interaction.response.send_message(
                "يجب أن تكون في قناة صوتية أولاً!",
                ephemeral=True
            )
        
        # إنشاء مودال للتشغيل
        class AllInOnePlayModal(ui.Modal, title="تشغيل موسيقى"):
            url_input = ui.TextInput(
                label="أدخل رابط أو اسم الأغنية",
                placeholder="https://www.youtube.com/... أو اسم الأغنية",
                style=discord.TextStyle.short,
                required=True,
                max_length=200
            )
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                # رسالة الانتظار
                wait_embed = discord.Embed(
                    title="⏳ جاري التشغيل...",
                    description=f"جاري تشغيل: `{self.url_input.value}`",
                    color=discord.Color.blue()
                )
                
                wait_embed.set_footer(text="سيتم الانضمام تلقائيًا إلى القناة الصوتية الخاصة بك")
                
                await modal_interaction.response.send_message(embed=wait_embed)
                
                # محاولة الانضمام للقناة الصوتية أولاً إذا لم يكن البوت متصلاً
                voice_channel = interaction.user.voice.channel
                voice_cog = self.bot.get_cog('VoiceControl')
                if voice_cog:
                    voice_ctx = await self.bot.get_context(self.ctx.message)
                    voice_command = self.bot.get_command('صوت')
                    if voice_command and not (hasattr(self.ctx.guild, 'voice_client') and self.ctx.guild.voice_client):
                        try:
                            await voice_ctx.invoke(voice_command, channel_or_volume=str(voice_channel.id))
                        except Exception as e:
                            print(f"Error joining voice channel: {e}")
                
                # تنفيذ أمر التشغيل
                play_command = self.bot.get_command('تشغيل') or self.bot.get_command('play')
                if play_command:
                    play_ctx = await self.bot.get_context(self.ctx.message)
                    await play_ctx.invoke(play_command, query=self.url_input.value)
                    
                    # تأكيد التشغيل
                    success_embed = discord.Embed(
                        title="✅ تم التشغيل بنجاح",
                        description=f"تم تشغيل: `{self.url_input.value}`",
                        color=discord.Color.green()
                    )
                    success_embed.set_footer(text="استمتع بالموسيقى! استخدم !تخطي للانتقال للأغنية التالية")
                    
                    message = await modal_interaction.original_response()
                    try:
                        await message.edit(embed=success_embed)
                        # مسح الرسالة بعد 5 ثوانٍ
                        await asyncio.sleep(5)
                        await message.delete()
                    except:
                        pass
                else:
                    error_embed = discord.Embed(
                        title="❌ خطأ",
                        description="عذراً، أمر التشغيل غير متاح حالياً.",
                        color=discord.Color.red()
                    )
                    
                    message = await modal_interaction.original_response()
                    await message.edit(embed=error_embed)
        
        # تخزين معرفات المستخدم والبوت للاستخدام في المودال
        self_bot = self.bot
        self_ctx = self.ctx
        
        # عرض المودال
        await interaction.response.send_modal(AllInOnePlayModal())
    
    @ui.button(label="⏹️ إيقاف", style=discord.ButtonStyle.secondary)
    async def stop_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر إيقاف الموسيقى"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة
        await interaction.message.delete()
        
        # تنفيذ أمر الإيقاف
        stop_command = self.bot.get_command('إيقاف') or self.bot.get_command('stop')
        if stop_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(stop_command)
        else:
            await interaction.followup.send("عذراً، أمر الإيقاف غير متاح حالياً.")
    
    @ui.button(label="⏭️ تخطي", style=discord.ButtonStyle.secondary)
    async def skip_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر تخطي الأغنية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة
        await interaction.message.delete()
        
        # تنفيذ أمر التخطي
        skip_command = self.bot.get_command('تخطي') or self.bot.get_command('skip')
        if skip_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(skip_command)
        else:
            await interaction.followup.send("عذراً، أمر التخطي غير متاح حالياً.")
    
    @ui.button(label="🔍 بحث", style=discord.ButtonStyle.primary)
    async def search_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر البحث عن موسيقى"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.message.delete()
        
        # إعداد أمر البحث
        message = await interaction.followup.send("يرجى كتابة اسم الأغنية للبحث عنها:")
        
        # انتظار رد المستخدم
        try:
            response = await self.bot.wait_for(
                'message',
                check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id,
                timeout=30.0
            )
            
            # تنفيذ أمر البحث
            search_command = self.bot.get_command('بحث') or self.bot.get_command('search')
            if search_command:
                ctx = await self.bot.get_context(response)
                await ctx.invoke(search_command, query=response.content)
                
                # حذف رسالة الطلب
                try:
                    await message.delete()
                except:
                    pass
            else:
                await interaction.followup.send("عذراً، أمر البحث غير متاح حالياً.")
        except asyncio.TimeoutError:
            await message.edit(content="انتهت المهلة. يرجى المحاولة مرة أخرى.")
    
    @ui.button(label="🔙 رجوع", style=discord.ButtonStyle.danger)
    async def back_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر الرجوع للقائمة الرئيسية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # العودة إلى القائمة الرئيسية
        main_view = MainMenuView(self.bot, self.ctx)
        
        # تحديث الرسالة بالقائمة الرئيسية
        embed = discord.Embed(
            title="🤖 القائمة الرئيسية",
            description="اختر أحد الخيارات أدناه:",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=main_view)


class GamesMenuView(ui.View):
    """واجهة قائمة الألعاب التفاعلية"""
    
    def __init__(self, bot, ctx, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
    
    @ui.button(label="🎣 صيد", style=discord.ButtonStyle.primary, emoji="🎣", row=2)
    async def fishing_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة الصيد"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # تنفيذ أمر الصيد
        fishing_command = self.bot.get_command('صيد') or self.bot.get_command('fish')
        if fishing_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(fishing_command)
        else:
            await interaction.followup.send("عذراً، لعبة الصيد غير متاحة حالياً.", ephemeral=True)
    
    @ui.button(label="🏇 سباق الخيول", style=discord.ButtonStyle.primary, emoji="🏇", row=2)
    async def horserace_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة سباق الخيول"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # تنفيذ أمر سباق الخيول
        horserace_command = self.bot.get_command('سباق') or self.bot.get_command('horserace')
        if horserace_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(horserace_command)
        else:
            await interaction.followup.send("عذراً، لعبة سباق الخيول غير متاحة حالياً.", ephemeral=True)
    
    @ui.button(label="🎲 النرد", style=discord.ButtonStyle.primary, emoji="🎲", row=2)
    async def dice_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة النرد"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # تنفيذ أمر النرد
        dice_command = self.bot.get_command('نرد') or self.bot.get_command('dice')
        if dice_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(dice_command)
        else:
            await interaction.followup.send("عذراً، لعبة النرد غير متاحة حالياً.", ephemeral=True)
    
    @ui.button(label="💵 الرصيد", style=discord.ButtonStyle.primary, emoji="💵")
    async def balance_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر عرض الرصيد"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة
        await interaction.message.delete()
        
        # إنشاء رسالة توضيحية
        embed = discord.Embed(
            title="💵 عرض الرصيد",
            description="جاري عرض رصيدك...",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="💡 تلميح",
            value="يمكنك استخدام الأمر `!رصيد` أو `!balance` مباشرة في المرات القادمة!",
            inline=False
        )
        
        start_message = await interaction.followup.send(embed=embed, ephemeral=True)
        
        # تنفيذ أمر الرصيد
        balance_command = self.bot.get_command('رصيد') or self.bot.get_command('balance')
        if balance_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(balance_command)
            
            # حذف رسالة البدء بعد فترة
            try:
                await asyncio.sleep(3)
                await start_message.delete()
            except:
                pass
        else:
            await interaction.followup.send("عذراً، أمر الرصيد غير متاح حالياً.", ephemeral=True)
    
    @ui.button(label="🎁 المكافأة اليومية", style=discord.ButtonStyle.primary, emoji="🎁")
    async def daily_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر المكافأة اليومية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة
        await interaction.message.delete()
        
        # إنشاء رسالة توضيحية
        embed = discord.Embed(
            title="🎁 المكافأة اليومية",
            description="جاري استلام المكافأة اليومية...",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="💡 تلميح",
            value="يمكنك استخدام الأمر `!يومي` أو `!daily` مباشرة في المرات القادمة!",
            inline=False
        )
        
        start_message = await interaction.followup.send(embed=embed, ephemeral=True)
        
        # تنفيذ أمر المكافأة اليومية
        daily_command = self.bot.get_command('يومي') or self.bot.get_command('daily')
        if daily_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(daily_command)
            
            # حذف رسالة البدء بعد فترة
            try:
                await asyncio.sleep(3)
                await start_message.delete()
            except:
                pass
        else:
            await interaction.followup.send("عذراً، أمر المكافأة اليومية غير متاح حالياً.", ephemeral=True)
    
    @ui.button(label="🛡️ حماية", style=discord.ButtonStyle.success, emoji="🛡️")
    async def protection_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر الحماية من السرقة"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة
        await interaction.message.delete()
        
        # إنشاء رسالة توضيحية
        embed = discord.Embed(
            title="🛡️ نظام الحماية",
            description="جاري فتح خيارات الحماية...",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="💡 تلميح",
            value="يمكنك استخدام الأمر `!حماية` أو `!protection` مباشرة في المرات القادمة!",
            inline=False
        )
        
        start_message = await interaction.followup.send(embed=embed, ephemeral=True)
        
        # تنفيذ أمر الحماية
        protection_command = self.bot.get_command('حماية') or self.bot.get_command('protection')
        if protection_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(protection_command)
            
            # حذف رسالة البدء بعد فترة
            try:
                await asyncio.sleep(3)
                await start_message.delete()
            except:
                pass
        else:
            await interaction.followup.send("عذراً، أمر الحماية غير متاح حالياً.", ephemeral=True)
    
    @ui.button(label="🕵️ سرقة", style=discord.ButtonStyle.danger, emoji="🕵️")
    async def steal_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر السرقة"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إنشاء مودال للسرقة
        class StealModal(ui.Modal, title="سرقة مستخدم"):
            target_input = ui.TextInput(
                label="أدخل اسم أو معرف المستخدم",
                placeholder="@username أو الاسم أو المعرف",
                style=discord.TextStyle.short,
                required=True,
                max_length=100
            )
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                # رسالة الانتظار
                wait_embed = discord.Embed(
                    title="🕵️ جاري محاولة السرقة...",
                    description=f"محاولة سرقة: `{self.target_input.value}`",
                    color=discord.Color.gold()
                )
                
                await modal_interaction.response.send_message(embed=wait_embed)
                
                # تنفيذ أمر السرقة
                steal_command = self.bot.get_command('سرقة') or self.bot.get_command('steal')
                if steal_command:
                    steal_ctx = await self.bot.get_context(self.ctx.message)
                    try:
                        await steal_ctx.invoke(steal_command, target=self.target_input.value)
                        
                        # حذف رسالة الانتظار بعد إتمام الأمر
                        message = await modal_interaction.original_response()
                        try:
                            await asyncio.sleep(3)
                            await message.delete()
                        except:
                            pass
                    except Exception as e:
                        error_embed = discord.Embed(
                            title="❌ خطأ في السرقة",
                            description=f"حدث خطأ أثناء محاولة السرقة: `{str(e)}`",
                            color=discord.Color.red()
                        )
                        
                        message = await modal_interaction.original_response()
                        await message.edit(embed=error_embed)
                else:
                    error_embed = discord.Embed(
                        title="❌ خطأ",
                        description="عذراً، أمر السرقة غير متاح حالياً.",
                        color=discord.Color.red()
                    )
                    
                    message = await modal_interaction.original_response()
                    await message.edit(embed=error_embed)
        
        # عرض المودال
        await interaction.response.send_modal(StealModal())
    
    @ui.button(label="💸 تحويل", style=discord.ButtonStyle.success, emoji="💸", row=3)
    async def transfer_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر التحويل"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إنشاء مودال للتحويل
        class TransferModal(ui.Modal, title="تحويل أموال"):
            recipient_input = ui.TextInput(
                label="المستلم",
                placeholder="@username أو الاسم أو المعرف",
                style=discord.TextStyle.short,
                required=True,
                max_length=100
            )
            
            amount_input = ui.TextInput(
                label="المبلغ",
                placeholder="أدخل مبلغ التحويل (أرقام فقط)",
                style=discord.TextStyle.short,
                required=True,
                max_length=10
            )
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                # رسالة الانتظار
                wait_embed = discord.Embed(
                    title="💸 جاري التحويل...",
                    description=f"محاولة تحويل `{self.amount_input.value}` إلى `{self.recipient_input.value}`",
                    color=discord.Color.gold()
                )
                
                await modal_interaction.response.send_message(embed=wait_embed)
                
                # تنفيذ أمر التحويل
                transfer_command = self.bot.get_command('تحويل') or self.bot.get_command('transfer')
                if transfer_command:
                    transfer_ctx = await self.bot.get_context(self.ctx.message)
                    try:
                        await transfer_ctx.invoke(transfer_command, recipient=self.recipient_input.value, amount=self.amount_input.value)
                        
                        # حذف رسالة الانتظار بعد إتمام الأمر
                        message = await modal_interaction.original_response()
                        try:
                            await asyncio.sleep(5)
                            await message.delete()
                        except:
                            pass
                    except Exception as e:
                        error_embed = discord.Embed(
                            title="❌ خطأ في التحويل",
                            description=f"حدث خطأ أثناء محاولة التحويل: `{str(e)}`",
                            color=discord.Color.red()
                        )
                        
                        message = await modal_interaction.original_response()
                        await message.edit(embed=error_embed)
                else:
                    error_embed = discord.Embed(
                        title="❌ خطأ",
                        description="عذراً، أمر التحويل غير متاح حالياً.",
                        color=discord.Color.red()
                    )
                    
                    message = await modal_interaction.original_response()
                    await message.edit(embed=error_embed)
        
        # عرض المودال
        await interaction.response.send_modal(TransferModal())
    
    @ui.button(label="🔙 رجوع", style=discord.ButtonStyle.secondary, emoji="🔙", row=2)
    async def back_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر الرجوع للقائمة الرئيسية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # العودة إلى القائمة الرئيسية
        main_view = MainMenuView(self.bot, self.ctx)
        
        # تحديث الرسالة بالقائمة الرئيسية
        embed = discord.Embed(
            title="🤖 القائمة الرئيسية",
            description="اختر أحد الخيارات أدناه:",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=main_view)


# إضافة واجهة الألعاب السريعة
class QuickGamesView(ui.View):
    """واجهة الألعاب السريعة"""
    
    def __init__(self, bot, ctx, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
    
    @ui.button(label="🎣 صيد", style=discord.ButtonStyle.primary, emoji="🎣", row=0)
    async def fishing_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة لصيد"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # تنفيذ أمر الصيد
        fishing_command = self.bot.get_command('صيد') or self.bot.get_command('fish')
        if fishing_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(fishing_command)
        else:
            await interaction.followup.send("عذراً، لعبة الصيد غير متاحة حالياً.", ephemeral=True)
    
    @ui.button(label="🎲 النرد", style=discord.ButtonStyle.primary, emoji="🎲", row=0)
    async def dice_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة النرد"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # تنفيذ أمر النرد
        dice_command = self.bot.get_command('نرد') or self.bot.get_command('dice')
        if dice_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(dice_command)
        else:
            await interaction.followup.send("عذراً، لعبة النرد غير متاحة حالياً.", ephemeral=True)
    
    @ui.button(label="🏇 سباق الخيول", style=discord.ButtonStyle.primary, emoji="🏇", row=0)
    async def horserace_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة سباق الخيول"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # تنفيذ أمر سباق الخيول
        horserace_command = self.bot.get_command('سباق') or self.bot.get_command('horserace')
        if horserace_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(horserace_command)
        else:
            await interaction.followup.send("عذراً، لعبة سباق الخيول غير متاحة حالياً.", ephemeral=True)
    
    @ui.button(label="🃏 بلاك جاك", style=discord.ButtonStyle.primary, emoji="🃏", row=0)
    async def blackjack_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة بلاك جاك"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # تنفيذ أمر بلاك جاك
        blackjack_command = self.bot.get_command('بلاك_جاك') or self.bot.get_command('blackjack')
        if blackjack_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(blackjack_command)
        else:
            await interaction.followup.send("عذراً، لعبة بلاك جاك غير متاحة حالياً.", ephemeral=True)
    
    @ui.button(label="🔙 رجوع", style=discord.ButtonStyle.danger, emoji="🔙", row=1)
    async def back_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر الرجوع للاختصارات السريعة"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # العودة إلى قائمة الاختصارات السريعة
        shortcuts_view = QuickShortcutsView(self.bot, self.ctx)
        
        # تحديث الرسالة
        embed = discord.Embed(
            title="⚡ الاختصارات السريعة",
            description="جميع الأوامر الشائعة في مكان واحد! اختر الأمر الذي تريده:",
            color=discord.Color.purple()
        )
        
        # إضافة توضيح
        embed.add_field(
            name="🔰 معلومات",
            value="هذه القائمة تجمع الأوامر الأكثر استخداماً في مكان واحد للوصول السريع",
            inline=False
        )
        
        # إضافة صورة البوت
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        await interaction.response.edit_message(embed=embed, view=shortcuts_view)


class ComprehensiveMenuView(ui.View):
    """واجهة شاملة تعرض جميع الأوامر مباشرة عند استدعاء الأمر !مساعدة"""
    
    def __init__(self, bot, ctx, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
    
    @ui.button(label="🎵 تشغيل موسيقى", style=discord.ButtonStyle.success, emoji="🎵", row=0)
    async def music_play_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر تشغيل الموسيقى"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # التحقق ما إذا كان المستخدم في قناة صوتية
        if not interaction.user.voice:
            return await interaction.response.send_message(
                "يجب أن تكون في قناة صوتية أولاً!",
                ephemeral=True
            )
            
        # إنشاء مودال للتشغيل
        class PlayModal(ui.Modal, title="تشغيل موسيقى"):
            url_input = ui.TextInput(
                label="أدخل رابط أو اسم الأغنية",
                placeholder="https://www.youtube.com/... أو اسم الأغنية",
                style=discord.TextStyle.short,
                required=True,
                max_length=200
            )
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                # محاولة الانضمام للقناة الصوتية أولاً إذا لم يكن البوت متصلاً
                voice_channel = interaction.user.voice.channel
                voice_cog = self.bot.get_cog('VoiceControl')
                if voice_cog:
                    voice_ctx = await self.bot.get_context(self.ctx.message)
                    voice_command = self.bot.get_command('صوت')
                    if voice_command and not (hasattr(self.ctx.guild, 'voice_client') and self.ctx.guild.voice_client):
                        try:
                            await voice_ctx.invoke(voice_command, channel_or_volume=str(voice_channel.id))
                        except Exception as e:
                            print(f"Error joining voice channel: {e}")
                
                # رسالة الانتظار
                wait_embed = discord.Embed(
                    title="⏳ جاري التشغيل...",
                    description=f"جاري تشغيل: `{self.url_input.value}`",
                    color=discord.Color.blue()
                )
                
                await modal_interaction.response.send_message(embed=wait_embed)
                
                # تنفيذ أمر التشغيل
                play_command = self.bot.get_command('تشغيل') or self.bot.get_command('play')
                if play_command:
                    play_ctx = await self.bot.get_context(self.ctx.message)
                    await play_ctx.invoke(play_command, query=self.url_input.value)
                    
                    # تأكيد التشغيل
                    success_embed = discord.Embed(
                        title="✅ تم التشغيل بنجاح",
                        description=f"تم تشغيل: `{self.url_input.value}`",
                        color=discord.Color.green()
                    )
                    
                    message = await modal_interaction.original_response()
                    try:
                        await message.edit(embed=success_embed)
                        await asyncio.sleep(5)
                        await message.delete()
                    except:
                        pass
                else:
                    await modal_interaction.response.send_message("عذراً، أمر التشغيل غير متاح حالياً.", ephemeral=True)
                
        await interaction.response.send_modal(PlayModal())
    
    @ui.button(label="🔍 بحث", style=discord.ButtonStyle.primary, emoji="🔍", row=0)
    async def music_search_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر البحث عن موسيقى"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # التحقق ما إذا كان المستخدم في قناة صوتية
        if not interaction.user.voice:
            return await interaction.response.send_message(
                "يجب أن تكون في قناة صوتية أولاً!",
                ephemeral=True
            )
        
        # إنشاء مودال للبحث
        class SearchModal(ui.Modal, title="البحث عن أغنية"):
            search_query = ui.TextInput(
                label="أدخل كلمات البحث",
                placeholder="مثال: despacito أو اسم الفنان",
                style=discord.TextStyle.short,
                required=True,
                max_length=200
            )
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                # تنفيذ أمر البحث
                search_command = self.bot.get_command('بحث') or self.bot.get_command('search')
                if search_command:
                    ctx = await self.bot.get_context(self.ctx.message)
                    
                    # رسالة انتظار
                    loading_msg = await modal_interaction.response.send_message("🔍 جاري البحث في YouTube...")
                    
                    try:
                        await ctx.invoke(search_command, query=self.search_query.value)
                        
                        # حذف رسالة الانتظار بعد إتمام البحث
                        try:
                            message = await modal_interaction.original_response()
                            await message.delete()
                        except:
                            pass
                    except Exception as e:
                        # عرض رسالة الخطأ
                        error_embed = discord.Embed(
                            title="❌ خطأ في البحث",
                            description=f"حدث خطأ أثناء البحث: `{str(e)}`",
                            color=discord.Color.red()
                        )
                        
                        message = await modal_interaction.original_response()
                        await message.edit(content="", embed=error_embed)
                else:
                    # عرض رسالة بعدم توفر أمر البحث
                    await modal_interaction.response.send_message("عذراً، أمر البحث غير متاح حالياً.", ephemeral=True)
        
        # عرض المودال
        await interaction.response.send_modal(SearchModal())
    
    @ui.button(label="⏹️ إيقاف الموسيقى", style=discord.ButtonStyle.secondary, emoji="⏹️", row=0)
    async def music_stop_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر إيقاف الموسيقى"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # تنفيذ أمر الإيقاف
        stop_command = self.bot.get_command('إيقاف') or self.bot.get_command('stop')
        if stop_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(stop_command)
            await interaction.response.send_message("تم إيقاف الموسيقى!", ephemeral=True)
        else:
            await interaction.response.send_message("عذراً، أمر الإيقاف غير متاح حالياً.", ephemeral=True)
    
    @ui.button(label="⏭️ تخطي الأغنية", style=discord.ButtonStyle.secondary, emoji="⏭️", row=0)
    async def music_skip_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر تخطي الأغنية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # تنفيذ أمر التخطي
        skip_command = self.bot.get_command('تخطي') or self.bot.get_command('skip')
        if skip_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(skip_command)
            await interaction.response.send_message("تم تخطي الأغنية الحالية!", ephemeral=True)
        else:
            await interaction.response.send_message("عذراً، أمر التخطي غير متاح حالياً.", ephemeral=True)
    
    @ui.button(label="🎮 لعبة الصيد", style=discord.ButtonStyle.primary, emoji="🎣", row=1)
    async def fishing_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة الصيد"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # تنفيذ أمر الصيد
        fishing_command = self.bot.get_command('صيد') or self.bot.get_command('fish')
        if fishing_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(fishing_command)
        else:
            await interaction.followup.send("عذراً، لعبة الصيد غير متاحة حالياً.", ephemeral=True)
            
    @ui.button(label="🎲 لعبة النرد", style=discord.ButtonStyle.primary, emoji="🎲", row=1)
    async def dice_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة النرد"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # تنفيذ أمر النرد
        dice_command = self.bot.get_command('نرد') or self.bot.get_command('dice')
        if dice_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(dice_command)
        else:
            await interaction.followup.send("عذراً، لعبة النرد غير متاحة حالياً.", ephemeral=True)
    
    @ui.button(label="🏇 سباق الخيول", style=discord.ButtonStyle.primary, emoji="🏇", row=1)
    async def horserace_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة سباق الخيول"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # تنفيذ أمر سباق الخيول
        horserace_command = self.bot.get_command('سباق') or self.bot.get_command('horserace')
        if horserace_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(horserace_command)
        else:
            await interaction.followup.send("عذراً، لعبة سباق الخيول غير متاحة حالياً.", ephemeral=True)
    
    @ui.button(label="🃏 بلاك جاك", style=discord.ButtonStyle.primary, emoji="🃏", row=1)
    async def blackjack_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة بلاك جاك"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # تنفيذ أمر بلاك جاك
        blackjack_command = self.bot.get_command('بلاك_جاك') or self.bot.get_command('blackjack')
        if blackjack_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(blackjack_command)
        else:
            await interaction.followup.send("عذراً، لعبة بلاك جاك غير متاحة حالياً.", ephemeral=True)
    
    @ui.button(label="💵 عرض الرصيد", style=discord.ButtonStyle.success, emoji="💵", row=2)
    async def balance_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر عرض الرصيد"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # تنفيذ أمر الرصيد
        balance_command = self.bot.get_command('رصيد') or self.bot.get_command('balance')
        if balance_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(balance_command)
        else:
            await interaction.followup.send("عذراً، أمر الرصيد غير متاح حالياً.", ephemeral=True)
            
    @ui.button(label="🎁 المكافأة اليومية", style=discord.ButtonStyle.success, emoji="🎁", row=2)
    async def daily_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر المكافأة اليومية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # تنفيذ أمر المكافأة اليومية
        daily_command = self.bot.get_command('يومي') or self.bot.get_command('daily')
        if daily_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(daily_command)
        else:
            await interaction.followup.send("عذراً، أمر المكافأة اليومية غير متاح حالياً.", ephemeral=True)
            
    @ui.button(label="🕵️ سرقة", style=discord.ButtonStyle.danger, emoji="🕵️", row=2)
    async def steal_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر السرقة"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إنشاء مودال للسرقة
        class StealModal(ui.Modal, title="سرقة مستخدم"):
            target_input = ui.TextInput(
                label="أدخل اسم أو معرف المستخدم",
                placeholder="@username أو الاسم أو المعرف",
                style=discord.TextStyle.short,
                required=True,
                max_length=100
            )
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                # رسالة الانتظار
                wait_embed = discord.Embed(
                    title="🕵️ جاري محاولة السرقة...",
                    description=f"محاولة سرقة: `{self.target_input.value}`",
                    color=discord.Color.gold()
                )
                
                await modal_interaction.response.send_message(embed=wait_embed)
                
                # تنفيذ أمر السرقة
                steal_command = self.bot.get_command('سرقة') or self.bot.get_command('steal')
                if steal_command:
                    steal_ctx = await self.bot.get_context(self.ctx.message)
                    try:
                        await steal_ctx.invoke(steal_command, target=self.target_input.value)
                        
                        message = await modal_interaction.original_response()
                        try:
                            await asyncio.sleep(3)
                            await message.delete()
                        except:
                            pass
                    except Exception as e:
                        message = await modal_interaction.original_response()
                        error_embed = discord.Embed(
                            title="❌ خطأ في السرقة",
                            description=f"حدث خطأ أثناء محاولة السرقة: `{str(e)}`",
                            color=discord.Color.red()
                        )
                        await message.edit(embed=error_embed)
                else:
                    message = await modal_interaction.original_response()
                    error_embed = discord.Embed(
                        title="❌ خطأ",
                        description="عذراً، أمر السرقة غير متاح حالياً.",
                        color=discord.Color.red()
                    )
                    await message.edit(embed=error_embed)
        
        # عرض المودال
        await interaction.response.send_modal(StealModal())
    
    @ui.button(label="💸 تحويل", style=discord.ButtonStyle.success, emoji="💸", row=3)
    async def transfer_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر التحويل"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إنشاء مودال للتحويل
        class TransferModal(ui.Modal, title="تحويل أموال"):
            recipient_input = ui.TextInput(
                label="المستلم",
                placeholder="@username أو الاسم أو المعرف",
                style=discord.TextStyle.short,
                required=True,
                max_length=100
            )
            
            amount_input = ui.TextInput(
                label="المبلغ",
                placeholder="أدخل مبلغ التحويل (أرقام فقط)",
                style=discord.TextStyle.short,
                required=True,
                max_length=10
            )
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                # رسالة الانتظار
                wait_embed = discord.Embed(
                    title="💸 جاري التحويل...",
                    description=f"محاولة تحويل `{self.amount_input.value}` إلى `{self.recipient_input.value}`",
                    color=discord.Color.gold()
                )
                
                await modal_interaction.response.send_message(embed=wait_embed)
                
                # تنفيذ أمر التحويل
                transfer_command = self.bot.get_command('تحويل') or self.bot.get_command('transfer')
                if transfer_command:
                    transfer_ctx = await self.bot.get_context(self.ctx.message)
                    try:
                        await transfer_ctx.invoke(transfer_command, recipient=self.recipient_input.value, amount=self.amount_input.value)
                        
                        # حذف رسالة الانتظار بعد إتمام الأمر
                        message = await modal_interaction.original_response()
                        try:
                            await asyncio.sleep(5)
                            await message.delete()
                        except:
                            pass
                    except Exception as e:
                        error_embed = discord.Embed(
                            title="❌ خطأ في التحويل",
                            description=f"حدث خطأ أثناء محاولة التحويل: `{str(e)}`",
                            color=discord.Color.red()
                        )
                        
                        message = await modal_interaction.original_response()
                        await message.edit(embed=error_embed)
                else:
                    error_embed = discord.Embed(
                        title="❌ خطأ",
                        description="عذراً، أمر التحويل غير متاح حالياً.",
                        color=discord.Color.red()
                    )
                    
                    message = await modal_interaction.original_response()
                    await message.edit(embed=error_embed)
        
        # عرض المودال
        await interaction.response.send_modal(TransferModal())
    
    @ui.button(label="🔊 دخول الروم الصوتي", style=discord.ButtonStyle.success, emoji="🔊", row=3)
    async def join_voice_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر الانضمام إلى الروم الصوتي للمستخدم"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # التحقق ما إذا كان المستخدم في قناة صوتية
        if not interaction.user.voice:
            return await interaction.response.send_message(
                "أنت غير متواجد في أي روم صوتي! يرجى الانضمام إلى روم صوتي أولاً.",
                ephemeral=True
            )
        
        voice_channel = interaction.user.voice.channel
        
        # إنشاء رسالة توضيحية
        embed = discord.Embed(
            title="🔊 دخول الروم الصوتي",
            description=f"جاري الانضمام إلى الروم الصوتي: **{voice_channel.name}**",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # محاولة الانضمام للقناة الصوتية
        voice_cog = self.bot.get_cog('VoiceControl')
        if voice_cog:
            voice_ctx = await self.bot.get_context(self.ctx.message)
            voice_command = self.bot.get_command('صوت') or self.bot.get_command('voice')
            if voice_command:
                try:
                    await voice_ctx.invoke(voice_command, channel_or_volume=str(voice_channel.id))
                    
                    # رسالة نجاح الانضمام
                    success_embed = discord.Embed(
                        title="✅ تم الانضمام بنجاح",
                        description=f"تم الانضمام إلى الروم الصوتي: **{voice_channel.name}**\n"
                                    f"يمكنك الآن استخدام أوامر الموسيقى مباشرة!",
                        color=discord.Color.green()
                    )
                    
                    await interaction.followup.send(embed=success_embed, ephemeral=True)
                except Exception as e:
                    error_embed = discord.Embed(
                        title="❌ خطأ في الانضمام",
                        description=f"حدث خطأ أثناء محاولة الانضمام إلى الروم الصوتي:\n`{str(e)}`",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=error_embed, ephemeral=True)
            else:
                await interaction.followup.send("عذراً، أمر الانضمام للروم الصوتي غير متاح حالياً.", ephemeral=True)
        else:
            await interaction.followup.send("عذراً، وحدة التحكم الصوتي غير متاحة حالياً.", ephemeral=True)
    
    @ui.button(label="🔗 انضمام لرابط", style=discord.ButtonStyle.primary, emoji="🔗", row=3)
    async def join_link_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر الانضمام لرابط دعوة"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
            
        # إنشاء مودال للرابط
        class InviteModal(ui.Modal, title="انضمام لرابط دعوة"):
            url_input = ui.TextInput(
                label="أدخل رابط الدعوة",
                placeholder="https://discord.gg/...",
                style=discord.TextStyle.short,
                required=True,
                max_length=200
            )
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                # رسالة الانتظار
                wait_embed = discord.Embed(
                    title="🔗 جاري الانضمام...",
                    description=f"جاري محاولة الانضمام إلى الرابط: `{self.url_input.value}`",
                    color=discord.Color.blue()
                )
                
                await modal_interaction.response.send_message(embed=wait_embed)
                
                # تنفيذ أمر الدعوة
                invite_command = self.bot.get_command('دعوة') or self.bot.get_command('invite')
                if invite_command:
                    invite_ctx = await self.bot.get_context(self.ctx.message)
                    try:
                        await invite_ctx.invoke(invite_command, invite_link=self.url_input.value)
                        
                        # تأكيد الانضمام
                        success_embed = discord.Embed(
                            title="✅ تم الانضمام بنجاح",
                            description=f"تم الانضمام إلى: `{self.url_input.value}`",
                            color=discord.Color.green()
                        )
                        
                        message = await modal_interaction.original_response()
                        try:
                            await message.edit(embed=success_embed)
                            await asyncio.sleep(5)
                            await message.delete()
                        except:
                            pass
                    except Exception as e:
                        message = await modal_interaction.original_response()
                        error_embed = discord.Embed(
                            title="❌ خطأ في الانضمام",
                            description=f"حدث خطأ أثناء محاولة الانضمام: `{str(e)}`",
                            color=discord.Color.red()
                        )
                        await message.edit(embed=error_embed)
                else:
                    message = await modal_interaction.original_response()
                    error_embed = discord.Embed(
                        title="❌ خطأ",
                        description="عذراً، أمر الانضمام غير متاح حالياً.",
                        color=discord.Color.red()
                    )
                    await message.edit(embed=error_embed)
        
        # عرض المودال
        await interaction.response.send_modal(InviteModal())
            
    @ui.button(label="❌ إغلاق", style=discord.ButtonStyle.danger, emoji="❌", row=3)
    async def close_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر إغلاق القائمة"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # حذف الرسالة
        await interaction.message.delete()

    async def on_timeout(self):
        """عند انتهاء مهلة القائمة"""
        # تعطيل جميع الأزرار
        for item in self.children:
            item.disabled = True
        
        # تحديث الرسالة
        try:
            await self.message.edit(view=self)
        except:
            pass


class Menu(commands.Cog):
    """أوامر القوائم التفاعلية"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name="h",
        aliases=["menu", "قائمة", "مساعدة"],
        description="عرض قائمة تفاعلية للأوامر"
    )
    async def menu(self, ctx):
        """
        عرض قائمة تفاعلية للأوامر
        
        استخدم هذا الأمر لعرض واجهة تفاعلية سهلة الاستخدام للوصول إلى جميع أوامر البوت.
        """
        # تحديد اللغة المستخدمة
        language = get_user_language(self.bot, ctx.author.id)
        
        # إنشاء رسالة مضمنة للقائمة الشاملة كل الأوامر
        embed = discord.Embed(
            title="🤖 أوامر البوت التفاعلية" if language == "ar" else "🤖 Interactive Bot Commands",
            description="اختر مباشرة أحد الأزرار أدناه للوصول إلى الأوامر:" if language == "ar" else "Choose one of the buttons below for direct access to commands:",
            color=discord.Color.blue()
        )
        
        # إضافة صورة البوت
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        # إنشاء كائن القائمة الشاملة المحسنة
        view = ComprehensiveMenuView(self.bot, ctx)
        
        # إرسال الرسالة مع القائمة
        message = await ctx.send(embed=embed, view=view)
        
        # حفظ الرسالة في كائن القائمة لاستخدامها لاحقًا
        view.message = message