#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import datetime
import random
import asyncio
import math

class Theft(commands.Cog):
    """نظام السرقة والحماية للبنك"""
    
    def __init__(self, bot):
        self.bot = bot
        self.protected_users = {}  # تخزين المستخدمين المحميين {user_id: end_time}
        self.theft_cooldowns = {}  # تخزين أوقات انتظار السرقة {user_id: next_available_time}
        self.currency_name = self.bot.config.get('bank', {}).get('currencyName', 'عملة')
        self.currency_emoji = self.bot.config.get('bank', {}).get('currencyEmoji', '💰')
        
        # قيم لضبط نظام السرقة
        self.min_theft_cooldown = 3600  # الحد الأدنى لوقت الانتظار (ساعة واحدة)
        self.max_theft_percent = 0.35  # الحد الأقصى للنسبة المئوية للسرقة (35%)
        self.min_balance_for_theft = 1000  # الحد الأدنى للرصيد للتمكن من السرقة
        
        # مستويات الحماية وأسعارها
        self.protection_levels = {
            "3": {"price": 2500, "hours": 3, "emoji": "🛡️"},
            "8": {"price": 5000, "hours": 8, "emoji": "🛡️🛡️"},
            "24": {"price": 15000, "hours": 24, "emoji": "🛡️🛡️🛡️"}
        }
    
    @commands.command(
        name="سرقة",
        aliases=["steal", "theft"],
        description="محاولة سرقة أموال من مستخدم آخر"
    )
    @commands.cooldown(1, 60, commands.BucketType.user)  # منع سبام الأمر
    async def steal(self, ctx, target: discord.Member = None):
        """
        محاولة سرقة أموال من مستخدم آخر
        
        المعلمات:
            target (discord.Member): المستخدم المراد سرقته
        """
        # التحقق من وجود هدف
        if not target:
            embed = discord.Embed(
                title="❌ خطأ",
                description="يجب تحديد مستخدم للسرقة منه.\n"
                            "مثال: `!سرقة @User`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من عدم سرقة النفس
        if target.id == ctx.author.id:
            embed = discord.Embed(
                title="❓ محاولة غريبة",
                description="لا يمكنك سرقة نفسك! هذا يبدو غريباً...",
                color=discord.Color.gold()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من عدم سرقة البوت
        if target.bot:
            embed = discord.Embed(
                title="🤖 محاولة فاشلة",
                description="لا يمكنك سرقة البوتات! لديهم أنظمة أمان متقدمة.",
                color=discord.Color.gold()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من فترة الانتظار
        now = datetime.datetime.utcnow()
        
        if ctx.author.id in self.theft_cooldowns:
            cooldown_end = self.theft_cooldowns[ctx.author.id]
            if now < cooldown_end:
                time_left = cooldown_end - now
                hours, remainder = divmod(time_left.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                embed = discord.Embed(
                    title="⏱️ انتظر قليلاً",
                    description=f"لا يمكنك السرقة الآن، عليك الانتظار **{hours} ساعة و {minutes} دقيقة** للمحاولة مرة أخرى.",
                    color=discord.Color.gold()
                )
                return await ctx.send(embed=embed)
        
        # التحقق من الحماية
        if target.id in self.protected_users:
            protection_end = self.protected_users[target.id]
            if now < protection_end:
                time_left = protection_end - now
                hours, remainder = divmod(time_left.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                embed = discord.Embed(
                    title="🛡️ محمي",
                    description=f"{target.mention} محمي حالياً! لا يمكنك سرقته.\n"
                               f"تنتهي الحماية بعد **{hours} ساعة و {minutes} دقيقة**.",
                    color=discord.Color.gold()
                )
                return await ctx.send(embed=embed)
        
        # جلب بيانات المستخدمين
        try:
            thief_data = await self._get_user_data(ctx.author.id)
            target_data = await self._get_user_data(target.id)
            
            # التحقق من أن للمستخدم رصيد كافٍ للسرقة
            if thief_data['balance'] < self.min_balance_for_theft:
                embed = discord.Embed(
                    title="💰 رصيد غير كافٍ",
                    description=f"يجب أن يكون لديك على الأقل **{self.min_balance_for_theft:,}** {self.currency_emoji} للسرقة.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
            
            # التحقق من أن الهدف لديه مال للسرقة
            if target_data['balance'] <= 100:
                embed = discord.Embed(
                    title="💸 لا يوجد ما يُسرق",
                    description=f"{target.mention} ليس لديه أموال كافية للسرقة!",
                    color=discord.Color.gold()
                )
                return await ctx.send(embed=embed)
            
            # حساب احتمالية نجاح السرقة (بين 40% و 75%)
            theft_success_chance = random.randint(40, 75)
            
            # تعديل الاحتمالية بناءً على مستوى اللاعبين (المستويات المتقدمة تزيد الفرص)
            thief_level = thief_data.get('bank_profile', {}).get('level', 1)
            target_level = target_data.get('bank_profile', {}).get('level', 1)
            
            # زيادة احتمالية النجاح للمستويات العالية
            if thief_level > target_level:
                theft_success_chance += min((thief_level - target_level) * 5, 20)  # حد أقصى 20% إضافية
            
            # تقليل احتمالية النجاح إذا كان الهدف أعلى مستوى
            if target_level > thief_level:
                theft_success_chance -= min((target_level - thief_level) * 3, 15)  # حد أقصى 15% خفض
            
            # يجب أن تكون الاحتمالية بين 30% و 90%
            theft_success_chance = max(30, min(theft_success_chance, 90))
            
            # رسالة البدء
            start_embed = discord.Embed(
                title="🕵️ محاولة سرقة",
                description=f"{ctx.author.mention} يحاول سرقة {target.mention}...",
                color=discord.Color.gold()
            )
            message = await ctx.send(embed=start_embed)
            
            # إضافة تأثير إنتظار
            await asyncio.sleep(2)
            
            # تحديد ما إذا كانت السرقة ناجحة
            is_success = random.randint(1, 100) <= theft_success_chance
            
            if is_success:
                # حساب المبلغ المسروق (10-35% من رصيد الهدف)
                steal_percent = random.uniform(0.10, self.max_theft_percent)
                stolen_amount = int(target_data['balance'] * steal_percent)
                
                # التأكد من أن المبلغ المسروق ليس صفر
                if stolen_amount <= 0:
                    stolen_amount = random.randint(1, min(100, target_data['balance']))
                
                # ضمان عدم سرقة كامل المبلغ
                if stolen_amount >= target_data['balance']:
                    stolen_amount = int(target_data['balance'] * 0.75)  # سرقة 75% كحد أقصى
                
                # تحديث قاعدة البيانات
                if hasattr(self.bot, 'db'):
                    users_collection = self.bot.db.users
                    
                    # تحديث رصيد الهدف (خصم المبلغ المسروق)
                    await users_collection.update_one(
                        {'user_id': target.id},
                        {'$inc': {'balance': -stolen_amount}}
                    )
                    
                    # تحديث رصيد السارق (إضافة المبلغ المسروق)
                    await users_collection.update_one(
                        {'user_id': ctx.author.id},
                        {'$inc': {'balance': stolen_amount}}
                    )
                    
                    # تسجيل في سجل المعاملات
                    transactions_collection = self.bot.db.transactions
                    if transactions_collection:
                        await transactions_collection.insert_one({
                            'type': 'theft',
                            'thief_id': ctx.author.id,
                            'target_id': target.id,
                            'amount': stolen_amount,
                            'timestamp': datetime.datetime.utcnow().isoformat(),
                            'channel_id': ctx.channel.id,
                            'guild_id': ctx.guild.id if ctx.guild else None
                        })
                
                # تحديث البيانات المحلية
                target_data['balance'] -= stolen_amount
                thief_data['balance'] += stolen_amount
                
                # تعيين فترة الانتظار للسرقة القادمة (1-3 ساعات)
                cooldown_hours = random.uniform(1, 3)
                self.theft_cooldowns[ctx.author.id] = now + datetime.timedelta(hours=cooldown_hours)
                
                # إنشاء رسالة النجاح
                embed = discord.Embed(
                    title="💰 سرقة ناجحة!",
                    description=f"{ctx.author.mention} نجح في سرقة **{stolen_amount:,}** {self.currency_emoji} من {target.mention}!",
                    color=discord.Color.green()
                )
                
                # إضافة معلومات الرصيد
                embed.add_field(
                    name="💳 رصيدك الجديد",
                    value=f"**{thief_data['balance']:,}** {self.currency_emoji}",
                    inline=True
                )
                
                embed.add_field(
                    name=f"💸 رصيد {target.display_name}",
                    value=f"**{target_data['balance']:,}** {self.currency_emoji}",
                    inline=True
                )
                
                # إضافة صورة السارق
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                
                await message.edit(embed=embed)
                
                # محاولة إرسال إشعار للضحية
                try:
                    target_notify = discord.Embed(
                        title="⚠️ تمت سرقتك!",
                        description=f"{ctx.author.mention} قام بسرقة **{stolen_amount:,}** {self.currency_emoji} من رصيدك!",
                        color=discord.Color.red()
                    )
                    target_notify.add_field(
                        name="💰 رصيدك الحالي",
                        value=f"**{target_data['balance']:,}** {self.currency_emoji}",
                        inline=True
                    )
                    target_notify.add_field(
                        name="🛡️ حماية حسابك",
                        value=f"استخدم `!حماية` لحماية حسابك من السرقة",
                        inline=False
                    )
                    
                    # إضافة صورة السارق
                    target_notify.set_thumbnail(url=ctx.author.display_avatar.url)
                    
                    await target.send(embed=target_notify)
                except:
                    pass
                
            else:
                # السرقة فشلت
                # تعيين فترة الانتظار (1-2 ساعة)
                cooldown_hours = random.uniform(1, 2)
                self.theft_cooldowns[ctx.author.id] = now + datetime.timedelta(hours=cooldown_hours)
                
                # حساب الغرامة (5-15% من رصيد السارق)
                fine_percent = random.uniform(0.05, 0.15)
                fine_amount = int(thief_data['balance'] * fine_percent)
                
                # التأكد من أن الغرامة ليست كبيرة جداً
                if fine_amount > 5000:
                    fine_amount = min(fine_amount, 5000)
                
                # التأكد من أن الغرامة ليست صفراً
                if fine_amount <= 0:
                    fine_amount = random.randint(1, min(100, thief_data['balance']))
                
                # تحديث قاعدة البيانات
                if hasattr(self.bot, 'db'):
                    users_collection = self.bot.db.users
                    
                    # تحديث رصيد السارق (خصم الغرامة)
                    await users_collection.update_one(
                        {'user_id': ctx.author.id},
                        {'$inc': {'balance': -fine_amount}}
                    )
                
                # تحديث البيانات المحلية
                thief_data['balance'] -= fine_amount
                
                # إنشاء رسالة الفشل
                embed = discord.Embed(
                    title="❌ سرقة فاشلة!",
                    description=f"{ctx.author.mention} فشل في سرقة {target.mention} وتم القبض عليه!\n"
                                f"تم تغريمك **{fine_amount:,}** {self.currency_emoji}.",
                    color=discord.Color.red()
                )
                
                # إضافة معلومات الرصيد
                embed.add_field(
                    name="💸 رصيدك الجديد",
                    value=f"**{thief_data['balance']:,}** {self.currency_emoji}",
                    inline=True
                )
                
                # إضافة توقيت المحاولة القادمة
                next_attempt_time = self.theft_cooldowns[ctx.author.id]
                time_diff = next_attempt_time - now
                hours = math.floor(time_diff.total_seconds() / 3600)
                minutes = math.floor((time_diff.total_seconds() % 3600) / 60)
                
                embed.add_field(
                    name="⏱️ المحاولة القادمة",
                    value=f"يمكنك المحاولة مرة أخرى بعد **{hours} ساعة و {minutes} دقيقة**",
                    inline=False
                )
                
                # إضافة صورة المستخدم
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                
                await message.edit(embed=embed)
                
                # محاولة إرسال إشعار للضحية
                try:
                    target_notify = discord.Embed(
                        title="🚨 محاولة سرقة فاشلة!",
                        description=f"{ctx.author.mention} حاول سرقتك ولكنه فشل!",
                        color=discord.Color.gold()
                    )
                    target_notify.add_field(
                        name="🛡️ حماية حسابك",
                        value=f"استخدم `!حماية` لحماية حسابك من محاولات السرقة المستقبلية",
                        inline=False
                    )
                    
                    # إضافة صورة السارق
                    target_notify.set_thumbnail(url=ctx.author.display_avatar.url)
                    
                    await target.send(embed=target_notify)
                except:
                    pass
        
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ أثناء محاولة السرقة: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            
    @steal.error
    async def steal_error(self, ctx, error):
        """معالجة أخطاء أمر السرقة"""
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏱️ انتظر قليلاً",
                description=f"لا يمكنك استخدام أمر السرقة الآن. حاول مرة أخرى بعد {error.retry_after:.0f} ثانية.",
                color=discord.Color.gold()
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(
                title="❌ خطأ",
                description="لم يتم العثور على المستخدم المحدد.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ غير متوقع: {str(error)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
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
    await bot.add_cog(Theft(bot)) 