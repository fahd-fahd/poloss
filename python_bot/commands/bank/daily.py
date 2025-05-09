#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import datetime
import random

class Daily(commands.Cog):
    """نظام البنك والاقتصاد"""
    
    def __init__(self, bot):
        self.bot = bot
        self.currency_name = self.bot.config.get('bank', {}).get('currencyName', 'عملة')
        self.currency_emoji = self.bot.config.get('bank', {}).get('currencyEmoji', '💰')
        self.daily_reward = self.bot.config.get('bank', {}).get('dailyReward', 200)
        self.daily_cooldown = self.bot.config.get('bank', {}).get('dailyCooldown', 86400)  # 24 ساعة بالثواني
    
    @commands.command(
        name="يومي",
        aliases=["daily", "اليومي", "هدية", "مكافأة"],
        description="الحصول على المكافأة اليومية من البنك"
    )
    async def daily(self, ctx):
        """
        الحصول على المكافأة اليومية
        يمكن استخدام هذا الأمر مرة واحدة كل 24 ساعة للحصول على عملات مجانية
        """
        user_id = ctx.author.id
        
        try:
            # جلب بيانات المستخدم من قاعدة البيانات
            user_data = await self._get_user_data(user_id)
            
            # التحقق من وقت آخر استلام للهدية اليومية
            last_claim = None
            if 'bank_profile' in user_data and 'daily' in user_data['bank_profile']:
                last_claim = user_data['bank_profile']['daily'].get('last_claim')
            
            # التحقق مما إذا كان يمكن المطالبة بالهدية اليومية
            now = datetime.datetime.utcnow()
            can_claim = True
            time_remaining = None
            
            if last_claim:
                last_claim_date = datetime.datetime.fromisoformat(last_claim)
                next_claim = last_claim_date + datetime.timedelta(seconds=self.daily_cooldown)
                
                if now < next_claim:
                    can_claim = False
                    time_remaining = next_claim - now
            
            if can_claim:
                # تحديد مقدار المكافأة (قد تتضمن عنصرًا عشوائيًا)
                reward_amount = self.daily_reward
                bonus = random.randint(0, 100)  # مكافأة عشوائية إضافية
                streak = 0
                
                # زيادة التتابع إذا كان آخر استلام خلال آخر 30 ساعة (يومية + 6 ساعات مهلة)
                if last_claim:
                    last_claim_date = datetime.datetime.fromisoformat(last_claim)
                    hours_since_last = (now - last_claim_date).total_seconds() / 3600
                    
                    if hours_since_last < 30:
                        streak = user_data['bank_profile'].get('daily', {}).get('streak', 0) + 1
                        
                        # مكافأة التتابع: 10% إضافية لكل يوم متتالي، بحد أقصى 100%
                        streak_bonus = min(streak * 10, 100) / 100
                        bonus += int(reward_amount * streak_bonus)
                
                total_reward = reward_amount + bonus
                
                # تحديث بيانات المستخدم
                if hasattr(self.bot, 'db'):
                    # تحديث في قاعدة البيانات
                    users_collection = self.bot.db.users
                    
                    # تحديث الرصيد والمعلومات اليومية
                    await users_collection.update_one(
                        {'user_id': user_id},
                        {
                            '$inc': {'balance': total_reward},
                            '$set': {
                                'bank_profile.daily.last_claim': now.isoformat(),
                                'bank_profile.daily.streak': streak
                            }
                        },
                        upsert=True
                    )
                
                # تحديث البيانات المحلية للعرض
                user_data['balance'] += total_reward
                if 'bank_profile' not in user_data:
                    user_data['bank_profile'] = {}
                if 'daily' not in user_data['bank_profile']:
                    user_data['bank_profile']['daily'] = {}
                
                user_data['bank_profile']['daily']['last_claim'] = now.isoformat()
                user_data['bank_profile']['daily']['streak'] = streak
                
                # إنشاء رسالة مضمنة لعرض المكافأة
                embed = discord.Embed(
                    title="💰 المكافأة اليومية",
                    description=f"لقد حصلت على مكافأتك اليومية!",
                    color=discord.Color.gold()
                )
                
                # إضافة معلومات المكافأة
                embed.add_field(
                    name="💵 المكافأة الأساسية",
                    value=f"**{reward_amount:,}** {self.currency_emoji}",
                    inline=True
                )
                
                if bonus > 0:
                    embed.add_field(
                        name="✨ المكافأة الإضافية",
                        value=f"**{bonus:,}** {self.currency_emoji}",
                        inline=True
                    )
                
                embed.add_field(
                    name="🏦 المجموع",
                    value=f"**{total_reward:,}** {self.currency_emoji}",
                    inline=True
                )
                
                # إضافة معلومات التتابع
                if streak > 0:
                    embed.add_field(
                        name="🔥 تتابع يومي",
                        value=f"**{streak}** يوم متتالي!",
                        inline=True
                    )
                
                # إضافة الرصيد الحالي
                embed.add_field(
                    name="💳 رصيدك الحالي",
                    value=f"**{user_data['balance']:,}** {self.currency_emoji}",
                    inline=True
                )
                
                # إضافة صورة المستخدم
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                
                # إضافة تذييل
                embed.set_footer(text="عد غدًا للحصول على المزيد من العملات!")
                
                # إرسال رسالة النجاح
                await ctx.send(embed=embed)
                
            else:
                # لا يمكن المطالبة بالمكافأة اليومية حتى انتهاء فترة الانتظار
                hours, remainder = divmod(int(time_remaining.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                
                embed = discord.Embed(
                    title="⏳ انتظر",
                    description="لقد حصلت بالفعل على مكافأتك اليومية.",
                    color=discord.Color.red()
                )
                
                embed.add_field(
                    name="⏰ الوقت المتبقي",
                    value=f"**{hours}** ساعة **{minutes}** دقيقة **{seconds}** ثانية",
                    inline=False
                )
                
                embed.set_footer(text="حاول مرة أخرى بعد انتهاء المدة")
                
                await ctx.send(embed=embed)
                
        except Exception as e:
            # في حالة حدوث خطأ، أرسل رسالة خطأ
            error_embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ أثناء محاولة الحصول على المكافأة اليومية: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed)
    
    async def _get_user_data(self, user_id):
        """
        الحصول على بيانات المستخدم من قاعدة البيانات
        إذا لم تكن البيانات موجودة، يتم إنشاء بيانات جديدة
        
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
    await bot.add_cog(Daily(bot)) 