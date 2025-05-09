#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import os
import json
from pathlib import Path
from discord.ui import Button, View

# مسار ملف إعدادات اللغة
LANGUAGE_FILE = Path(__file__).parent.parent.parent / "data" / "language_settings.json"

# التأكد من وجود مجلد البيانات وإنشاء ملف إعدادات اللغة إذا لم يكن موجوداً
def ensure_language_file():
    """التأكد من وجود ملف إعدادات اللغة"""
    # إنشاء مجلد البيانات إذا لم يكن موجوداً
    data_dir = LANGUAGE_FILE.parent
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # إنشاء ملف إعدادات اللغة إذا لم يكن موجوداً
    if not LANGUAGE_FILE.exists():
        default_settings = {
            "default": "ar",  # اللغة الافتراضية هي العربية
            "users": {},      # إعدادات اللغة لكل مستخدم
            "servers": {}     # إعدادات اللغة لكل سيرفر
        }
        with open(LANGUAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(default_settings, f, ensure_ascii=False, indent=4)
    
    return True

# تحميل إعدادات اللغة
def load_language_settings():
    """تحميل إعدادات اللغة من الملف"""
    ensure_language_file()
    try:
        with open(LANGUAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"خطأ في تحميل إعدادات اللغة: {str(e)}")
        return {
            "default": "ar",
            "users": {},
            "servers": {}
        }

# حفظ إعدادات اللغة
def save_language_settings(settings):
    """حفظ إعدادات اللغة في الملف"""
    ensure_language_file()
    try:
        with open(LANGUAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"خطأ في حفظ إعدادات اللغة: {str(e)}")
        return False

# الحصول على لغة المستخدم
def get_user_language(user_id):
    """الحصول على لغة المستخدم المحددة"""
    settings = load_language_settings()
    return settings["users"].get(str(user_id), settings["default"])

# تحديث لغة المستخدم
def update_user_language(user_id, language):
    """تحديث لغة المستخدم"""
    settings = load_language_settings()
    settings["users"][str(user_id)] = language
    return save_language_settings(settings)

# فئة أزرار اختيار اللغة
class LanguageSelectView(View):
    """عرض أزرار اختيار اللغة"""
    
    def __init__(self, ctx, timeout=60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.selected_language = None
        self.return_to_menu = False
    
    @discord.ui.button(label="العربية", emoji="🇸🇦", style=discord.ButtonStyle.primary)
    async def arabic_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر اختيار اللغة العربية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الأزرار مخصصة لصاحب الأمر فقط.", ephemeral=True)
        
        # تحديث لغة المستخدم إلى العربية
        update_user_language(interaction.user.id, "ar")
        self.selected_language = "ar"
        
        embed = discord.Embed(
            title="✅ تم تغيير اللغة",
            description="تم تعيين لغة البوت إلى **العربية**",
            color=discord.Color.green()
        )
        embed.set_footer(text="سيتم استخدام اللغة العربية في جميع رسائل البوت")
        
        # إضافة زر العودة للقائمة
        back_button = Button(
            label="العودة للقائمة",
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            custom_id="return_to_menu"
        )
        back_button.callback = self.return_to_menu_callback
        
        # إنشاء عرض جديد يحتوي فقط على زر العودة
        return_view = View(timeout=60)
        return_view.add_item(back_button)
        
        await interaction.response.edit_message(embed=embed, view=return_view)
        self.stop()
    
    @discord.ui.button(label="English", emoji="🇬🇧", style=discord.ButtonStyle.primary)
    async def english_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر اختيار اللغة الإنجليزية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("This button is only for the command user.", ephemeral=True)
        
        # تحديث لغة المستخدم إلى الإنجليزية
        update_user_language(interaction.user.id, "en")
        self.selected_language = "en"
        
        embed = discord.Embed(
            title="✅ Language Changed",
            description="Bot language has been set to **English**",
            color=discord.Color.green()
        )
        embed.set_footer(text="English will be used in all bot messages")
        
        # إضافة زر العودة للقائمة
        back_button = Button(
            label="Return to Menu",
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            custom_id="return_to_menu"
        )
        back_button.callback = self.return_to_menu_callback
        
        # إنشاء عرض جديد يحتوي فقط على زر العودة
        return_view = View(timeout=60)
        return_view.add_item(back_button)
        
        await interaction.response.edit_message(embed=embed, view=return_view)
        self.stop()
    
    async def return_to_menu_callback(self, interaction):
        """الرجوع إلى القائمة الرئيسية"""
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if self.selected_language == "ar" else "These buttons are only for the command user."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        self.return_to_menu = True
        
        # تشغيل أمر القائمة
        menu_command = interaction.client.get_command("قائمة")
        if menu_command:
            await interaction.response.edit_message(content="⏳", embed=None, view=None)
            await self.ctx.invoke(menu_command)
        else:
            # إذا لم يتم العثور على أمر القائمة
            error_msg = "لم يتم العثور على أمر القائمة." if self.selected_language == "ar" else "Menu command not found."
            await interaction.response.edit_message(content=error_msg, embed=None, view=None)

class Language(commands.Cog):
    """أوامر إعدادات اللغة"""
    
    def __init__(self, bot):
        self.bot = bot
        # التأكد من وجود ملف إعدادات اللغة عند بدء تشغيل البوت
        ensure_language_file()
    
    @commands.command(
        name="لغة",
        aliases=["language", "lang", "لغه"],
        description="تغيير لغة البوت (عربي/إنجليزي)"
    )
    async def language(self, ctx):
        """
        تغيير لغة البوت بين العربية والإنجليزية
        """
        # الحصول على اللغة الحالية للمستخدم
        current_lang = get_user_language(ctx.author.id)
        
        # إنشاء رسالة مضمنة
        if current_lang == "ar":
            embed = discord.Embed(
                title="🌐 إعدادات اللغة",
                description="اختر لغة البوت المفضلة لديك من الخيارات أدناه.\nاللغة الحالية: **العربية** 🇸🇦",
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                title="🌐 Language Settings",
                description="Choose your preferred bot language from the options below.\nCurrent language: **English** 🇬🇧",
                color=discord.Color.blue()
            )
        
        # إنشاء عرض الأزرار
        view = LanguageSelectView(ctx)
        await ctx.send(embed=embed, view=view)
        
        # انتظار انتهاء العرض
        await view.wait()
        
        # العودة إلى القائمة الرئيسية إذا تم النقر على زر العودة
        if view.return_to_menu:
            menu_command = self.bot.get_command("قائمة")
            if menu_command:
                await ctx.invoke(menu_command)
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        """استمع لجميع الأوامر للتحقق من لغة المستخدم"""
        # يمكن استخدام هذا الحدث لتطبيق إعدادات اللغة على استجابات الأوامر
        # حاليًا لم يتم تنفيذ منطق متعدد اللغات لجميع الأوامر
        pass

async def setup(bot):
    """إعداد الصنف وإضافته إلى البوت"""
    await bot.add_cog(Language(bot)) 