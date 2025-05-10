#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import datetime
import math

class Protection(commands.Cog):
    """نظام الحماية للبنك"""
    
    def __init__(self, bot):
        self.bot = bot
        self.currency_name = self.bot.config.get('bank', {}).get('currencyName', 'عملة')
        self.currency_emoji = self.bot.config.get('bank', {}).get('currencyEmoji', '💰')
        
        # مستويات الحماية وأسعارها
        self.protection_levels = {
            "3": {"price": 2500, "hours": 3, "emoji": "🛡️"},
            "8": {"price": 5000, "hours": 8, "emoji": "🛡️🛡️"},
            "24": {"price": 15000, "hours": 24, "emoji": "🛡️🛡️🛡️"}
        }
    
    @commands.command(
        name="حماية",
        aliases=["protection", "protect", "حمي"],
        description="شراء حماية لحسابك البنكي من السرقة"
    )
    async def protect(self, ctx, duration: str = None):
        """
        شراء حماية لحسابك البنكي من السرقة
        
        المعلمات:
            duration (str): مدة الحماية بالساعات (3, 8, أو 24)
        
        أمثلة:
            !حماية - لعرض خيارات الحماية
            !حماية 3 - لشراء حماية لمدة 3 ساعات
            !حماية 8 - لشراء حماية لمدة 8 ساعات
            !حماية 24 - لشراء حماية لمدة 24 ساعة
        """
        # الوصول إلى كائن Theft
        theft_cog = self.bot.get_cog('Theft')
        if not theft_cog:
            embed = discord.Embed(
                title="❌ خطأ",
                description="نظام السرقة غير متاح حالياً. لا يمكن شراء حماية.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        if not duration:
            # عرض خيارات الحماية
            embed = self._create_protection_options()
            return await ctx.send(embed=embed)
        
        # التحقق من صحة المدة
        if duration not in self.protection_levels:
            embed = discord.Embed(
                title="❌ خيار غير صالح",
                description="يرجى اختيار إحدى المدد المتاحة: 3, 8, أو 24 ساعة.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # جلب بيانات المستخدم
        user_data = await self._get_user_data(ctx.author.id)
        
        # التحقق من إذا كان المستخدم محمي بالفعل
        now = datetime.datetime.utcnow()
        if ctx.author.id in theft_cog.protected_users:
            protection_end = theft_cog.protected_users[ctx.author.id]
            if now < protection_end:
                time_left = protection_end - now
                hours = math.floor(time_left.total_seconds() / 3600)
                minutes = math.floor((time_left.total_seconds() % 3600) / 60)
                
                embed = discord.Embed(
                    title="🛡️ محمي بالفعل",
                    description=f"حسابك محمي بالفعل! الحماية الحالية ستنتهي بعد **{hours} ساعة و {minutes} دقيقة**.\n\n"
                               f"هل ترغب في تمديد الحماية؟ استخدم `!تمديد_حماية` للتمديد.",
                    color=discord.Color.blue()
                )
                return await ctx.send(embed=embed)
        
        # الحصول على معلومات الحماية المختارة
        protection_info = self.protection_levels[duration]
        price = protection_info["price"]
        hours = protection_info["hours"]
        emoji = protection_info["emoji"]
        
        # التحقق من الرصيد
        if user_data["balance"] < price:
            embed = discord.Embed(
                title="❌ رصيد غير كافٍ",
                description=f"ليس لديك رصيد كافٍ لشراء هذه الحماية.\n"
                           f"السعر: **{price:,}** {self.currency_emoji}\n"
                           f"رصيدك: **{user_data['balance']:,}** {self.currency_emoji}",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # تحديث قاعدة البيانات
        if hasattr(self.bot, 'db'):
            users_collection = self.bot.db.users
            
            # خصم المبلغ من المستخدم
            await users_collection.update_one(
                {'user_id': ctx.author.id},
                {'$inc': {'balance': -price}}
            )
            
            # تسجيل في سجل المعاملات
            transactions_collection = self.bot.db.transactions
            if transactions_collection:
                await transactions_collection.insert_one({
                    'type': 'protection',
                    'user_id': ctx.author.id,
                    'amount': price,
                    'duration_hours': hours,
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'channel_id': ctx.channel.id,
                    'guild_id': ctx.guild.id if ctx.guild else None
                })
        
        # تحديث البيانات المحلية
        user_data['balance'] -= price
        
        # تعيين الحماية
        protection_end = now + datetime.timedelta(hours=hours)
        theft_cog.protected_users[ctx.author.id] = protection_end
        
        # إنشاء رسالة تأكيد
        embed = discord.Embed(
            title=f"{emoji} حماية نشطة!",
            description=f"تم تفعيل الحماية على حسابك لمدة **{hours} ساعة**!\n"
                       f"لن يتمكن أحد من سرقتك حتى **{protection_end.strftime('%Y-%m-%d %H:%M:%S')} UTC**.",
            color=discord.Color.green()
        )
        
        # إضافة معلومات الرصيد
        embed.add_field(
            name="💸 تكلفة الحماية",
            value=f"**{price:,}** {self.currency_emoji}",
            inline=True
        )
        
        embed.add_field(
            name="💰 رصيدك الحالي",
            value=f"**{user_data['balance']:,}** {self.currency_emoji}",
            inline=True
        )
        
        # إضافة صورة المستخدم
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(
        name="تمديد_حماية",
        aliases=["extend_protection", "extend"],
        description="تمديد فترة الحماية الحالية"
    )
    async def extend_protection(self, ctx, duration: str = None):
        """
        تمديد فترة الحماية الحالية
        
        المعلمات:
            duration (str): مدة التمديد بالساعات (3, 8, أو 24)
        
        أمثلة:
            !تمديد_حماية - لعرض خيارات التمديد
            !تمديد_حماية 3 - لتمديد الحماية بمدة 3 ساعات إضافية
        """
        # الوصول إلى كائن Theft
        theft_cog = self.bot.get_cog('Theft')
        if not theft_cog:
            embed = discord.Embed(
                title="❌ خطأ",
                description="نظام السرقة غير متاح حالياً. لا يمكن تمديد الحماية.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من أن المستخدم محمي بالفعل
        now = datetime.datetime.utcnow()
        if ctx.author.id not in theft_cog.protected_users or theft_cog.protected_users[ctx.author.id] < now:
            embed = discord.Embed(
                title="❌ غير محمي",
                description="ليس لديك حماية نشطة حالياً للتمديد. استخدم `!حماية` لشراء حماية جديدة.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        if not duration:
            # عرض خيارات الحماية
            embed = self._create_protection_options(is_extension=True)
            return await ctx.send(embed=embed)
        
        # التحقق من صحة المدة
        if duration not in self.protection_levels:
            embed = discord.Embed(
                title="❌ خيار غير صالح",
                description="يرجى اختيار إحدى المدد المتاحة: 3, 8, أو 24 ساعة.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # جلب بيانات المستخدم
        user_data = await self._get_user_data(ctx.author.id)
        
        # الحصول على معلومات الحماية المختارة
        protection_info = self.protection_levels[duration]
        price = protection_info["price"]
        hours = protection_info["hours"]
        emoji = protection_info["emoji"]
        
        # التحقق من الرصيد
        if user_data["balance"] < price:
            embed = discord.Embed(
                title="❌ رصيد غير كافٍ",
                description=f"ليس لديك رصيد كافٍ لتمديد الحماية.\n"
                           f"السعر: **{price:,}** {self.currency_emoji}\n"
                           f"رصيدك: **{user_data['balance']:,}** {self.currency_emoji}",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # تحديث قاعدة البيانات
        if hasattr(self.bot, 'db'):
            users_collection = self.bot.db.users
            
            # خصم المبلغ من المستخدم
            await users_collection.update_one(
                {'user_id': ctx.author.id},
                {'$inc': {'balance': -price}}
            )
            
            # تسجيل في سجل المعاملات
            transactions_collection = self.bot.db.transactions
            if transactions_collection:
                await transactions_collection.insert_one({
                    'type': 'protection_extension',
                    'user_id': ctx.author.id,
                    'amount': price,
                    'duration_hours': hours,
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'channel_id': ctx.channel.id,
                    'guild_id': ctx.guild.id if ctx.guild else None
                })
        
        # تحديث البيانات المحلية
        user_data['balance'] -= price
        
        # تمديد الحماية
        current_protection_end = theft_cog.protected_users[ctx.author.id]
        new_protection_end = current_protection_end + datetime.timedelta(hours=hours)
        theft_cog.protected_users[ctx.author.id] = new_protection_end
        
        # حساب المدة الإجمالية
        total_time = new_protection_end - now
        total_hours = math.floor(total_time.total_seconds() / 3600)
        
        # إنشاء رسالة تأكيد
        embed = discord.Embed(
            title=f"{emoji} تم تمديد الحماية!",
            description=f"تم تمديد الحماية على حسابك بمدة **{hours} ساعة** إضافية!\n"
                       f"الحماية ستستمر الآن حتى **{new_protection_end.strftime('%Y-%m-%d %H:%M:%S')} UTC**\n"
                       f"(إجمالي **{total_hours} ساعة** من الآن)",
            color=discord.Color.green()
        )
        
        # إضافة معلومات الرصيد
        embed.add_field(
            name="💸 تكلفة التمديد",
            value=f"**{price:,}** {self.currency_emoji}",
            inline=True
        )
        
        embed.add_field(
            name="💰 رصيدك الحالي",
            value=f"**{user_data['balance']:,}** {self.currency_emoji}",
            inline=True
        )
        
        # إضافة صورة المستخدم
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(
        name="حالة_الحماية",
        aliases=["protection_status", "status"],
        description="عرض حالة الحماية لحسابك"
    )
    async def protection_status(self, ctx):
        """عرض حالة الحماية الحالية لحسابك"""
        # الوصول إلى كائن Theft
        theft_cog = self.bot.get_cog('Theft')
        if not theft_cog:
            embed = discord.Embed(
                title="❌ خطأ",
                description="نظام السرقة غير متاح حالياً.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        now = datetime.datetime.utcnow()
        
        # التحقق من حالة الحماية
        if ctx.author.id in theft_cog.protected_users:
            protection_end = theft_cog.protected_users[ctx.author.id]
            
            if now < protection_end:
                # الحماية نشطة
                time_left = protection_end - now
                hours = math.floor(time_left.total_seconds() / 3600)
                minutes = math.floor((time_left.total_seconds() % 3600) / 60)
                
                embed = discord.Embed(
                    title="🛡️ حالة الحماية",
                    description=f"حسابك محمي حالياً من السرقة.\n"
                               f"الحماية ستنتهي بعد **{hours} ساعة و {minutes} دقيقة**\n"
                               f"(في **{protection_end.strftime('%Y-%m-%d %H:%M:%S')} UTC**)",
                    color=discord.Color.green()
                )
                
                embed.add_field(
                    name="📝 ملاحظة",
                    value="يمكنك تمديد فترة الحماية باستخدام أمر `!تمديد_حماية`",
                    inline=False
                )
            else:
                # الحماية منتهية
                embed = discord.Embed(
                    title="⚠️ الحماية منتهية",
                    description="انتهت فترة الحماية لحسابك! أنت معرض للسرقة الآن.",
                    color=discord.Color.gold()
                )
                
                embed.add_field(
                    name="🛡️ تجديد الحماية",
                    value="استخدم أمر `!حماية` لشراء حماية جديدة لحسابك.",
                    inline=False
                )
        else:
            # لا توجد حماية
            embed = discord.Embed(
                title="⚠️ غير محمي",
                description="حسابك غير محمي حالياً من عمليات السرقة!",
                color=discord.Color.gold()
            )
            
            embed.add_field(
                name="🛡️ شراء حماية",
                value="استخدم أمر `!حماية` لشراء حماية لحسابك.",
                inline=False
            )
        
        # إضافة صورة المستخدم
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    def _create_protection_options(self, is_extension=False):
        """إنشاء قائمة خيارات الحماية"""
        action = "تمديد" if is_extension else "شراء"
        
        embed = discord.Embed(
            title="🛡️ خيارات الحماية",
            description=f"اختر مدة الحماية التي ترغب في {action}ها:",
            color=discord.Color.blue()
        )
        
        for key, info in self.protection_levels.items():
            embed.add_field(
                name=f"{info['emoji']} {key} ساعة",
                value=f"السعر: **{info['price']:,}** {self.currency_emoji}\n"
                     f"استخدم `!{'تمديد_حماية' if is_extension else 'حماية'} {key}`",
                inline=False
            )
        
        embed.set_footer(text="الحماية تمنع الآخرين من سرقة أموالك")
        
        return embed
    
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
    await bot.add_cog(Protection(bot)) 