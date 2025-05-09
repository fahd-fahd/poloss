#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import random
import asyncio
import datetime

class Dice(commands.Cog):
    """لعبة النرد (الزهر)"""
    
    def __init__(self, bot):
        self.bot = bot
        self.currency_emoji = self.bot.config.get('bank', {}).get('currencyEmoji', '💰')
        self.min_bet = self.bot.config.get('games', {}).get('minBet', 10)
        self.max_bet = self.bot.config.get('games', {}).get('maxBet', 10000)
        
        # رموز النرد
        self.dice_emojis = {
            1: "⚀",
            2: "⚁",
            3: "⚂",
            4: "⚃",
            5: "⚄",
            6: "⚅"
        }
    
    @commands.command(
        name="نرد",
        aliases=["dice", "roll", "زهر", "رمي_النرد"],
        description="لعبة النرد للمراهنة"
    )
    async def dice(self, ctx, choice: str = None, amount: str = None):
        """
        لعبة النرد (الزهر) للمراهنة
        
        المعلمات:
            choice (str): نوع الرهان: 'عالي'/'high'/'h' أو 'منخفض'/'low'/'l' أو رقم محدد من 1-6
            amount (str): المبلغ الذي تريد المراهنة عليه
        
        أمثلة:
            !نرد عالي 100
            !نرد منخفض 200
            !نرد 6 300
            !dice high 100
            !dice low 200
            !roll 5 300
        """
        # التحقق من المعلمات
        if not choice or not amount:
            embed = discord.Embed(
                title="❌ خطأ في الأمر",
                description=f"يجب عليك تحديد نوع الرهان والمبلغ.\n"
                            f"مثال: `!نرد عالي 100` أو `!نرد 6 200`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # تحويل الاختيار إلى تنسيق موحد
        if choice.lower() in ["عالي", "high", "h", "ع"]:
            bet_type = "high"  # رهان على الأرقام العالية (4-6)
            bet_name = "عالي (4-6) 🎲"
        elif choice.lower() in ["منخفض", "low", "l", "م"]:
            bet_type = "low"  # رهان على الأرقام المنخفضة (1-3)
            bet_name = "منخفض (1-3) 🎲"
        elif choice.isdigit() and 1 <= int(choice) <= 6:
            bet_type = int(choice)  # رهان على رقم محدد
            bet_name = f"الرقم {bet_type} {self.dice_emojis[bet_type]}"
        else:
            embed = discord.Embed(
                title="❌ خطأ في الاختيار",
                description=f"يجب اختيار `عالي` أو `منخفض` أو رقم محدد بين 1 و 6.",
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
        
        # رمي النرد
        embed = discord.Embed(
            title="🎲 لعبة النرد",
            description=f"{ctx.author.mention} يرمي النرد...\n"
                        f"الرهان على: **{bet_name}**\n"
                        f"المبلغ: **{bet_amount:,}** {self.currency_emoji}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        message = await ctx.send(embed=embed)
        
        # تأخير لإضافة التشويق
        await asyncio.sleep(2)
        
        # رمي النرد
        dice_result = random.randint(1, 6)
        dice_emoji = self.dice_emojis[dice_result]
        
        # تحديد النتيجة
        won = False
        
        # التحقق من نوع الرهان
        if bet_type == "high":
            # إذا كان الرهان على الأرقام العالية (4-6)
            multiplier = 2
            won = dice_result >= 4
        elif bet_type == "low":
            # إذا كان الرهان على الأرقام المنخفضة (1-3)
            multiplier = 2
            won = dice_result <= 3
        else:
            # إذا كان الرهان على رقم محدد
            multiplier = 6
            won = dice_result == bet_type
        
        # حساب النتيجة النهائية
        if won:
            winnings = bet_amount * multiplier
            new_balance = user_data['balance'] + (winnings - bet_amount)
            result_text = f"🎉 مبروك! لقد ربحت **{winnings:,}** {self.currency_emoji}"
            color = discord.Color.green()
        else:
            winnings = 0
            new_balance = user_data['balance'] - bet_amount
            result_text = f"😔 للأسف، لقد خسرت **{bet_amount:,}** {self.currency_emoji}"
            color = discord.Color.red()
        
        # تحديث قاعدة البيانات
        if hasattr(self.bot, 'db'):
            await self.bot.db.users.update_one(
                {"user_id": ctx.author.id},
                {"$set": {"balance": new_balance}}
            )
        
        # تحديث الرسالة
        embed = discord.Embed(
            title="🎲 نتيجة لعبة النرد",
            description=f"{ctx.author.mention} رمى النرد...\n"
                        f"الرهان على: **{bet_name}**\n"
                        f"المبلغ: **{bet_amount:,}** {self.currency_emoji}\n\n"
                        f"النتيجة: **{dice_emoji} ({dice_result})**\n\n"
                        f"{result_text}",
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
    await bot.add_cog(Dice(bot)) 