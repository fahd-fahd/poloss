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
                "البنك": "Bank",
                "دعوات": "Invites",
                "تشغيل سريع": "Quick Play",
                "اختصارات سريعة": "Quick Shortcuts",
                "تحويل": "Transfer",
                "سرقة": "Steal",
                "حماية": "Protection",
                "رصيد": "Balance",
                "بحث": "Search",
                "صوت": "Voice",
                "قائمة شاملة": "Full Menu",
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
        
        # زر البنك/الاقتصاد
        economy_button = MenuButton(
            "البنك", 
            emoji="💰", 
            style=discord.ButtonStyle.success, 
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
        
        # زر الدعوات
        invites_button = MenuButton(
            "دعوات", 
            emoji="🔗", 
            style=discord.ButtonStyle.secondary, 
            language=self.language,
            action=lambda i: self.show_menu("invites", i)
        )
        self.add_item(invites_button)
        
        # زر التشغيل السريع في الصف الثاني
        quick_play_button = MenuButton(
            "تشغيل سريع", 
            emoji="▶️", 
            style=discord.ButtonStyle.success, 
            language=self.language,
            action=self._quick_play_music
        )
        self.add_item(quick_play_button)
        
        # زر الاختصارات السريعة في الصف الثاني
        quick_shortcuts_button = MenuButton(
            "اختصارات سريعة", 
            emoji="⚡", 
            style=discord.ButtonStyle.danger, 
            language=self.language,
            action=self._show_quick_shortcuts
        )
        self.add_item(quick_shortcuts_button)
        
        # زر الإعدادات في الصف الثاني
        settings_button = MenuButton(
            "إعدادات", 
            emoji="⚙️", 
            style=discord.ButtonStyle.secondary, 
            language=self.language,
            action=lambda i: self.show_menu("settings", i)
        )
        self.add_item(settings_button)
        
        # زر المساعدة في الصف الثاني
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
        
        # زر لعبة الصيد
        fishing_button = MenuButton(
            "صيد", 
            emoji="🎣", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=self._play_fishing
        )
        self.add_item(fishing_button)
        
        # زر لعبة النرد
        dice_button = MenuButton(
            "نرد", 
            emoji="🎲", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=self._play_dice
        )
        self.add_item(dice_button)
        
        # زر لعبة بلاك جاك
        blackjack_button = MenuButton(
            "بلاك جاك", 
            emoji="🃏", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=self._play_blackjack
        )
        self.add_item(blackjack_button)
    
    async def _create_music_menu(self):
        """إنشاء قائمة الموسيقى"""
        # زر تشغيل
        play_button = MenuButton(
            "تشغيل", 
            emoji="▶️", 
            style=discord.ButtonStyle.success, 
            language=self.language,
            action=self._play_music
        )
        self.add_item(play_button)
        
        # زر إيقاف
        stop_button = MenuButton(
            "إيقاف", 
            emoji="⏹️", 
            style=discord.ButtonStyle.danger, 
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
        
        # زر بحث
        search_button = MenuButton(
            "بحث", 
            emoji="🔍", 
            style=discord.ButtonStyle.secondary, 
            language=self.language,
            action=self._search_music
        )
        self.add_item(search_button)
        
        # زر التحكم بالصوت
        volume_button = MenuButton(
            "صوت", 
            emoji="🔊", 
            style=discord.ButtonStyle.secondary, 
            language=self.language,
            action=self._volume_control
        )
        self.add_item(volume_button)
    
    async def _create_economy_menu(self):
        """إنشاء قائمة الاقتصاد (البنك)"""
        # زر الرصيد
        balance_button = MenuButton(
            "رصيد", 
            emoji="💵", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=self._show_balance
        )
        self.add_item(balance_button)
        
        # زر المكافأة اليومية
        daily_button = MenuButton(
            "المكافأة اليومية", 
            emoji="🎁", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=self._get_daily_reward
        )
        self.add_item(daily_button)
        
        # زر الحماية
        protection_button = MenuButton(
            "حماية", 
            emoji="🛡️", 
            style=discord.ButtonStyle.success, 
            language=self.language,
            action=self._activate_protection
        )
        self.add_item(protection_button)
        
        # زر التحويل
        transfer_button = MenuButton(
            "تحويل", 
            emoji="💸", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=self._transfer_money
        )
        self.add_item(transfer_button)
        
        # زر السرقة
        steal_button = MenuButton(
            "سرقة", 
            emoji="🕵️", 
            style=discord.ButtonStyle.danger, 
            language=self.language,
            action=self._quick_steal
        )
        self.add_item(steal_button)
    
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
        if menu_type == "main":
            title = "🤖 القائمة الرئيسية" if self.language == "ar" else "🤖 Main Menu"
            description = "اختر إحدى الفئات أدناه:" if self.language == "ar" else "Choose one of the categories below:"
            color = discord.Color.blue()
            
            embed = discord.Embed(title=title, description=description, color=color)
            
            # إضافة حقول الوصف للقوائم المختلفة
            embed.add_field(
                name="🎮 الألعاب" if self.language == "ar" else "🎮 Games",
                value="العب وأربح عملات" if self.language == "ar" else "Play and earn coins",
                inline=True
            )
            
            embed.add_field(
                name="💰 البنك" if self.language == "ar" else "💰 Bank",
                value="إدارة أموالك" if self.language == "ar" else "Manage your money",
                inline=True
            )
            
            embed.add_field(
                name="🎵 الموسيقى" if self.language == "ar" else "🎵 Music",
                value="استمع للموسيقى" if self.language == "ar" else "Listen to music",
                inline=True
            )
            
            embed.add_field(
                name="▶️ تشغيل سريع" if self.language == "ar" else "▶️ Quick Play",
                value="تشغيل موسيقى بخطوة واحدة" if self.language == "ar" else "Play music in one step",
                inline=True
            )
            
            embed.add_field(
                name="⚡ اختصارات سريعة" if self.language == "ar" else "⚡ Quick Shortcuts",
                value="وصول سريع للأوامر الشائعة" if self.language == "ar" else "Quick access to common commands",
                inline=True
            )
            
        elif menu_type == "games":
            title = "🎮 قائمة الألعاب" if self.language == "ar" else "🎮 Games Menu"
            description = "اختر إحدى الألعاب أدناه:" if self.language == "ar" else "Choose one of the games below:"
            color = discord.Color.green()
            
            embed = discord.Embed(title=title, description=description, color=color)
            
            # إضافة معلومات حول الألعاب
            embed.add_field(
                name="🏇 سباق الخيل" if self.language == "ar" else "🏇 Horse Race",
                value="راهن على الخيول واربح الرهان!" if self.language == "ar" else "Bet on horses and win the race!",
                inline=True
            )
            
            embed.add_field(
                name="🎣 الصيد" if self.language == "ar" else "🎣 Fishing",
                value="اصطد الأسماك واربح العملات" if self.language == "ar" else "Catch fish and earn coins",
                inline=True
            )
            
            embed.add_field(
                name="🎲 النرد" if self.language == "ar" else "🎲 Dice",
                value="العب النرد وضاعف أموالك" if self.language == "ar" else "Play dice and double your money",
                inline=True
            )
            
            embed.add_field(
                name="🃏 بلاك جاك" if self.language == "ar" else "🃏 Blackjack",
                value="حاول الوصول إلى 21 واربح المال" if self.language == "ar" else "Try to reach 21 and win money",
                inline=True
            )
            
            # إضافة تلميح للاستخدام المباشر
            embed.add_field(
                name="💡 تلميح" if self.language == "ar" else "💡 Tip",
                value="يمكنك استخدام الأوامر مباشرة: `!صيد` أو `!نرد` أو `!سباق`" if self.language == "ar" else "You can use commands directly: `!fish` or `!dice` or `!horserace`",
                inline=False
            )
            
        elif menu_type == "music":
            title = "🎵 قائمة الموسيقى" if self.language == "ar" else "🎵 Music Menu"
            description = "اختر إحدى خيارات الموسيقى أدناه:" if self.language == "ar" else "Choose one of the music options below:"
            color = discord.Color.purple()
            
            embed = discord.Embed(title=title, description=description, color=color)
            
            # إضافة معلومات حول أوامر الموسيقى
            embed.add_field(
                name="▶️ تشغيل" if self.language == "ar" else "▶️ Play",
                value="تشغيل أغنية جديدة" if self.language == "ar" else "Play a new song",
                inline=True
            )
            
            embed.add_field(
                name="⏹️ إيقاف" if self.language == "ar" else "⏹️ Stop",
                value="إيقاف تشغيل الموسيقى" if self.language == "ar" else "Stop playing music",
                inline=True
            )
            
            embed.add_field(
                name="⏭️ تخطي" if self.language == "ar" else "⏭️ Skip",
                value="الانتقال للأغنية التالية" if self.language == "ar" else "Skip to the next song",
                inline=True
            )
            
            embed.add_field(
                name="🔍 بحث" if self.language == "ar" else "🔍 Search",
                value="البحث عن أغنية" if self.language == "ar" else "Search for a song",
                inline=True
            )
            
            embed.add_field(
                name="🔊 صوت" if self.language == "ar" else "🔊 Volume",
                value="التحكم بمستوى الصوت" if self.language == "ar" else "Control the volume level",
                inline=True
            )
            
            # إضافة تلميح للاستخدام المباشر
            embed.add_field(
                name="💡 تلميح" if self.language == "ar" else "💡 Tip",
                value="يمكنك استخدام الأوامر مباشرة: `!p رابط/اسم_أغنية` أو `!s` أو `!sk`" if self.language == "ar" else "You can use commands directly: `!p link/song_name` or `!s` or `!sk`",
                inline=False
            )
            
        elif menu_type == "economy":
            title = "💰 قائمة البنك" if self.language == "ar" else "💰 Bank Menu"
            description = "اختر إحدى خيارات البنك أدناه:" if self.language == "ar" else "Choose one of the bank options below:"
            color = discord.Color.gold()
            
            embed = discord.Embed(title=title, description=description, color=color)
            
            # إضافة معلومات عن أوامر البنك
            embed.add_field(
                name="💵 رصيد" if self.language == "ar" else "💵 Balance",
                value="عرض رصيدك الحالي" if self.language == "ar" else "View your current balance",
                inline=True
            )
            
            embed.add_field(
                name="🎁 المكافأة اليومية" if self.language == "ar" else "🎁 Daily Reward",
                value="احصل على مكافأة يومية" if self.language == "ar" else "Get a daily reward",
                inline=True
            )
            
            embed.add_field(
                name="🛡️ حماية" if self.language == "ar" else "🛡️ Protection",
                value="حماية أموالك من السرقة" if self.language == "ar" else "Protect your money from theft",
                inline=True
            )
            
            embed.add_field(
                name="💸 تحويل" if self.language == "ar" else "💸 Transfer",
                value="تحويل أموال لشخص آخر" if self.language == "ar" else "Transfer money to another person",
                inline=True
            )
            
            embed.add_field(
                name="🕵️ سرقة" if self.language == "ar" else "🕵️ Steal",
                value="محاولة سرقة أموال شخص آخر" if self.language == "ar" else "Try to steal money from another person",
                inline=True
            )
            
            # إضافة معلومات عن نظام الحماية
            embed.add_field(
                name="🛡️ نظام الحماية" if self.language == "ar" else "🛡️ Protection System",
                value="استخدم **!حماية** لشراء حماية من السرقة بثلاثة مستويات:\n"
                     "- 3 ساعات مقابل 2500 عملة\n"
                     "- 8 ساعات مقابل 5000 عملة\n"
                     "- 24 ساعة مقابل 15000 عملة" if self.language == "ar" else 
                     "Use **!protection** to buy theft protection with three levels:\n"
                     "- 3 hours for 2500 coins\n"
                     "- 8 hours for 5000 coins\n"
                     "- 24 hours for 15000 coins",
                inline=False
            )
            
        elif menu_type == "invites":
            title = "🔗 قائمة الدعوات" if self.language == "ar" else "🔗 Invites Menu"
            description = "اختر إحدى خيارات الدعوات أدناه:" if self.language == "ar" else "Choose one of the invite options below:"
            color = discord.Color.blue()
            
            embed = discord.Embed(title=title, description=description, color=color)
            
            # إضافة معلومات حول أوامر الدعوات
            embed.add_field(
                name="🔗 انضمام لرابط" if self.language == "ar" else "🔗 Join Link",
                value="الانضمام إلى سيرفر باستخدام رابط دعوة" if self.language == "ar" else "Join a server using an invite link",
                inline=True
            )
            
            embed.add_field(
                name="📨 إنشاء دعوة" if self.language == "ar" else "📨 Create Invite",
                value="إنشاء رابط دعوة للقناة الحالية" if self.language == "ar" else "Create an invite link for the current channel",
                inline=True
            )
            
            # إضافة تلميح للاستخدام المباشر
            embed.add_field(
                name="💡 تلميح" if self.language == "ar" else "💡 Tip",
                value="يمكنك استخدام الأوامر مباشرة: `!دعوة رابط_الدعوة` أو `!إنشاء_دعوة`" if self.language == "ar" else "You can use commands directly: `!invite invite_link` or `!create_invite`",
                inline=False
            )
            
        elif menu_type == "shortcuts":
            title = "⚡ الاختصارات السريعة" if self.language == "ar" else "⚡ Quick Shortcuts"
            description = "جميع الأوامر الشائعة في مكان واحد! اختر الأمر الذي تريده:" if self.language == "ar" else "All common commands in one place! Choose the command you want:"
            color = discord.Color.purple()
            
            embed = discord.Embed(title=title, description=description, color=color)
            
            # إضافة توضيح
            embed.add_field(
                name="🔰 معلومات" if self.language == "ar" else "🔰 Information",
                value="هذه القائمة تجمع الأوامر الأكثر استخداماً في مكان واحد للوصول السريع" if self.language == "ar" else "This menu combines the most used commands in one place for quick access",
                inline=False
            )
            
        elif menu_type == "settings":
            title = "⚙️ الإعدادات" if self.language == "ar" else "⚙️ Settings"
            description = "اختر إحدى خيارات الإعدادات أدناه:" if self.language == "ar" else "Choose one of the settings options below:"
            color = discord.Color.dark_gray()
            
            embed = discord.Embed(title=title, description=description, color=color)
        
        else:
            title = "قائمة غير معروفة" if self.language == "ar" else "Unknown Menu"
            description = "هذه القائمة غير معروفة." if self.language == "ar" else "This menu is unknown."
            color = discord.Color.red()
            
            embed = discord.Embed(title=title, description=description, color=color)
        
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
        """بدء سباق الخيل"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية لمنع التداخل
        await interaction.response.defer()
        await self.message.delete()
        
        # تنفيذ أمر سباق الخيل
        race_command = self.bot.get_command('سباق') or self.bot.get_command('horserace')
        if race_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(race_command)
        else:
            msg = "عذراً، لعبة سباق الخيل غير متاحة حالياً." if self.language == "ar" else "Sorry, the horse race game is not available."
            await interaction.followup.send(msg)
            
    async def _play_blackjack(self, interaction):
        """تشغيل لعبة بلاك جاك"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية لمنع التداخل
        await interaction.response.defer()
        await self.message.delete()
        
        # تنفيذ أمر بلاك جاك
        blackjack_command = self.bot.get_command('بلاك_جاك') or self.bot.get_command('blackjack')
        if blackjack_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(blackjack_command)
        else:
            msg = "عذراً، لعبة بلاك جاك غير متاحة حالياً." if self.language == "ar" else "Sorry, the blackjack game is not available."
            await interaction.followup.send(msg)
            
    async def _search_music(self, interaction):
        """البحث عن موسيقى"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.response.edit_message(view=None)
        
        # إعداد أمر البحث
        embed = discord.Embed(
            title="🔍 بحث عن موسيقى" if self.language == "ar" else "🔍 Music Search",
            description="أدخل اسم الأغنية التي تريد البحث عنها:" if self.language == "ar" else "Enter the name of the song you want to search for:",
            color=discord.Color.blue()
        )
        
        await interaction.response.edit_message(embed=embed)
        
        # انتظار رد المستخدم
        try:
            response = await self.bot.wait_for(
                'message',
                check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id,
                timeout=30.0
            )
            
            # رسالة الانتظار
            wait_embed = discord.Embed(
                title="🔍 جاري البحث..." if self.language == "ar" else "🔍 Searching...",
                description=f"البحث عن: `{response.content}`" if self.language == "ar" else f"Searching for: `{response.content}`",
                color=discord.Color.blue()
            )
            
            await self.message.edit(embed=wait_embed)
            
            # تنفيذ أمر البحث
            search_command = self.bot.get_command('بحث') or self.bot.get_command('search')
            if search_command:
                ctx = await self.bot.get_context(response)
                await ctx.invoke(search_command, query=response.content)
                
                # حذف رسالة المستخدم
                try:
                    await response.delete()
                except:
                    pass
                
                # إعادة إنشاء القائمة بعد فترة
                await asyncio.sleep(5)
                await self.show_menu("music")
            else:
                error_embed = discord.Embed(
                    title="❌ خطأ" if self.language == "ar" else "❌ Error",
                    description="عذراً، أمر البحث غير متاح حالياً." if self.language == "ar" else "Sorry, the search command is not available.",
                    color=discord.Color.red()
                )
                await self.message.edit(embed=error_embed)
                # إعادة إنشاء القائمة بعد الخطأ
                await asyncio.sleep(3)
                await self.show_menu("music")
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ انتهت المهلة" if self.language == "ar" else "⏰ Timeout",
                description="انتهت مهلة الانتظار. يرجى المحاولة مرة أخرى." if self.language == "ar" else "Timeout. Please try again.",
                color=discord.Color.orange()
            )
            await self.message.edit(embed=timeout_embed)
            # إعادة إنشاء القائمة بعد انتهاء المهلة
            await asyncio.sleep(3)
            await self.show_menu("music")
            
    async def _volume_control(self, interaction):
        """التحكم بمستوى الصوت"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.response.edit_message(view=None)
        
        # إعداد أمر التحكم بالصوت
        embed = discord.Embed(
            title="🔊 التحكم بالصوت" if self.language == "ar" else "🔊 Volume Control",
            description="أدخل مستوى الصوت المطلوب (1-100):" if self.language == "ar" else "Enter the desired volume level (1-100):",
            color=discord.Color.blue()
        )
        
        await interaction.response.edit_message(embed=embed)
        
        # انتظار رد المستخدم
        try:
            response = await self.bot.wait_for(
                'message',
                check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id,
                timeout=30.0
            )
            
            # رسالة الانتظار
            wait_embed = discord.Embed(
                title="🔊 جاري تعديل الصوت..." if self.language == "ar" else "🔊 Adjusting volume...",
                description=f"تعديل الصوت إلى: `{response.content}`" if self.language == "ar" else f"Adjusting volume to: `{response.content}`",
                color=discord.Color.blue()
            )
            
            await self.message.edit(embed=wait_embed)
            
            # تنفيذ أمر التحكم بالصوت
            volume_command = self.bot.get_command('صوت') or self.bot.get_command('volume')
            if volume_command:
                ctx = await self.bot.get_context(response)
                await ctx.invoke(volume_command, channel_or_volume=response.content)
                
                # حذف رسالة المستخدم
                try:
                    await response.delete()
                except:
                    pass
                
                # إعادة إنشاء القائمة بعد فترة
                await asyncio.sleep(3)
                await self.show_menu("music")
            else:
                error_embed = discord.Embed(
                    title="❌ خطأ" if self.language == "ar" else "❌ Error",
                    description="عذراً، أمر التحكم بالصوت غير متاح حالياً." if self.language == "ar" else "Sorry, the volume control command is not available.",
                    color=discord.Color.red()
                )
                await self.message.edit(embed=error_embed)
                # إعادة إنشاء القائمة بعد الخطأ
                await asyncio.sleep(3)
                await self.show_menu("music")
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ انتهت المهلة" if self.language == "ar" else "⏰ Timeout",
                description="انتهت مهلة الانتظار. يرجى المحاولة مرة أخرى." if self.language == "ar" else "Timeout. Please try again.",
                color=discord.Color.orange()
            )
            await self.message.edit(embed=timeout_embed)
            # إعادة إنشاء القائمة بعد انتهاء المهلة
            await asyncio.sleep(3)
            await self.show_menu("music")
            
    async def _activate_protection(self, interaction):
        """تفعيل الحماية"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.response.defer()
        await self.message.delete()
        
        # تنفيذ أمر الحماية
        protection_command = self.bot.get_command('حماية') or self.bot.get_command('protection')
        if protection_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(protection_command)
        else:
            msg = "عذراً، أمر الحماية غير متاح حالياً." if self.language == "ar" else "Sorry, the protection command is not available."
            await interaction.followup.send(msg)
            
    async def _transfer_money(self, interaction):
        """تحويل الأموال"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.response.edit_message(view=None)
        
        # إعداد أمر التحويل
        embed = discord.Embed(
            title="💸 تحويل أموال" if self.language == "ar" else "💸 Transfer Money",
            description="يرجى كتابة اسم المستخدم والمبلغ بالصيغة التالية:\n" + 
                        "`@اسم_المستخدم 1000`" if self.language == "ar" else 
                        "Please enter the username and amount in the following format:\n" +
                        "`@username 1000`",
            color=discord.Color.blue()
        )
        
        await interaction.response.edit_message(embed=embed)
        
        # انتظار رد المستخدم
        try:
            response = await self.bot.wait_for(
                'message',
                check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id,
                timeout=30.0
            )
            
            # رسالة الانتظار
            wait_embed = discord.Embed(
                title="💸 جاري التحويل..." if self.language == "ar" else "💸 Transferring...",
                description=f"محاولة تحويل: `{response.content}`" if self.language == "ar" else f"Attempting to transfer: `{response.content}`",
                color=discord.Color.blue()
            )
            
            await self.message.edit(embed=wait_embed)
            
            # تنفيذ أمر التحويل
            transfer_command = self.bot.get_command('تحويل') or self.bot.get_command('transfer')
            if transfer_command:
                ctx = await self.bot.get_context(response)
                
                # معالجة معلمات الأمر
                args = response.content.split()
                if len(args) >= 2:
                    recipient = args[0]
                    amount = args[1]
                    
                    await ctx.invoke(transfer_command, recipient=recipient, amount=amount)
                    
                    # حذف رسالة المستخدم
                    try:
                        await response.delete()
                    except:
                        pass
                    
                    # إعادة إنشاء القائمة بعد فترة
                    await asyncio.sleep(5)
                    await self.show_menu("economy")
                else:
                    error_embed = discord.Embed(
                        title="❌ خطأ في الصيغة" if self.language == "ar" else "❌ Format Error",
                        description="الصيغة غير صحيحة. يرجى استخدام الصيغة: `@اسم_المستخدم 1000`" if self.language == "ar" else "Incorrect format. Please use the format: `@username 1000`",
                        color=discord.Color.red()
                    )
                    await self.message.edit(embed=error_embed)
                    # إعادة إنشاء القائمة بعد الخطأ
                    await asyncio.sleep(3)
                    await self.show_menu("economy")
            else:
                error_embed = discord.Embed(
                    title="❌ خطأ" if self.language == "ar" else "❌ Error",
                    description="عذراً، أمر التحويل غير متاح حالياً." if self.language == "ar" else "Sorry, the transfer command is not available.",
                    color=discord.Color.red()
                )
                await self.message.edit(embed=error_embed)
                # إعادة إنشاء القائمة بعد الخطأ
                await asyncio.sleep(3)
                await self.show_menu("economy")
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ انتهت المهلة" if self.language == "ar" else "⏰ Timeout",
                description="انتهت مهلة الانتظار. يرجى المحاولة مرة أخرى." if self.language == "ar" else "Timeout. Please try again.",
                color=discord.Color.orange()
            )
            await self.message.edit(embed=timeout_embed)
            # إعادة إنشاء القائمة بعد انتهاء المهلة
            await asyncio.sleep(3)
            await self.show_menu("economy")
            
    async def _join_invite(self, interaction):
        """الانضمام لرابط دعوة"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.response.edit_message(view=None)
        
        # إعداد أمر الانضمام
        embed = discord.Embed(
            title="🔗 انضمام لرابط دعوة" if self.language == "ar" else "🔗 Join Invite Link",
            description="يرجى إدخال رابط الدعوة الذي تريد الانضمام إليه:" if self.language == "ar" else "Please enter the invite link you want to join:",
            color=discord.Color.blue()
        )
        
        # إضافة تلميح
        embed.add_field(
            name="💡 تلميح" if self.language == "ar" else "💡 Tip",
            value="يجب أن يكون الرابط من الشكل التالي:\n`https://discord.gg/...`" if self.language == "ar" else "The link should be in the following format:\n`https://discord.gg/...`",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed)
        
        # انتظار رد المستخدم
        try:
            response = await self.bot.wait_for(
                'message',
                check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id,
                timeout=30.0
            )
            
            # رسالة الانتظار
            wait_embed = discord.Embed(
                title="🔗 جاري الانضمام..." if self.language == "ar" else "🔗 Joining...",
                description=f"محاولة الانضمام للرابط: `{response.content}`" if self.language == "ar" else f"Attempting to join link: `{response.content}`",
                color=discord.Color.blue()
            )
            
            await self.message.edit(embed=wait_embed)
            
            # تنفيذ أمر الانضمام
            invite_command = self.bot.get_command('دعوة') or self.bot.get_command('invite')
            if invite_command:
                ctx = await self.bot.get_context(response)
                await ctx.invoke(invite_command, invite_link=response.content)
                
                # حذف رسالة المستخدم
                try:
                    await response.delete()
                except:
                    pass
                
                # إعادة إنشاء القائمة بعد فترة
                await asyncio.sleep(5)
                await self.show_menu("invites")
            else:
                error_embed = discord.Embed(
                    title="❌ خطأ" if self.language == "ar" else "❌ Error",
                    description="عذراً، أمر الانضمام غير متاح حالياً." if self.language == "ar" else "Sorry, the join command is not available.",
                    color=discord.Color.red()
                )
                await self.message.edit(embed=error_embed)
                # إعادة إنشاء القائمة بعد الخطأ
                await asyncio.sleep(3)
                await self.show_menu("invites")
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ انتهت المهلة" if self.language == "ar" else "⏰ Timeout",
                description="انتهت مهلة الانتظار. يرجى المحاولة مرة أخرى." if self.language == "ar" else "Timeout. Please try again.",
                color=discord.Color.orange()
            )
            await self.message.edit(embed=timeout_embed)
            # إعادة إنشاء القائمة بعد انتهاء المهلة
            await asyncio.sleep(3)
            await self.show_menu("invites")
            
    async def _create_invite(self, interaction):
        """إنشاء دعوة"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.response.defer()
        
        # تنفيذ أمر إنشاء دعوة
        create_invite_command = self.bot.get_command('إنشاء_دعوة') or self.bot.get_command('create_invite')
        if create_invite_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(create_invite_command)
            
            # إعادة إنشاء القائمة بعد فترة
            await asyncio.sleep(5)
            await self.show_menu("invites")
        else:
            # محاولة إنشاء دعوة مباشرة إذا كان الأمر غير متاح
            try:
                invite = await interaction.channel.create_invite(max_age=86400, max_uses=0, unique=True)
                
                success_embed = discord.Embed(
                    title="✅ تم إنشاء الدعوة بنجاح" if self.language == "ar" else "✅ Invite Created Successfully",
                    description=f"رابط الدعوة: {invite.url}" if self.language == "ar" else f"Invite link: {invite.url}",
                    color=discord.Color.green()
                )
                
                await interaction.followup.send(embed=success_embed)
                
                # إعادة إنشاء القائمة بعد فترة
                await asyncio.sleep(5)
                await self.show_menu("invites")
            except Exception as e:
                error_embed = discord.Embed(
                    title="❌ خطأ" if self.language == "ar" else "❌ Error",
                    description=f"حدث خطأ أثناء إنشاء الدعوة: {str(e)}" if self.language == "ar" else f"An error occurred while creating the invite: {str(e)}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=error_embed)
                
                # إعادة إنشاء القائمة بعد فترة
                await asyncio.sleep(3)
                await self.show_menu("invites")

    async def _quick_play_music(self, interaction):
        """تشغيل موسيقى سريع"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # التحقق ما إذا كان المستخدم في قناة صوتية
        if not interaction.user.voice:
            error_msg = "يجب أن تكون في قناة صوتية أولاً!" if self.language == "ar" else "You must be in a voice channel first!"
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.response.defer()
        await self.message.delete()
        
        # إعداد واجهة التشغيل السريع
        embed = discord.Embed(
            title="▶️ التشغيل السريع" if self.language == "ar" else "▶️ Quick Play",
            description="أدخل اسم الأغنية أو رابط YouTube للتشغيل مباشرة:" if self.language == "ar" else "Enter the song name or YouTube link for direct playback:",
            color=discord.Color.green()
        )
        
        # إضافة تلميح حول التشغيل
        embed.add_field(
            name="🔊 ملاحظة" if self.language == "ar" else "🔊 Note",
            value="سيتم الانضمام تلقائياً إلى قناتك الصوتية الحالية وتشغيل الموسيقى فوراً!" if self.language == "ar" else "The bot will automatically join your current voice channel and play music immediately!",
            inline=False
        )
        
        # إضافة أمثلة
        embed.add_field(
            name="📝 أمثلة" if self.language == "ar" else "📝 Examples",
            value="اكتب اسم أغنية: `أغنية عربية`\nأو رابط: `https://www.youtube.com/...`" if self.language == "ar" else "Type a song name: `Arabic song`\nOr a link: `https://www.youtube.com/...`",
            inline=False
        )
        
        message = await interaction.followup.send(embed=embed)
        
        # انتظار رد المستخدم
        try:
            response = await self.bot.wait_for(
                'message',
                check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id,
                timeout=60.0
            )
            
            # رسالة الانتظار
            wait_embed = discord.Embed(
                title="🎵 جاري تشغيل الموسيقى..." if self.language == "ar" else "🎵 Playing music...",
                description=f"جاري تشغيل: `{response.content}`" if self.language == "ar" else f"Playing: `{response.content}`",
                color=discord.Color.blue()
            )
            
            wait_embed.set_footer(text="يرجى الانتظار قليلاً..." if self.language == "ar" else "Please wait a moment...")
            await message.edit(embed=wait_embed)
            
            # محاولة الانضمام للقناة الصوتية أولاً إذا لم يكن البوت متصلاً
            voice_channel = interaction.user.voice.channel
            voice_cog = self.bot.get_cog('VoiceControl')
            if voice_cog:
                voice_ctx = await self.bot.get_context(self.ctx.message)
                voice_command = self.bot.get_command('صوت') or self.bot.get_command('voice')
                if voice_command and not (hasattr(self.ctx.guild, 'voice_client') and self.ctx.guild.voice_client):
                    try:
                        await voice_ctx.invoke(voice_command, channel_or_volume=str(voice_channel.id))
                    except Exception as e:
                        print(f"Error joining voice channel: {e}")
            
            # تنفيذ أمر التشغيل
            play_command = self.bot.get_command('تشغيل') or self.bot.get_command('play')
            if play_command:
                ctx = await self.bot.get_context(response)
                await ctx.invoke(play_command, query=response.content)
                
                # تأكيد التشغيل
                success_embed = discord.Embed(
                    title="✅ تم التشغيل بنجاح" if self.language == "ar" else "✅ Successfully played",
                    description=f"تم تشغيل: `{response.content}`" if self.language == "ar" else f"Now playing: `{response.content}`",
                    color=discord.Color.green()
                )
                success_embed.set_footer(text="استمتع بالموسيقى!" if self.language == "ar" else "Enjoy the music!")
                
                try:
                    await message.edit(embed=success_embed)
                    # مسح الرسالة بعد 5 ثوانٍ
                    await asyncio.sleep(5)
                    await message.delete()
                except:
                    pass
                
                # حذف رسالة المستخدم
                try:
                    await response.delete()
                except:
                    pass
            else:
                error_embed = discord.Embed(
                    title="❌ خطأ" if self.language == "ar" else "❌ Error",
                    description="عذراً، أمر التشغيل غير متاح حالياً." if self.language == "ar" else "Sorry, the play command is not available.",
                    color=discord.Color.red()
                )
                await message.edit(embed=error_embed)
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ انتهت المهلة" if self.language == "ar" else "⏰ Timeout",
                description="انتهت مهلة الانتظار. يرجى المحاولة مرة أخرى." if self.language == "ar" else "Timeout. Please try again.",
                color=discord.Color.orange()
            )
            await message.edit(embed=timeout_embed)

    async def _show_quick_shortcuts(self, interaction):
        """عرض قائمة الاختصارات السريعة"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # تغيير القائمة الحالية إلى قائمة الاختصارات
        self.current_menu = "shortcuts"
        
        # إنشاء رسالة مضمنة لقائمة الاختصارات
        embed = await self._create_menu_embed("shortcuts")
        
        # تحديث القائمة
        await interaction.response.edit_message(embed=embed, view=self)
        
        # إنشاء أزرار الاختصارات
        # مسح الأزرار الحالية
        self.clear_items()
        
        # زر الرصيد السريع
        balance_button = MenuButton(
            "رصيد", 
            emoji="💰", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=self._show_balance
        )
        self.add_item(balance_button)
        
        # زر المكافأة اليومية
        daily_button = MenuButton(
            "المكافأة اليومية", 
            emoji="🎁", 
            style=discord.ButtonStyle.primary, 
            language=self.language,
            action=self._get_daily_reward
        )
        self.add_item(daily_button)
        
        # زر تشغيل موسيقى سريع
        quick_play_button = MenuButton(
            "تشغيل سريع", 
            emoji="▶️", 
            style=discord.ButtonStyle.success, 
            language=self.language,
            action=self._quick_play_music
        )
        self.add_item(quick_play_button)
        
        # زر لعبة سريعة
        quick_game_button = MenuButton(
            "لعبة سريعة", 
            emoji="🎲", 
            style=discord.ButtonStyle.secondary, 
            language=self.language,
            action=lambda i: self.show_menu("games", i)
        )
        self.add_item(quick_game_button)
        
        # زر الرجوع للقائمة الرئيسية
        back_button = MenuButton(
            "رجوع للرئيسية", 
            emoji="🔙", 
            style=discord.ButtonStyle.danger, 
            language=self.language,
            action=lambda i: self.show_menu("main", i)
        )
        self.add_item(back_button)

    async def _play_music(self, interaction):
        """تشغيل موسيقى"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # التحقق ما إذا كان المستخدم في قناة صوتية
        if not interaction.user.voice:
            error_msg = "يجب أن تكون في قناة صوتية أولاً!" if self.language == "ar" else "You must be in a voice channel first!"
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.response.defer()
        await self.message.delete()
        
        # إعداد واجهة التشغيل السريع
        embed = discord.Embed(
            title="▶️ التشغيل السريع" if self.language == "ar" else "▶️ Quick Play",
            description="أدخل اسم الأغنية أو رابط YouTube للتشغيل مباشرة:" if self.language == "ar" else "Enter the song name or YouTube link for direct playback:",
            color=discord.Color.green()
        )
        
        # إضافة تلميح حول التشغيل
        embed.add_field(
            name="🔊 ملاحظة" if self.language == "ar" else "🔊 Note",
            value="سيتم الانضمام تلقائياً إلى قناتك الصوتية الحالية وتشغيل الموسيقى فوراً!" if self.language == "ar" else "The bot will automatically join your current voice channel and play music immediately!",
            inline=False
        )
        
        # إضافة أمثلة
        embed.add_field(
            name="📝 أمثلة" if self.language == "ar" else "📝 Examples",
            value="اكتب اسم أغنية: `أغنية عربية`\nأو رابط: `https://www.youtube.com/...`" if self.language == "ar" else "Type a song name: `Arabic song`\nOr a link: `https://www.youtube.com/...`",
            inline=False
        )
        
        message = await interaction.followup.send(embed=embed)
        
        # انتظار رد المستخدم
        try:
            response = await self.bot.wait_for(
                'message',
                check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id,
                timeout=60.0
            )
            
            # رسالة الانتظار
            wait_embed = discord.Embed(
                title="🎵 جاري تشغيل الموسيقى..." if self.language == "ar" else "🎵 Playing music...",
                description=f"جاري تشغيل: `{response.content}`" if self.language == "ar" else f"Playing: `{response.content}`",
                color=discord.Color.blue()
            )
            
            wait_embed.set_footer(text="يرجى الانتظار قليلاً..." if self.language == "ar" else "Please wait a moment...")
            await message.edit(embed=wait_embed)
            
            # محاولة الانضمام للقناة الصوتية أولاً إذا لم يكن البوت متصلاً
            voice_channel = interaction.user.voice.channel
            voice_cog = self.bot.get_cog('VoiceControl')
            if voice_cog:
                voice_ctx = await self.bot.get_context(self.ctx.message)
                voice_command = self.bot.get_command('صوت') or self.bot.get_command('voice')
                if voice_command and not (hasattr(self.ctx.guild, 'voice_client') and self.ctx.guild.voice_client):
                    try:
                        await voice_ctx.invoke(voice_command, channel_or_volume=str(voice_channel.id))
                    except Exception as e:
                        print(f"Error joining voice channel: {e}")
            
            # تنفيذ أمر التشغيل
            play_command = self.bot.get_command('تشغيل') or self.bot.get_command('play')
            if play_command:
                ctx = await self.bot.get_context(response)
                await ctx.invoke(play_command, query=response.content)
                
                # تأكيد التشغيل
                success_embed = discord.Embed(
                    title="✅ تم التشغيل بنجاح" if self.language == "ar" else "✅ Successfully played",
                    description=f"تم تشغيل: `{response.content}`" if self.language == "ar" else f"Now playing: `{response.content}`",
                    color=discord.Color.green()
                )
                success_embed.set_footer(text="استمتع بالموسيقى!" if self.language == "ar" else "Enjoy the music!")
                
                try:
                    await message.edit(embed=success_embed)
                    # مسح الرسالة بعد 5 ثوانٍ
                    await asyncio.sleep(5)
                    await message.delete()
                except:
                    pass
                
                # حذف رسالة المستخدم
                try:
                    await response.delete()
                except:
                    pass
            else:
                error_embed = discord.Embed(
                    title="❌ خطأ" if self.language == "ar" else "❌ Error",
                    description="عذراً، أمر التشغيل غير متاح حالياً." if self.language == "ar" else "Sorry, the play command is not available.",
                    color=discord.Color.red()
                )
                await message.edit(embed=error_embed)
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ انتهت المهلة" if self.language == "ar" else "⏰ Timeout",
                description="انتهت مهلة الانتظار. يرجى المحاولة مرة أخرى." if self.language == "ar" else "Timeout. Please try again.",
                color=discord.Color.orange()
            )
            await message.edit(embed=timeout_embed)

    async def _show_balance(self, interaction):
        """عرض الرصيد"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية لمنع التداخل
        await interaction.response.defer()
        await self.message.delete()
        
        # تنفيذ أمر الرصيد
        balance_command = self.bot.get_command('رصيد') or self.bot.get_command('balance')
        if balance_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(balance_command)
        else:
            msg = "عذراً، أمر الرصيد غير متاح حالياً." if self.language == "ar" else "Sorry, the balance command is not available."
            await interaction.followup.send(msg)

    async def _get_daily_reward(self, interaction):
        """الحصول على المكافأة اليومية"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية لمنع التداخل
        await interaction.response.defer()
        await self.message.delete()
        
        # تنفيذ أمر المكافأة اليومية
        daily_command = self.bot.get_command('يومي') or self.bot.get_command('daily')
        if daily_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(daily_command)
        else:
            msg = "عذراً، أمر المكافأة اليومية غير متاح حالياً." if self.language == "ar" else "Sorry, the daily reward command is not available."
            await interaction.followup.send(msg)
            
    async def _skip_music(self, interaction):
        """تخطي الأغنية الحالية"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.response.defer()
        
        # تنفيذ أمر تخطي الموسيقى
        skip_command = self.bot.get_command('تخطي') or self.bot.get_command('skip')
        if skip_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(skip_command)
            
            # إرسال رسالة تأكيد
            confirm_msg = "تم تخطي الأغنية الحالية." if self.language == "ar" else "Skipped the current song."
            await interaction.followup.send(confirm_msg, ephemeral=True)
        else:
            error_msg = "عذراً، أمر التخطي غير متاح حالياً." if self.language == "ar" else "Sorry, the skip command is not available."
            await interaction.followup.send(error_msg, ephemeral=True)
            
    async def _stop_music(self, interaction):
        """إيقاف الموسيقى"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.response.defer()
        
        # تنفيذ أمر إيقاف الموسيقى
        stop_command = self.bot.get_command('إيقاف') or self.bot.get_command('stop')
        if stop_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(stop_command)
            
            # إرسال رسالة تأكيد
            confirm_msg = "تم إيقاف الموسيقى." if self.language == "ar" else "Stopped the music."
            await interaction.followup.send(confirm_msg, ephemeral=True)
        else:
            error_msg = "عذراً، أمر الإيقاف غير متاح حالياً." if self.language == "ar" else "Sorry, the stop command is not available."
            await interaction.followup.send(error_msg, ephemeral=True)
            
    async def _quick_steal(self, interaction):
        """سرقة سريعة"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.response.edit_message(view=None)
        
        # إعداد أمر السرقة
        embed = discord.Embed(
            title="🕵️ سرقة سريعة" if self.language == "ar" else "🕵️ Quick Steal",
            description="أدخل اسم أو معرف المستخدم الذي تريد سرقته:" if self.language == "ar" else "Enter the name or ID of the user you want to steal from:",
            color=discord.Color.red()
        )
        
        # إضافة تحذير
        embed.add_field(
            name="⚠️ تحذير" if self.language == "ar" else "⚠️ Warning",
            value="تذكر أن السرقة قد تفشل وتخسر جزءاً من أموالك!" if self.language == "ar" else "Remember that stealing may fail and you could lose some money!",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed)
        
        # انتظار رد المستخدم
        try:
            response = await self.bot.wait_for(
                'message',
                check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id,
                timeout=30.0
            )
            
            # رسالة الانتظار
            wait_embed = discord.Embed(
                title="🕵️ جاري محاولة السرقة..." if self.language == "ar" else "🕵️ Attempting to steal...",
                description=f"محاولة سرقة `{response.content}`..." if self.language == "ar" else f"Attempting to steal from `{response.content}`...",
                color=discord.Color.gold()
            )
            
            await self.message.edit(embed=wait_embed)
            
            # تنفيذ أمر السرقة
            steal_command = self.bot.get_command('سرقة') or self.bot.get_command('steal')
            if steal_command:
                ctx = await self.bot.get_context(response)
                await ctx.invoke(steal_command, target=response.content)
                
                # حذف رسالة المستخدم
                try:
                    await response.delete()
                except:
                    pass
                
                # إعادة إنشاء القائمة بعد فترة
                await asyncio.sleep(5)
                await self.show_menu("economy")
            else:
                error_embed = discord.Embed(
                    title="❌ خطأ" if self.language == "ar" else "❌ Error",
                    description="عذراً، أمر السرقة غير متاح حالياً." if self.language == "ar" else "Sorry, the steal command is not available.",
                    color=discord.Color.red()
                )
                await self.message.edit(embed=error_embed)
                
                # إعادة إنشاء القائمة بعد فترة
                await asyncio.sleep(3)
                await self.show_menu("economy")
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ انتهت المهلة" if self.language == "ar" else "⏰ Timeout",
                description="انتهت مهلة الانتظار. يرجى المحاولة مرة أخرى." if self.language == "ar" else "Timeout. Please try again.",
                color=discord.Color.orange()
            )
            await self.message.edit(embed=timeout_embed)
            
            # إعادة إنشاء القائمة بعد فترة
            await asyncio.sleep(3)
            await self.show_menu("economy")
            
    async def _language_settings(self, interaction):
        """إعدادات اللغة"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.response.defer()
        await self.message.delete()
        
        # تنفيذ أمر اللغة
        language_command = self.bot.get_command('لغة') or self.bot.get_command('language')
        if language_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(language_command)
        else:
            msg = "عذراً، أمر إعدادات اللغة غير متاح حالياً." if self.language == "ar" else "Sorry, the language settings command is not available."
            await interaction.followup.send(msg)
            
    async def _play_fishing(self, interaction):
        """لعب لعبة الصيد"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.response.defer()
        await self.message.delete()
        
        # تنفيذ أمر الصيد
        fishing_command = self.bot.get_command('صيد') or self.bot.get_command('fish')
        if fishing_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(fishing_command)
        else:
            msg = "عذراً، لعبة الصيد غير متاحة حالياً." if self.language == "ar" else "Sorry, the fishing game is not available."
            await interaction.followup.send(msg)
            
    async def _play_dice(self, interaction):
        """لعب لعبة النرد"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.response.defer()
        await self.message.delete()
        
        # تنفيذ أمر النرد
        dice_command = self.bot.get_command('نرد') or self.bot.get_command('dice')
        if dice_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(dice_command)
        else:
            msg = "عذراً، لعبة النرد غير متاحة حالياً." if self.language == "ar" else "Sorry, the dice game is not available."
            await interaction.followup.send(msg)

class MainMenu(commands.Cog):
    """أوامر القوائم الرئيسية"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name="قائمة",
        aliases=["menu", "م", "h"],
        description="فتح القائمة الرئيسية للبوت"
    )
    async def menu(self, ctx):
        """فتح القائمة الرئيسية التفاعلية للبوت"""
        # إنشاء قائمة تنقل
        nav_view = NavigationView(self.bot, ctx)
        
        # عرض القائمة الرئيسية
        await nav_view.show_menu("main")
    
    @commands.command(
        name="قائمة_شاملة",
        aliases=["m", "all", "شامل"],
        description="عرض قائمة شاملة تحتوي على جميع الأوامر الأساسية في صفحة واحدة"
    )
    async def all_in_one_menu(self, ctx):
        """عرض قائمة شاملة لجميع الأوامر الأساسية في صفحة واحدة"""
        # تحديد اللغة المستخدمة
        language = get_user_language(self.bot, ctx.author.id)
        
        # إنشاء رسالة مضمنة للقائمة الشاملة
        embed = discord.Embed(
            title="⚡ القائمة الشاملة" if language == "ar" else "⚡ Comprehensive Menu",
            description="جميع الأوامر الأساسية في مكان واحد!" if language == "ar" else "All essential commands in one place!",
            color=discord.Color.purple()
        )
        
        # إضافة قسم الموسيقى
        embed.add_field(
            name="🎵 أوامر الموسيقى" if language == "ar" else "🎵 Music Commands",
            value="**!تشغيل** أو **!p** + رابط/اسم: تشغيل موسيقى\n"
                 "**!إيقاف** أو **!s**: إيقاف الموسيقى\n"
                 "**!تخطي** أو **!sk**: تخطي الأغنية الحالية\n"
                 "**!صوت** أو **!v** + رقم: ضبط مستوى الصوت\n"
                 "**!بحث** أو **!search** + كلمة: البحث عن أغنية" if language == "ar" else 
                 "**!play** or **!p** + link/name: Play music\n"
                 "**!stop** or **!s**: Stop music\n"
                 "**!skip** or **!sk**: Skip current song\n"
                 "**!volume** or **!v** + number: Adjust volume\n"
                 "**!search** + term: Search for a song",
            inline=False
        )
        
        # إضافة قسم البنك
        embed.add_field(
            name="💰 أوامر البنك" if language == "ar" else "💰 Bank Commands",
            value="**!رصيد** أو **!balance**: عرض رصيدك\n"
                 "**!يومي** أو **!daily**: المكافأة اليومية\n"
                 "**!تحويل** أو **!transfer**: تحويل أموال\n"
                 "**!حماية** أو **!protection**: حماية من السرقة\n"
                 "**!سرقة** أو **!steal**: محاولة سرقة شخص آخر" if language == "ar" else 
                 "**!balance**: View your balance\n"
                 "**!daily**: Get daily reward\n"
                 "**!transfer**: Transfer money\n"
                 "**!protection**: Protect from stealing\n"
                 "**!steal**: Try to steal from someone",
            inline=False
        )
        
        # إضافة قسم الألعاب
        embed.add_field(
            name="🎮 أوامر الألعاب" if language == "ar" else "🎮 Game Commands",
            value="**!صيد** أو **!fish**: لعبة الصيد\n"
                 "**!سباق** أو **!horserace**: سباق الخيول\n"
                 "**!نرد** أو **!dice**: لعبة النرد\n"
                 "**!بلاك_جاك** أو **!blackjack**: لعبة بلاك جاك" if language == "ar" else 
                 "**!fish**: Fishing game\n"
                 "**!horserace**: Horse racing\n"
                 "**!dice**: Dice game\n"
                 "**!blackjack**: Blackjack game",
            inline=False
        )
        
        # إضافة قسم الدعوات
        embed.add_field(
            name="🔗 أوامر الدعوات" if language == "ar" else "🔗 Invite Commands",
            value="**!دعوة** أو **!invite** + رابط: الانضمام لرابط دعوة\n"
                 "**!إنشاء_دعوة** أو **!create_invite**: إنشاء رابط دعوة" if language == "ar" else 
                 "**!invite** + link: Join an invite link\n"
                 "**!create_invite**: Create an invite link",
            inline=False
        )
        
        # إضافة قسم الاختصارات
        embed.add_field(
            name="⚡ اختصارات سريعة" if language == "ar" else "⚡ Quick Shortcuts",
            value="**!h**: القائمة التفاعلية\n"
                 "**!m**: هذه القائمة الشاملة" if language == "ar" else 
                 "**!h**: Interactive menu\n"
                 "**!m**: This comprehensive menu",
            inline=False
        )
        
        # إضافة صورة البوت
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        # إضافة تذييل
        embed.set_footer(
            text="استخدم الأمر !h للقائمة التفاعلية الكاملة" if language == "ar" else "Use !h command for the full interactive menu"
        )
        
        # إرسال القائمة
        await ctx.send(embed=embed)

async def setup(bot):
    """إضافة الأمر للبوت"""
    await bot.add_cog(MainMenu(bot)) 