#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import random
import asyncio
import datetime

class Coinflip(commands.Cog):
    """لعبة رمي العملة"""
    
    def __init__(self, bot):
        self.bot = bot
        self.currency_emoji = self.bot.config.get('bank', {}).get('currencyEmoji', '💰')
        self.min_bet = self.bot.config.get('games', {}).get('minBet', 10)
        self.max_bet = self.bot.config.get('games', {}).get('maxBet', 10000)
    
    @commands.command(
        name="عملة",
        aliases=["coinflip", "flip", "رمي_عملة", "قلب_عملة"],
        description="لعبة رمي العملة للمراهنة"
    )
    async def coinflip(self, ctx, choice: str = None, amount: str = None):
        """
        لعبة رمي العملة للمراهنة
        
        المعلمات:
            choice (str): اختيارك 'وجه' أو 'كتابة' (heads or tails)
            amount (str): المبلغ الذي تريد المراهنة عليه
        
        أمثلة:
            !عملة وجه 100
            !عملة كتابة 500
            !coinflip heads 200
            !flip tails 1000
        """
        # التحقق من المعلمات
        if not choice or not amount:
            embed = discord.Embed(
                title="❌ خطأ في الأمر",
                description=f"يجب عليك تحديد الاختيار والمبلغ.\n"
                            f"مثال: `!عملة وجه 100` أو `!عملة كتابة 500`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # تحويل الاختيار إلى تنسيق موحد
        if choice.lower() in ["وجه", "heads", "h", "head", "و"]:
            side = "heads"
            side_name = "وجه 🪙"
        elif choice.lower() in ["كتابة", "tails", "t", "tail", "ك"]:
            side = "tails"
            side_name = "كتابة 📝"
        else:
            embed = discord.Embed(
                title="❌ خطأ في الاختيار",
                description=f"يجب اختيار `وجه` أو `كتابة`.",
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
        
        # رمي العملة
        embed = discord.Embed(
            title="🪙 رمي العملة",
            description=f"{ctx.author.mention} يرمي العملة...",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        message = await ctx.send(embed=embed)
        
        # تأخير لإضافة التشويق
        await asyncio.sleep(2)
        
        # تحديد النتيجة
        result = random.choice(["heads", "tails"])
        won = result == side
        
        # تحديث الرصيد
        if won:
            # المستخدم ربح، مضاعفة المبلغ
            new_balance = user_data['balance'] + bet_amount
            result_text = f"🎉 مبروك! لقد ربحت **{bet_amount:,}** {self.currency_emoji}"
            color = discord.Color.green()
        else:
            # المستخدم خسر
            new_balance = user_data['balance'] - bet_amount
            result_text = f"😔 للأسف، لقد خسرت **{bet_amount:,}** {self.currency_emoji}"
            color = discord.Color.red()
        
        # تحديث رصيد المستخدم في قاعدة البيانات
        if hasattr(self.bot, 'db'):
            await self.bot.db.users.update_one(
                {"user_id": ctx.author.id},
                {"$set": {"balance": new_balance}}
            )
        
        # إعداد النتيجة النهائية
        if result == "heads":
            result_name = "وجه 🪙"
        else:
            result_name = "كتابة 📝"
        
        # تحديث رسالة النتيجة
        embed = discord.Embed(
            title="🪙 نتيجة رمي العملة",
            description=f"اختيارك: **{side_name}**\n"
                        f"النتيجة: **{result_name}**\n\n"
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
    await bot.add_cog(Coinflip(bot)) 