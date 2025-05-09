#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
from pathlib import Path
import sys

# إضافة مسار البوت إلى مسار البحث
sys.path.append(str(Path(__file__).parent.parent.parent))

# استيراد نظام القائمة
from utils.menu import NavigationView

# استيراد وحدة الترجمة
try:
    from utils.translator import get_user_language, t
except ImportError:
    # دالة مؤقتة في حالة عدم وجود وحدة الترجمة
    def get_user_language(bot, user_id):
        return "ar"
    
    def t(key, language="ar"):
        return key

class BotMenu(commands.Cog):
    """أوامر القائمة الرئيسية للبوت"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name="قائمة",
        aliases=["menu", "م", "قائمه", "m"],
        description="فتح القائمة الرئيسية للبوت"
    )
    async def menu(self, ctx):
        """
        فتح القائمة الرئيسية للبوت مع أزرار التنقل
        
        أمثلة:
            !قائمة
            !م
            !menu
        """
        # الحصول على لغة المستخدم
        language = get_user_language(self.bot, ctx.author.id)
        
        # إنشاء منظر القائمة
        view = NavigationView(self.bot, ctx)
        # عرض القائمة الرئيسية
        await view.show_menu("main")
    
    @commands.command(
        name="الألعاب",
        aliases=["games", "العاب", "g", "ج"],
        description="فتح قائمة الألعاب"
    )
    async def games_menu(self, ctx):
        """فتح قائمة الألعاب مباشرة"""
        # إنشاء منظر القائمة
        view = NavigationView(self.bot, ctx)
        # عرض قائمة الألعاب
        await view.show_menu("games")
    
    @commands.command(
        name="الموسيقى",
        aliases=["music", "موسيقى", "اغاني", "أغاني"],
        description="فتح قائمة الموسيقى"
    )
    async def music_menu(self, ctx):
        """فتح قائمة الموسيقى مباشرة"""
        # إنشاء منظر القائمة
        view = NavigationView(self.bot, ctx)
        # عرض قائمة الموسيقى
        await view.show_menu("music")
    
    @commands.command(
        name="الإعدادات",
        aliases=["settings", "اعدادات", "إعدادات", "الاعدادات"],
        description="فتح قائمة الإعدادات"
    )
    async def settings_menu(self, ctx):
        """فتح قائمة الإعدادات مباشرة"""
        # إنشاء منظر القائمة
        view = NavigationView(self.bot, ctx)
        # عرض قائمة الإعدادات
        await view.show_menu("settings")

async def setup(bot):
    """إعداد الصنف وإضافته إلى البوت"""
    await bot.add_cog(BotMenu(bot)) 