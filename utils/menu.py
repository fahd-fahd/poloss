#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
from discord.ui import Button, View
import sys
import os
from pathlib import Path

# إضافة مسار البوت إلى مسار البحث
sys.path.append(str(Path(__file__).parent.parent))

# استيراد وحدة الترجمة
try:
    from utils.translator import get_user_language, t
except ImportError:
    # دالة مؤقتة في حالة عدم وجود وحدة الترجمة
    def get_user_language(bot, user_id):
        return "ar"
    
    def t(key, language="ar"):
        return key

class MenuButton(Button):
    """زر قائمة مخصص مع ترجمة تلقائية"""
    
    def __init__(self, label_key, emoji=None, style=discord.ButtonStyle.primary, custom_id=None, language="ar", action=None, **kwargs):
        """
        إنشاء زر قائمة جديد
        
        Args:
            label_key: مفتاح الترجمة للنص
            emoji: الرمز التعبيري للزر
            style: نمط الزر
            custom_id: معرف مخصص للزر
            language: لغة العرض
            action: وظيفة يتم تنفيذها عند النقر
        """
        # ترجمة النص حسب اللغة المحددة
        if language == "ar":
            label = label_key
        else:
            # قاموس بسيط للترجمة
            translations = {
                "الرئيسية": "Home",
                "ألعاب": "Games",
                "اقتصاد": "Economy",
                "موسيقى": "Music",
                "إعدادات": "Settings",
                "رجوع": "Back",
                "الألعاب": "Games",
                "سباق الخيل": "Horse Race",
                "الموسيقى": "Music",
                "تشغيل": "Play",
                "إيقاف": "Stop",
                "تخطي": "Skip",
                "اللغة": "Language",
                "المساعدة": "Help",
            }
            label = translations.get(label_key, label_key)
        
        super().__init__(label=label, emoji=emoji, style=style, custom_id=custom_id, **kwargs)
        self.action = action
        self.language = language
        
    async def callback(self, interaction):
        """معالجة النقر على الزر"""
        if self.action:
            await self.action(interaction)

class NavigationView(View):
    """منظر التنقل بالأزرار مع دعم الرجوع"""
    
    def __init__(self, bot, ctx, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
        self.language = get_user_language(bot, ctx.author.id)
        self.current_menu = None
        self.history = []  # تاريخ التنقل
        self.message = None
        
    async def show_menu(self, menu_type, interaction=None):
        """عرض قائمة محددة"""
        # حفظ القائمة الحالية في التاريخ إذا كانت مختلفة
        if self.current_menu and self.current_menu != menu_type:
            self.history.append(self.current_menu)
        
        self.current_menu = menu_type
        
        # إزالة جميع الأزرار الحالية
        self.clear_items()
        
        # إضافة الأزرار الجديدة حسب نوع القائمة
        if menu_type == "main":
            await self._create_main_menu()
        elif menu_type == "games":
            await self._create_games_menu()
        elif menu_type == "music":
            await self._create_music_menu()
        elif menu_type == "economy":
            await self._create_economy_menu()
        elif menu_type == "settings":
            await self._create_settings_menu()
        
        # إضافة زر الرجوع إذا كان هناك قوائم سابقة
        if self.history:
            back_button = MenuButton(
                "رجوع", 
                emoji="↩️", 
                style=discord.ButtonStyle.secondary, 
                language=self.language,
                action=self._go_back
            )
            self.add_item(back_button)
        
        # إنشاء رسالة مضمنة للقائمة
        embed = await self._create_menu_embed(menu_type)
        
        # عرض القائمة أو تحديثها
        if interaction:
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            if self.message:
                await self.message.edit(embed=embed, view=self)
            else:
                self.message = await self.ctx.send(embed=embed, view=self)
    
    async def _go_back(self, interaction):
        """الرجوع إلى القائمة السابقة"""
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        if self.history:
            previous_menu = self.history.pop()
            await self.show_menu(previous_menu, interaction)
    
    async def _create_main_menu(self):
        """إنشاء القائمة الرئيسية"""
        # زر الألعاب
        games_button = MenuButton(
            "ألعاب", 
            emoji="🎮", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=lambda i: self.show_menu("games", i)
        )
        self.add_item(games_button)
        
        # زر الاقتصاد
        economy_button = MenuButton(
            "اقتصاد", 
            emoji="💰", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=lambda i: self.show_menu("economy", i)
        )
        self.add_item(economy_button)
        
        # زر الموسيقى
        music_button = MenuButton(
            "موسيقى", 
            emoji="🎵", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=lambda i: self.show_menu("music", i)
        )
        self.add_item(music_button)
        
        # زر الإعدادات
        settings_button = MenuButton(
            "إعدادات", 
            emoji="⚙️", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=lambda i: self.show_menu("settings", i)
        )
        self.add_item(settings_button)
        
        # زر المساعدة
        help_button = MenuButton(
            "المساعدة", 
            emoji="❓", 
            style=discord.ButtonStyle.secondary, 
            language=self.language,
            action=self._show_help
        )
        self.add_item(help_button)
    
    async def _create_games_menu(self):
        """إنشاء قائمة الألعاب"""
        # زر سباق الخيل
        horse_race_button = MenuButton(
            "سباق الخيل", 
            emoji="🐎", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=self._start_horse_race
        )
        self.add_item(horse_race_button)
        
        # يمكن إضافة المزيد من أزرار الألعاب هنا
    
    async def _create_music_menu(self):
        """إنشاء قائمة الموسيقى"""
        # زر تشغيل
        play_button = MenuButton(
            "تشغيل", 
            emoji="▶️", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=self._play_music
        )
        self.add_item(play_button)
        
        # زر إيقاف
        stop_button = MenuButton(
            "إيقاف", 
            emoji="⏹️", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=self._stop_music
        )
        self.add_item(stop_button)
        
        # زر تخطي
        skip_button = MenuButton(
            "تخطي", 
            emoji="⏭️", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=self._skip_music
        )
        self.add_item(skip_button)
    
    async def _create_economy_menu(self):
        """إنشاء قائمة الاقتصاد"""
        # أزرار الاقتصاد (ستضاف لاحقاً)
        pass
    
    async def _create_settings_menu(self):
        """إنشاء قائمة الإعدادات"""
        # زر اللغة
        language_button = MenuButton(
            "اللغة", 
            emoji="🌐", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=self._language_settings
        )
        self.add_item(language_button)
    
    async def _create_menu_embed(self, menu_type):
        """إنشاء رسالة مضمنة للقائمة"""
        if self.language == "ar":
            titles = {
                "main": "📋 القائمة الرئيسية",
                "games": "🎮 قائمة الألعاب",
                "music": "🎵 قائمة الموسيقى",
                "economy": "💰 قائمة الاقتصاد",
                "settings": "⚙️ الإعدادات"
            }
            
            descriptions = {
                "main": "اختر من القائمة الرئيسية:",
                "games": "اختر لعبة للعب:",
                "music": "اختر وظيفة موسيقية:",
                "economy": "اختر وظيفة اقتصادية:",
                "settings": "اختر إعداد لتغييره:"
            }
        else:
            titles = {
                "main": "📋 Main Menu",
                "games": "🎮 Games Menu",
                "music": "🎵 Music Menu",
                "economy": "💰 Economy Menu",
                "settings": "⚙️ Settings"
            }
            
            descriptions = {
                "main": "Choose from the main menu:",
                "games": "Choose a game to play:",
                "music": "Choose a music function:",
                "economy": "Choose an economy function:",
                "settings": "Choose a setting to change:"
            }
        
        embed = discord.Embed(
            title=titles.get(menu_type, "Menu"),
            description=descriptions.get(menu_type, "Choose an option:"),
            color=discord.Color.blue()
        )
        
        # إضافة رسالة تذكيرية في التذييل
        footer_text = "انقر على الأزرار للتنقل" if self.language == "ar" else "Click the buttons to navigate"
        embed.set_footer(text=footer_text)
        
        return embed
    
    async def _show_help(self, interaction):
        """عرض مساعدة البوت"""
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إنشاء رسالة مضمنة للمساعدة
        if self.language == "ar":
            embed = discord.Embed(
                title="❓ مساعدة البوت",
                description="دليل استخدام البوت:",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="🎮 الألعاب",
                value="• سباق الخيل: العب واربح عملات!\n"
                      "• المزيد من الألعاب قريبًا!",
                inline=False
            )
            
            embed.add_field(
                name="🎵 الموسيقى",
                value="• استخدم أزرار التشغيل والإيقاف والتخطي\n"
                      "• أو استخدم الأمر `تشغيل` مع رابط",
                inline=False
            )
            
            embed.add_field(
                name="⚙️ الإعدادات",
                value="• غير لغة البوت\n"
                      "• المزيد من الإعدادات قريبًا!",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❓ Bot Help",
                description="Guide to using the bot:",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="🎮 Games",
                value="• Horse Race: Play and win coins!\n"
                      "• More games coming soon!",
                inline=False
            )
            
            embed.add_field(
                name="🎵 Music",
                value="• Use the play, stop and skip buttons\n"
                      "• Or use the `play` command with a URL",
                inline=False
            )
            
            embed.add_field(
                name="⚙️ Settings",
                value="• Change bot language\n"
                      "• More settings coming soon!",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def _start_horse_race(self, interaction):
        """بدء لعبة سباق الخيل"""
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة
        await interaction.response.edit_message(view=None)
        
        # تشغيل أمر سباق الخيل
        horse_race_command = self.bot.get_command("سباق_الخيل")
        if horse_race_command:
            ctx = self.ctx
            await ctx.invoke(horse_race_command)
    
    async def _play_music(self, interaction):
        """تشغيل الموسيقى"""
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # طلب رابط من المستخدم
        prompt = "أرسل رابط الأغنية:" if self.language == "ar" else "Send the song URL:"
        await interaction.response.send_message(prompt)
        
        # انتظار رد المستخدم
        try:
            response = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == self.ctx.author and m.channel == self.ctx.channel,
                timeout=30
            )
            
            # تشغيل أمر تشغيل الموسيقى
            play_command = self.bot.get_command("تشغيل")
            if play_command:
                ctx = self.ctx
                await ctx.invoke(play_command, url=response.content)
        except asyncio.TimeoutError:
            timeout_msg = "انتهت المهلة. يرجى المحاولة مرة أخرى." if self.language == "ar" else "Timed out. Please try again."
            await self.ctx.send(timeout_msg)
    
    async def _stop_music(self, interaction):
        """إيقاف الموسيقى"""
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # تشغيل أمر إيقاف الموسيقى
        stop_command = self.bot.get_command("إيقاف")
        if stop_command:
            ctx = self.ctx
            await ctx.invoke(stop_command)
            
            success_msg = "تم إيقاف الموسيقى." if self.language == "ar" else "Music stopped."
            await interaction.response.send_message(success_msg)
    
    async def _skip_music(self, interaction):
        """تخطي الأغنية الحالية"""
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # تشغيل أمر تخطي الموسيقى
        skip_command = self.bot.get_command("تخطي")
        if skip_command:
            ctx = self.ctx
            await ctx.invoke(skip_command)
            
            success_msg = "تم تخطي الأغنية." if self.language == "ar" else "Song skipped."
            await interaction.response.send_message(success_msg)
    
    async def _language_settings(self, interaction):
        """فتح إعدادات اللغة"""
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة
        await interaction.response.edit_message(view=None)
        
        # تشغيل أمر اللغة
        language_command = self.bot.get_command("لغة")
        if language_command:
            ctx = self.ctx
            await ctx.invoke(language_command)
    
    async def on_timeout(self):
        """معالجة انتهاء وقت القائمة"""
        if self.message:
            # تعطيل الأزرار عند انتهاء الوقت
            for item in self.children:
                item.disabled = True
            
            timeout_msg = "انتهى وقت القائمة" if self.language == "ar" else "Menu timed out"
            
            embed = discord.Embed(
                title=timeout_msg,
                description="" if self.language == "ar" else "",
                color=discord.Color.red()
            )
            
            await self.message.edit(embed=embed, view=self)

class MainMenu(commands.Cog):
    """نظام القائمة الرئيسية والتنقل للبوت"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name="قائمة",
        aliases=["menu", "م", "m"],
        description="فتح القائمة الرئيسية للبوت"
    )
    async def menu(self, ctx):
        """
        فتح القائمة الرئيسية للبوت مع أزرار التنقل
        """
        # إنشاء منظر القائمة
        view = NavigationView(self.bot, ctx)
        # عرض القائمة الرئيسية
        await view.show_menu("main")

async def setup(bot):
    """إعداد الصنف وإضافته إلى البوت"""
    await bot.add_cog(MainMenu(bot)) 