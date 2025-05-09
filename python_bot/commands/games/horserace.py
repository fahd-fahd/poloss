#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import random
import asyncio
from discord.ui import Button, View
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

# الخيول المتاحة مع الرموز التعبيرية والألوان
HORSES = [
    {"name_ar": "البرق الأسود", "name_en": "Black Lightning", "emoji": "🐎", "color": discord.Color.dark_gray(), "position": 0},
    {"name_ar": "المهر الأبيض", "name_en": "White Stallion", "emoji": "🐗", "color": discord.Color.light_gray(), "position": 0},
    {"name_ar": "صقر الصحراء", "name_en": "Desert Falcon", "emoji": "🐕", "color": discord.Color.gold(), "position": 0},
    {"name_ar": "سريع الريح", "name_en": "Wind Racer", "emoji": "🐅", "color": discord.Color.blue(), "position": 0},
    {"name_ar": "وحش الليل", "name_en": "Night Beast", "emoji": "🦝", "color": discord.Color.purple(), "position": 0}
]

# طول مسار السباق
RACE_LENGTH = 15

# قيمة الرهان الافتراضية
DEFAULT_BET = 100

class HorseSelectionView(View):
    """منظر اختيار الخيل للمراهنة عليه"""
    
    def __init__(self, bot, ctx, bet_amount):
        super().__init__(timeout=30)
        self.bot = bot
        self.ctx = ctx
        self.bet_amount = bet_amount
        self.selected_horse = None
        
        # الحصول على لغة المستخدم
        self.language = get_user_language(bot, ctx.author.id)
        
        # إضافة زر لكل خيل
        for i, horse in enumerate(HORSES):
            horse_name = horse["name_ar"] if self.language == "ar" else horse["name_en"]
            btn = Button(
                label=horse_name,
                emoji=horse["emoji"],
                style=discord.ButtonStyle.primary,
                custom_id=str(i)
            )
            btn.callback = self.make_callback(i)
            self.add_item(btn)
        
        # إضافة زر إلغاء
        cancel_label = "إلغاء" if self.language == "ar" else "Cancel"
        cancel_btn = Button(
            label=cancel_label,
            emoji="❌",
            style=discord.ButtonStyle.danger,
            custom_id="cancel"
        )
        cancel_btn.callback = self.cancel_callback
        self.add_item(cancel_btn)
    
    def make_callback(self, horse_idx):
        """إنشاء رد فعل مخصص لكل زر"""
        async def callback(interaction):
            # التحقق من أن التفاعل من طالب اللعبة
            if interaction.user.id != self.ctx.author.id:
                error_msg = "هذه الأزرار مخصصة لصاحب الرهان فقط." if self.language == "ar" else "These buttons are only for the bet owner."
                return await interaction.response.send_message(error_msg, ephemeral=True)
            
            self.selected_horse = horse_idx
            self.stop()
            
            horse_name = HORSES[horse_idx]["name_ar"] if self.language == "ar" else HORSES[horse_idx]["name_en"]
            
            if self.language == "ar":
                content = f"**تم اختيار**: {HORSES[horse_idx]['emoji']} {horse_name} | **قيمة الرهان**: {self.bet_amount} 🪙"
            else:
                content = f"**Selected**: {HORSES[horse_idx]['emoji']} {horse_name} | **Bet Amount**: {self.bet_amount} 🪙"
                
            await interaction.response.edit_message(
                content=content,
                view=None
            )
        
        return callback
    
    async def cancel_callback(self, interaction):
        """رد فعل زر الإلغاء"""
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب الرهان فقط." if self.language == "ar" else "These buttons are only for the bet owner."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # إلغاء السباق
        cancel_msg = "🚫 تم إلغاء السباق." if self.language == "ar" else "🚫 Race cancelled."
        await interaction.response.edit_message(content=cancel_msg, embed=None, view=None)
        
        # العودة إلى القائمة الرئيسية
        menu_command = self.bot.get_command("قائمة")
        if menu_command:
            await asyncio.sleep(1)
            await self.ctx.invoke(menu_command)
        
        self.stop()

class RaceResultView(View):
    """منظر نتيجة السباق مع زر للعودة للقائمة"""
    
    def __init__(self, bot, ctx, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
        self.language = get_user_language(bot, ctx.author.id)
        
        # إضافة زر للعب مرة أخرى
        play_again_label = "لعب مرة أخرى" if self.language == "ar" else "Play Again"
        play_again_btn = Button(
            label=play_again_label,
            emoji="🔄",
            style=discord.ButtonStyle.primary,
            custom_id="play_again"
        )
        play_again_btn.callback = self.play_again_callback
        self.add_item(play_again_btn)
        
        # إضافة زر للعودة للقائمة
        menu_label = "العودة للقائمة" if self.language == "ar" else "Back to Menu"
        menu_btn = Button(
            label=menu_label,
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            custom_id="back_to_menu"
        )
        menu_btn.callback = self.menu_callback
        self.add_item(menu_btn)
    
    async def play_again_callback(self, interaction):
        """رد فعل زر اللعب مرة أخرى"""
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب اللعبة فقط." if self.language == "ar" else "These buttons are only for the game owner."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # تشغيل أمر سباق الخيل مرة أخرى
        race_command = self.bot.get_command("سباق_الخيل")
        if race_command:
            await interaction.response.edit_message(content="⏳", embed=None, view=None)
            await self.ctx.invoke(race_command)
        
        self.stop()
    
    async def menu_callback(self, interaction):
        """رد فعل زر العودة للقائمة"""
        if interaction.user.id != self.ctx.author.id:
            error_msg = "هذه الأزرار مخصصة لصاحب اللعبة فقط." if self.language == "ar" else "These buttons are only for the game owner."
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        # تشغيل أمر القائمة
        menu_command = self.bot.get_command("قائمة")
        if menu_command:
            await interaction.response.edit_message(content="⏳", embed=None, view=None)
            await self.ctx.invoke(menu_command)
        
        self.stop()

class HorseRace(commands.Cog):
    """نظام لعبة سباق الخيل"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_races = {}  # تخزين السباقات النشطة
        
    @commands.command(
        name="سباق_الخيل",
        aliases=["خيل", "سباق", "horserace", "race"],
        description="لعبة سباق الخيل"
    )
    async def horse_race(self, ctx, bet: int = DEFAULT_BET):
        """
        لعبة سباق الخيل - اختر خيلاً وراهن عليه للفوز
        
        المعلمات:
            bet (int): قيمة الرهان (اختياري، الافتراضي: 100)
        
        أمثلة:
            !سباق_الخيل
            !خيل 500
        """
        # الحصول على لغة المستخدم
        language = get_user_language(self.bot, ctx.author.id)
        
        # التحقق من وجود سباق نشط بالفعل في هذه القناة
        if ctx.channel.id in self.active_races:
            if language == "ar":
                embed = discord.Embed(
                    title="⏳ سباق جارٍ",
                    description="يوجد بالفعل سباق نشط في هذه القناة. انتظر حتى ينتهي.",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="⏳ Race in Progress",
                    description="There is already an active race in this channel. Wait until it finishes.",
                    color=discord.Color.red()
                )
            return await ctx.send(embed=embed)
        
        # التحقق من صحة قيمة الرهان
        if bet < 1:
            if language == "ar":
                embed = discord.Embed(
                    title="❌ قيمة رهان غير صالحة",
                    description="يجب أن تكون قيمة الرهان أكبر من الصفر.",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="❌ Invalid Bet Value",
                    description="Bet amount must be greater than zero.",
                    color=discord.Color.red()
                )
            return await ctx.send(embed=embed)
        
        # التحقق من أن المستخدم لديه رصيد كافٍ
        if hasattr(self.bot, 'db'):
            # جلب رصيد اللاعب من قاعدة البيانات
            users_collection = self.bot.db.users
            user_data = await users_collection.find_one({"user_id": ctx.author.id})
            
            if user_data is None or user_data.get("balance", 0) < bet:
                if language == "ar":
                    embed = discord.Embed(
                        title="❌ رصيد غير كافٍ",
                        description=f"ليس لديك رصيد كافٍ للمراهنة بـ {bet} 🪙",
                        color=discord.Color.red()
                    )
                else:
                    embed = discord.Embed(
                        title="❌ Insufficient Balance",
                        description=f"You don't have enough balance to bet {bet} 🪙",
                        color=discord.Color.red()
                    )
                return await ctx.send(embed=embed)
        
        # إظهار قائمة الخيول للاختيار منها
        if language == "ar":
            embed = discord.Embed(
                title="🏇 سباق الخيل",
                description=f"اختر خيلاً للمراهنة عليه بمبلغ {bet} 🪙",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="🏇 Horse Race",
                description=f"Choose a horse to bet on with {bet} 🪙",
                color=discord.Color.green()
            )
        
        for horse in HORSES:
            horse_name = horse["name_ar"] if language == "ar" else horse["name_en"]
            value_text = "سرعة مختلفة وحظ مختلف" if language == "ar" else "Different speed and luck"
            
            embed.add_field(
                name=f"{horse['emoji']} {horse_name}",
                value=value_text,
                inline=True
            )
        
        # إنشاء منظر الاختيار
        view = HorseSelectionView(self.bot, ctx, bet)
        selection_message = await ctx.send(embed=embed, view=view)
        
        # انتظار اختيار اللاعب
        await view.wait()
        
        # التحقق من انتهاء مهلة الاختيار
        if view.selected_horse is None:
            # تم إلغاء السباق أو انتهت المهلة
            if selection_message:
                timeout_msg = "⏰ انتهت مهلة الاختيار. تم إلغاء السباق." if language == "ar" else "⏰ Selection timed out. Race cancelled."
                await selection_message.edit(
                    content=timeout_msg,
                    embed=None,
                    view=None
                )
            return
        
        # خصم الرهان من رصيد اللاعب
        if hasattr(self.bot, 'db'):
            await users_collection.update_one(
                {"user_id": ctx.author.id},
                {"$inc": {"balance": -bet}}
            )
        
        # تسجيل هذه القناة كسباق نشط
        self.active_races[ctx.channel.id] = True
        
        # إعادة تعيين مواقع الخيول
        for horse in HORSES:
            horse["position"] = 0
        
        # إنشاء رسالة السباق
        race_start_msg = "🏁 السباق يبدأ..." if language == "ar" else "🏁 Race is starting..."
        race_message = await ctx.send(race_start_msg)
        
        # العد التنازلي للبدء
        for i in range(3, 0, -1):
            countdown_msg = f"🏁 السباق يبدأ في {i}..." if language == "ar" else f"🏁 Race starts in {i}..."
            await race_message.edit(content=countdown_msg)
            await asyncio.sleep(1)
        
        go_msg = "🏁 انطلق!" if language == "ar" else "🏁 GO!"
        await race_message.edit(content=go_msg)
        
        # بدء عملية السباق
        selected_horse_idx = view.selected_horse
        selected_horse = HORSES[selected_horse_idx]
        
        race_finished = False
        winner = None
        
        # حلقة السباق الرئيسية
        while not race_finished:
            await asyncio.sleep(1)  # تأخير بين الجولات
            
            # تحديث مواقع الخيول
            for i, horse in enumerate(HORSES):
                # احتمالية تحرك كل خيل تعتمد على عوامل عشوائية
                move_chance = random.randint(0, 100)
                
                if move_chance < 80:  # احتمالية 80% للتحرك
                    # تحديد طول القفزة (1-3 خطوات)
                    move_steps = random.randint(1, 3)
                    horse["position"] += move_steps
                
                # التحقق من وصول أي خيل لخط النهاية
                if horse["position"] >= RACE_LENGTH:
                    race_finished = True
                    winner = i
                    horse["position"] = RACE_LENGTH  # تأكد من عدم تجاوز النهاية
            
            # عرض حالة السباق الحالية
            race_status = self._generate_race_track(language)
            await race_message.edit(content=race_status)
        
        # إعلان الفائز
        winning_horse = HORSES[winner]
        winning_horse_name = winning_horse["name_ar"] if language == "ar" else winning_horse["name_en"]
        
        if language == "ar":
            result_embed = discord.Embed(
                title="🏆 نتيجة السباق",
                description=f"الفائز هو: {winning_horse['emoji']} **{winning_horse_name}**!",
                color=winning_horse["color"]
            )
        else:
            result_embed = discord.Embed(
                title="🏆 Race Result",
                description=f"The winner is: {winning_horse['emoji']} **{winning_horse_name}**!",
                color=winning_horse["color"]
            )
        
        # التحقق من فوز اللاعب
        if winner == selected_horse_idx:
            # اللاعب فاز - إضافة الجائزة
            winnings = bet * 2  # مضاعفة الرهان
            
            if language == "ar":
                result_embed.add_field(
                    name="🎉 مبروك!",
                    value=f"{ctx.author.mention} لقد فاز خيلك! 🥇\nربحت {winnings} 🪙",
                    inline=False
                )
            else:
                result_embed.add_field(
                    name="🎉 Congratulations!",
                    value=f"{ctx.author.mention} your horse won! 🥇\nYou won {winnings} 🪙",
                    inline=False
                )
            
            # إضافة المكافأة إلى رصيد اللاعب
            if hasattr(self.bot, 'db'):
                await users_collection.update_one(
                    {"user_id": ctx.author.id},
                    {"$inc": {"balance": winnings}}
                )
        else:
            # اللاعب خسر
            selected_horse_name = selected_horse["name_ar"] if language == "ar" else selected_horse["name_en"]
            
            if language == "ar":
                result_embed.add_field(
                    name="😔 للأسف",
                    value=f"{ctx.author.mention} خسر خيلك {selected_horse['emoji']} **{selected_horse_name}** السباق.\nخسرت رهانك البالغ {bet} 🪙",
                    inline=False
                )
            else:
                result_embed.add_field(
                    name="😔 Sorry",
                    value=f"{ctx.author.mention} your horse {selected_horse['emoji']} **{selected_horse_name}** lost the race.\nYou lost your bet of {bet} 🪙",
                    inline=False
                )
        
        # إضافة ترتيب جميع الخيول
        # ترتيب الخيول حسب موضعها النهائي
        sorted_horses = sorted(enumerate(HORSES), key=lambda x: x[1]["position"], reverse=True)
        
        ranking = ""
        for rank, (idx, horse) in enumerate(sorted_horses, 1):
            position = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
            selected = " ⭐" if idx == selected_horse_idx else ""
            horse_name = horse["name_ar"] if language == "ar" else horse["name_en"]
            ranking += f"{position} {horse['emoji']} **{horse_name}**{selected}\n"
        
        if language == "ar":
            result_embed.add_field(name="🏁 الترتيب النهائي", value=ranking, inline=False)
        else:
            result_embed.add_field(name="🏁 Final Ranking", value=ranking, inline=False)
        
        # إنشاء منظر النتيجة مع أزرار
        result_view = RaceResultView(self.bot, ctx)
        await ctx.send(embed=result_embed, view=result_view)
        
        # إزالة السباق من القائمة النشطة
        del self.active_races[ctx.channel.id]
    
    def _generate_race_track(self, language="ar"):
        """توليد شاشة عرض لمضمار السباق"""
        track = []
        
        # إنشاء مضمار السباق لكل خيل
        for horse in HORSES:
            # خط السباق مع موضع الخيل
            position = horse["position"]
            track_line = "🏁" + "▫️" * (RACE_LENGTH - 1) + "🏁"
            
            # وضع الخيل في موضعه الحالي
            if position < RACE_LENGTH:
                track_line = track_line[:position] + horse["emoji"] + track_line[position+1:]
            else:
                # الخيل وصل للنهاية
                track_line = track_line[:-1] + horse["emoji"]
            
            # اسم الخيل حسب اللغة
            horse_name = horse["name_ar"] if language == "ar" else horse["name_en"]
            track.append(f"{horse_name}: {track_line}")
        
        return "\n".join(track)
    
    @commands.command(
        name="احصائيات_الخيل",
        aliases=["horse_stats", "خيول", "horses"],
        description="عرض إحصائيات خيول السباق"
    )
    async def horse_stats(self, ctx):
        """عرض معلومات وإحصائيات خيول السباق"""
        # الحصول على لغة المستخدم
        language = get_user_language(self.bot, ctx.author.id)
        
        if language == "ar":
            embed = discord.Embed(
                title="🏇 إحصائيات خيول السباق",
                description="معلومات عن الخيول المتاحة للسباق",
                color=discord.Color.gold()
            )
        else:
            embed = discord.Embed(
                title="🏇 Horse Statistics",
                description="Information about available race horses",
                color=discord.Color.gold()
            )
        
        # القيم حسب اللغة
        speeds_ar = ["سريع جداً", "متوسط السرعة", "سرعة عالية", "قوي البنية", "خفيف الحركة"]
        speeds_en = ["Very Fast", "Medium Speed", "High Speed", "Strong Build", "Light Movement"]
        
        origins_ar = ["من أصول عربية", "من سلالة ملكية", "من الصحراء", "مدرب تدريباً عالياً", "فائز بعدة سباقات"]
        origins_en = ["Arabian Origin", "Royal Breed", "From the Desert", "Highly Trained", "Multiple Race Winner"]
        
        for horse in HORSES:
            # اختيار القيم العشوائية
            speed_index = random.randint(0, len(speeds_ar) - 1)
            origin_index = random.randint(0, len(origins_ar) - 1)
            
            speed = speeds_ar[speed_index] if language == "ar" else speeds_en[speed_index]
            origin = origins_ar[origin_index] if language == "ar" else origins_en[origin_index]
            
            # الاسم حسب اللغة
            horse_name = horse["name_ar"] if language == "ar" else horse["name_en"]
            
            # التنسيق حسب اللغة
            if language == "ar":
                embed.add_field(
                    name=f"{horse['emoji']} {horse_name}",
                    value=f"**المميزات**: {speed}، {origin}\n**اللون**: {self._translate_color(horse['color'].name, 'ar')}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{horse['emoji']} {horse_name}",
                    value=f"**Features**: {speed}, {origin}\n**Color**: {self._translate_color(horse['color'].name, 'en')}",
                    inline=False
                )
        
        # إضافة زر للعودة إلى القائمة
        menu_label = "العودة للقائمة" if language == "ar" else "Back to Menu"
        menu_view = View(timeout=60)
        menu_btn = Button(
            label=menu_label,
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            custom_id="back_to_menu"
        )
        
        async def menu_callback(interaction):
            if interaction.user.id != ctx.author.id:
                error_msg = "هذه الأزرار مخصصة لصاحب الأمر فقط." if language == "ar" else "These buttons are only for the command user."
                return await interaction.response.send_message(error_msg, ephemeral=True)
            
            # تشغيل أمر القائمة
            menu_command = self.bot.get_command("قائمة")
            if menu_command:
                await interaction.response.edit_message(content="⏳", embed=None, view=None)
                await ctx.invoke(menu_command)
        
        menu_btn.callback = menu_callback
        menu_view.add_item(menu_btn)
        
        await ctx.send(embed=embed, view=menu_view)
    
    def _translate_color(self, color_name, language):
        """ترجمة اسم اللون"""
        color_translations = {
            "dark_gray": {"ar": "رمادي داكن", "en": "Dark Gray"},
            "light_gray": {"ar": "رمادي فاتح", "en": "Light Gray"},
            "gold": {"ar": "ذهبي", "en": "Gold"},
            "blue": {"ar": "أزرق", "en": "Blue"},
            "purple": {"ar": "أرجواني", "en": "Purple"},
            "green": {"ar": "أخضر", "en": "Green"},
            "red": {"ar": "أحمر", "en": "Red"}
        }
        
        color_name = color_name.lower().replace("_", " ")
        for key, translations in color_translations.items():
            if key in color_name:
                return translations[language]
        
        return color_name.title()

async def setup(bot):
    """إعداد الصنف وإضافته إلى البوت"""
    await bot.add_cog(HorseRace(bot)) 