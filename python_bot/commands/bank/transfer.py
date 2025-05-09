#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import datetime
import re

class Transfer(commands.Cog):
    """نظام البنك والاقتصاد"""
    
    def __init__(self, bot):
        self.bot = bot
        self.currency_name = self.bot.config.get('bank', {}).get('currencyName', 'عملة')
        self.currency_emoji = self.bot.config.get('bank', {}).get('currencyEmoji', '💰')
        self.min_transfer = self.bot.config.get('bank', {}).get('minTransfer', 10)
    
    @commands.command(
        name="تحويل",
        aliases=["transfer", "send", "ارسال", "إرسال"],
        description=f"تحويل العملات إلى مستخدم آخر"
    )
    async def transfer(self, ctx, recipient: discord.Member = None, amount: str = None):
        """
        تحويل العملات إلى مستخدم آخر
        
        المعلمات:
            recipient (discord.Member): المستخدم المراد التحويل إليه
            amount (str): المبلغ المراد تحويله (يمكن استخدام الأرقام أو الكلمات مثل 'كل' أو 'all')
        
        أمثلة:
            !تحويل @User 100
            !تحويل @User كل
            !transfer @User 500
            !transfer @User all
        """
        # التحقق من وجود جميع المعلمات المطلوبة
        if not recipient:
            embed = discord.Embed(
                title="❌ خطأ في الأمر",
                description=f"يرجى تحديد المستخدم المراد التحويل إليه.\n"
                            f"مثال: `!تحويل @User 100`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        if not amount:
            embed = discord.Embed(
                title="❌ خطأ في الأمر",
                description=f"يرجى تحديد المبلغ المراد تحويله.\n"
                            f"مثال: `!تحويل @{recipient.display_name} 100`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من أن المستلم ليس البوت أو المرسل نفسه
        if recipient.bot:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك تحويل العملات إلى بوت!",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        if recipient.id == ctx.author.id:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك تحويل العملات إلى نفسك!",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        try:
            # الحصول على بيانات المرسل
            sender_data = await self._get_user_data(ctx.author.id)
            
            # تحويل المبلغ إلى رقم
            if amount.lower() in ['all', 'كل', 'الكل']:
                transfer_amount = sender_data['balance']
            else:
                # إزالة أي علامات ترقيم أو فواصل
                cleaned_amount = re.sub(r'[^\d]', '', amount)
                if not cleaned_amount:
                    embed = discord.Embed(
                        title="❌ خطأ",
                        description="يرجى إدخال مبلغ صحيح للتحويل.",
                        color=discord.Color.red()
                    )
                    return await ctx.send(embed=embed)
                
                transfer_amount = int(cleaned_amount)
            
            # التحقق من صحة المبلغ
            if transfer_amount <= 0:
                embed = discord.Embed(
                    title="❌ خطأ",
                    description="يجب أن يكون المبلغ المراد تحويله أكبر من صفر.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
            
            if transfer_amount < self.min_transfer:
                embed = discord.Embed(
                    title="❌ خطأ",
                    description=f"الحد الأدنى للتحويل هو {self.min_transfer} {self.currency_name}.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
            
            # التحقق من رصيد المرسل
            if sender_data['balance'] < transfer_amount:
                embed = discord.Embed(
                    title="❌ رصيد غير كافٍ",
                    description=f"ليس لديك رصيد كافٍ للتحويل.\n"
                                f"رصيدك الحالي: **{sender_data['balance']:,}** {self.currency_emoji}",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
            
            # الحصول على بيانات المستلم
            recipient_data = await self._get_user_data(recipient.id)
            
            # إجراء التحويل
            if hasattr(self.bot, 'db'):
                # تحديث في قاعدة البيانات
                users_collection = self.bot.db.users
                
                # خصم المبلغ من المرسل
                await users_collection.update_one(
                    {'user_id': ctx.author.id},
                    {'$inc': {'balance': -transfer_amount}}
                )
                
                # إضافة المبلغ للمستلم
                await users_collection.update_one(
                    {'user_id': recipient.id},
                    {'$inc': {'balance': transfer_amount}}
                )
                
                # تسجيل المعاملة في سجل المعاملات
                transactions_collection = self.bot.db.transactions
                if transactions_collection:
                    await transactions_collection.insert_one({
                        'sender_id': ctx.author.id,
                        'recipient_id': recipient.id,
                        'amount': transfer_amount,
                        'timestamp': datetime.datetime.utcnow().isoformat(),
                        'channel_id': ctx.channel.id,
                        'guild_id': ctx.guild.id if ctx.guild else None
                    })
            
            # تحديث البيانات المحلية للعرض
            sender_data['balance'] -= transfer_amount
            recipient_data['balance'] += transfer_amount
            
            # إنشاء رسالة نجاح التحويل
            embed = discord.Embed(
                title="✅ تم التحويل بنجاح",
                description=f"تم تحويل **{transfer_amount:,}** {self.currency_emoji} إلى {recipient.mention}.",
                color=discord.Color.green()
            )
            
            # إضافة معلومات الرصيد
            embed.add_field(
                name="💳 رصيدك الحالي",
                value=f"**{sender_data['balance']:,}** {self.currency_emoji}",
                inline=True
            )
            
            # إضافة صورة المستخدم
            embed.set_thumbnail(url=recipient.display_avatar.url)
            
            # إرسال الرسالة
            await ctx.send(embed=embed)
            
            # إرسال إشعار للمستلم إذا لم يكن في نفس القناة
            if recipient.id != ctx.author.id and ctx.channel.permissions_for(recipient).read_messages is False:
                try:
                    recipient_embed = discord.Embed(
                        title="💰 استلمت تحويلاً!",
                        description=f"استلمت **{transfer_amount:,}** {self.currency_emoji} من {ctx.author.mention}.",
                        color=discord.Color.gold()
                    )
                    recipient_embed.add_field(
                        name="💳 رصيدك الحالي",
                        value=f"**{recipient_data['balance']:,}** {self.currency_emoji}",
                        inline=True
                    )
                    await recipient.send(embed=recipient_embed)
                except:
                    # تجاهل إذا كان المستلم لا يقبل الرسائل الخاصة
                    pass
                
        except Exception as e:
            # في حالة حدوث خطأ، أرسل رسالة خطأ
            error_embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ أثناء عملية التحويل: {str(e)}",
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
    await bot.add_cog(Transfer(bot)) 