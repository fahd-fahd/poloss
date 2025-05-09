#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import random
import datetime

class Balance(commands.Cog):
    """نظام البنك والاقتصاد"""
    
    def __init__(self, bot):
        self.bot = bot
        self.default_balance = int(self.bot.config.get('bank', {}).get('initialBalance', 1000))
        self.currency_name = self.bot.config.get('bank', {}).get('currencyName', 'عملة')
        self.currency_emoji = self.bot.config.get('bank', {}).get('currencyEmoji', '💰')
    
    @commands.command(
        name="رصيد",
        aliases=["balance", "bal", "coins", "عملات"],
        description="عرض رصيدك الحالي في البنك"
    )
    async def balance(self, ctx, member: discord.Member = None):
        """
        عرض الرصيد الحالي للعضو
        
        المعلمات:
            member (discord.Member, اختياري): العضو المراد عرض رصيده، إذا لم يتم تحديده، يتم عرض رصيد المستخدم الحالي
        """
        # إذا لم يتم تحديد عضو، استخدم الشخص الذي أرسل الأمر
        target = member or ctx.author
        
        try:
            # جلب بيانات المستخدم من قاعدة البيانات
            user_data = await self._get_user_data(target.id)
            
            # إنشاء رسالة مضمنة لعرض الرصيد
            embed = discord.Embed(
                title=f"💳 رصيد {target.display_name}",
                color=0x43B581  # لون أخضر
            )
            
            # إضافة معلومات الرصيد
            embed.add_field(
                name=f"{self.currency_emoji} الرصيد الحالي",
                value=f"**{user_data['balance']:,}** {self.currency_name}",
                inline=False
            )
            
            # إذا كان هناك ملف شخصي مصرفي، أضف معلومات إضافية
            if 'bank_profile' in user_data:
                bank_profile = user_data['bank_profile']
                embed.add_field(
                    name="🏦 المستوى المصرفي",
                    value=f"**{bank_profile.get('level', 1)}**",
                    inline=True
                )
                
                # إضافة معلومات الإيداع اليومي
                daily_info = bank_profile.get('daily', {})
                last_daily = daily_info.get('last_claim', None)
                
                if last_daily:
                    # التحقق مما إذا كان يمكن المطالبة بالإيداع اليومي مرة أخرى
                    now = datetime.datetime.utcnow()
                    last_claim_date = datetime.datetime.fromisoformat(last_daily)
                    next_claim = last_claim_date + datetime.timedelta(days=1)
                    
                    if now >= next_claim:
                        daily_status = "✅ متاح الآن"
                    else:
                        # حساب الوقت المتبقي
                        remaining = next_claim - now
                        hours, remainder = divmod(remaining.seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        daily_status = f"⏳ متبقي {hours}:{minutes:02d}:{seconds:02d}"
                else:
                    daily_status = "✅ متاح الآن"
                
                embed.add_field(
                    name="📅 الإيداع اليومي",
                    value=daily_status,
                    inline=True
                )
            
            # إضافة الصورة الشخصية للمستخدم
            embed.set_thumbnail(url=target.display_avatar.url)
            
            # إضافة تذييل
            embed.set_footer(text=f"استخدم !مساعدة bank للحصول على قائمة أوامر البنك")
            
            # إرسال الرسالة المضمنة
            await ctx.send(embed=embed)
            
        except Exception as e:
            # في حالة حدوث خطأ، أرسل رسالة خطأ
            error_embed = discord.Embed(
                title="❌ خطأ في عرض الرصيد",
                description=f"حدث خطأ أثناء محاولة عرض الرصيد: {str(e)}",
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
                'balance': self.default_balance,
                'bank_profile': {
                    'level': 1,
                    'daily': {
                        'last_claim': None
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
                'balance': self.default_balance,
                'bank_profile': {
                    'level': 1,
                    'daily': {
                        'last_claim': None
                    }
                },
                'created_at': datetime.datetime.utcnow().isoformat()
            }
            # حفظ البيانات الجديدة في قاعدة البيانات
            await users_collection.insert_one(user_data)
        
        return user_data

async def setup(bot):
    """إعداد الأمر وإضافته إلى البوت"""
    await bot.add_cog(Balance(bot)) 