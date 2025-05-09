#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import random
import asyncio
import datetime

class Slots(commands.Cog):
    """لعبة آلات القمار (سلوتس)"""
    
    def __init__(self, bot):
        self.bot = bot
        self.currency_emoji = self.bot.config.get('bank', {}).get('currencyEmoji', '💰')
        self.min_bet = self.bot.config.get('games', {}).get('minBet', 10)
        self.max_bet = self.bot.config.get('games', {}).get('maxBet', 10000)
        
        # رموز السلوتس
        self.slots_emojis = [
            "🍒", "🍊", "🍋", "🍇", "🍉", "🍓", "🍎", "🎰", "💎", "🌟"
        ]
        
        # معدلات الفوز
        self.win_rates = {
            3: 5,    # ثلاثة رموز متطابقة تعطي 5 أضعاف
            2: 2,    # رمزان متطابقان يعطيان ضعف المبلغ
            "jackpot": 10  # الجاكبوت (ثلاث ماسات أو نجوم) يعطي 10 أضعاف
        }
        
        # رموز الجاكبوت
        self.jackpot_symbols = ["💎", "🌟", "🎰"]
    
    @commands.command(
        name="سلوتس",
        aliases=["slots", "slot", "سلوت"],
        description="لعبة آلات القمار للمراهنة"
    )
    async def slots(self, ctx, amount: str = None):
        """
        لعبة آلات القمار (سلوتس) للمراهنة
        
        المعلمات:
            amount (str): المبلغ الذي تريد المراهنة عليه
        
        أمثلة:
            !سلوتس 100
            !سلوتس كل
            !slots 500
            !slot all
        """
        # التحقق من المبلغ
        if not amount:
            embed = discord.Embed(
                title="❌ خطأ في الأمر",
                description=f"يجب عليك تحديد المبلغ للمراهنة.\n"
                            f"مثال: `!سلوتس 100` أو `!سلوتس كل`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # تحويل المبلغ
        try:
            if amount.lower() in ['all', 'كل', 'الكل']:
                # الحصول على رصيد المستخدم
                user_data = await self._get_user_data(ctx.author.id)
                bet_amount = user_data['balance']
            else:
                # تحويل المبلغ إلى رقم
                bet_amount = int(amount.replace(',', '').strip())
        except ValueError:
            embed = discord.Embed(
                title="❌ خطأ في المبلغ",
                description=f"يرجى إدخال مبلغ صالح للمراهنة.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من صحة المبلغ
        if bet_amount < self.min_bet:
            embed = discord.Embed(
                title="❌ خطأ في المبلغ",
                description=f"الحد الأدنى للمراهنة هو {self.min_bet} {self.currency_emoji}.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        if bet_amount > self.max_bet:
            embed = discord.Embed(
                title="❌ خطأ في المبلغ",
                description=f"الحد الأقصى للمراهنة هو {self.max_bet} {self.currency_emoji}.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من رصيد المستخدم
        user_data = await self._get_user_data(ctx.author.id)
        if user_data['balance'] < bet_amount:
            embed = discord.Embed(
                title="❌ رصيد غير كافٍ",
                description=f"ليس لديك رصيد كافٍ للمراهنة بهذا المبلغ.\n"
                            f"رصيدك الحالي: **{user_data['balance']:,}** {self.currency_emoji}",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # بدء اللعبة
        embed = discord.Embed(
            title="🎰 آلة القمار",
            description=f"{ctx.author.mention} يقوم بتشغيل آلة القمار...\n"
                        f"الرهان: **{bet_amount:,}** {self.currency_emoji}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        message = await ctx.send(embed=embed)
        
        # تأخير للتشويق
        await asyncio.sleep(1)
        
        # دوران الآلة
        slots = []
        for i in range(3):
            # إنشاء مصفوفة من الرموز العشوائية
            # حيث الرموز الأعلى قيمة (جاكبوت) لها احتمالية أقل
            if random.random() < 0.1:  # 10% فرصة للحصول على رمز جاكبوت
                symbol = random.choice(self.jackpot_symbols)
            else:
                symbol = random.choice(self.slots_emojis[:7])  # اختيار من الرموز العادية فقط
            
            slots.append(symbol)
            
            # تحديث الرسالة لإظهار دوران تدريجي
            current_slots = ' | '.join([s if idx <= i else "❓" for idx, s in enumerate(slots + ["❓"] * (3 - len(slots)))])
            embed.description = f"{ctx.author.mention} يقوم بتشغيل آلة القمار...\n" \
                               f"الرهان: **{bet_amount:,}** {self.currency_emoji}\n\n" \
                               f"[ {current_slots} ]"
            await message.edit(embed=embed)
            await asyncio.sleep(0.7)
        
        # تحديد النتيجة
        result_line = ' | '.join(slots)
        
        # حساب الجائزة
        multiplier = 0
        winnings = 0
        
        # تحقق من الجاكبوت (ثلاثة رموز جاكبوت)
        if all(symbol in self.jackpot_symbols for symbol in slots):
            multiplier = self.win_rates["jackpot"]
            result_message = f"🎊 **جاكبوت!** لقد ربحت **{multiplier}×** المبلغ!"
            color = discord.Color.gold()
        
        # تحقق من الثلاثة المتطابقة
        elif slots[0] == slots[1] == slots[2]:
            multiplier = self.win_rates[3]
            result_message = f"🎉 **ثلاثة متطابقة!** لقد ربحت **{multiplier}×** المبلغ!"
            color = discord.Color.green()
        
        # تحقق من اثنين متطابقين
        elif slots[0] == slots[1] or slots[1] == slots[2] or slots[0] == slots[2]:
            multiplier = self.win_rates[2]
            result_message = f"🙂 **اثنان متطابقان!** لقد ربحت **{multiplier}×** المبلغ!"
            color = discord.Color.green()
        
        # لا يوجد تطابق
        else:
            result_message = f"😔 لا يوجد تطابق. لقد خسرت **{bet_amount:,}** {self.currency_emoji}"
            color = discord.Color.red()
        
        # حساب المبلغ النهائي
        if multiplier > 0:
            winnings = bet_amount * multiplier
            new_balance = user_data['balance'] + winnings - bet_amount
        else:
            winnings = 0
            new_balance = user_data['balance'] - bet_amount
        
        # تحديث قاعدة البيانات
        if hasattr(self.bot, 'db'):
            await self.bot.db.users.update_one(
                {"user_id": ctx.author.id},
                {"$set": {"balance": new_balance}}
            )
        
        # إظهار النتيجة النهائية
        result_description = f"{ctx.author.mention} قام بتشغيل آلة القمار...\n" \
                            f"الرهان: **{bet_amount:,}** {self.currency_emoji}\n\n" \
                            f"[ {result_line} ]\n\n" \
                            f"{result_message}"
        
        if multiplier > 0:
            result_description += f"\nلقد ربحت: **{winnings:,}** {self.currency_emoji}"
        
        embed = discord.Embed(
            title="🎰 نتيجة آلة القمار",
            description=result_description,
            color=color
        )
        
        embed.add_field(
            name="💳 رصيدك الحالي",
            value=f"**{new_balance:,}** {self.currency_emoji}",
            inline=True
        )
        
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await message.edit(embed=embed)
    
    async def _get_user_data(self, user_id):
        """
        الحصول على بيانات المستخدم من قاعدة البيانات
        
        المعلمات:
            user_id (int): معرف المستخدم
            
        Returns:
            dict: بيانات المستخدم
        """
        # التحقق من وجود قاعدة بيانات
        if not hasattr(self.bot, 'db'):
            # إذا لم تكن هناك قاعدة بيانات، أرجع بيانات افتراضية
            return {
                'user_id': user_id,
                'balance': self.bot.config.get('bank', {}).get('initialBalance', 1000),
                'bank_profile': {
                    'level': 1,
                    'daily': {
                        'last_claim': None,
                        'streak': 0
                    }
                },
                'created_at': datetime.datetime.utcnow().isoformat()
            }
        
        # البحث عن المستخدم في قاعدة البيانات
        users_collection = self.bot.db.users
        user_data = await users_collection.find_one({'user_id': user_id})
        
        # إذا لم يتم العثور على المستخدم، قم بإنشاء سجل جديد
        if not user_data:
            user_data = {
                'user_id': user_id,
                'balance': self.bot.config.get('bank', {}).get('initialBalance', 1000),
                'bank_profile': {
                    'level': 1,
                    'daily': {
                        'last_claim': None,
                        'streak': 0
                    }
                },
                'created_at': datetime.datetime.utcnow().isoformat()
            }
            # حفظ البيانات الجديدة في قاعدة البيانات
            await users_collection.insert_one(user_data)
        
        return user_data

async def setup(bot):
    """إعداد الأمر وإضافته إلى البوت"""
    await bot.add_cog(Slots(bot)) 