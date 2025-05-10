#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio

class Clear(commands.Cog):
    """أوامر الإدارة"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name="حذف",
        aliases=["clear", "مسح", "delete"],
        description="حذف عدد محدد من الرسائل من القناة"
    )
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = None):
        """
        حذف عدد محدد من الرسائل من القناة
        
        المعلمات:
            amount (int, اختياري): عدد الرسائل المراد حذفها. الافتراضي هو 5.
        """
        if amount is None:
            amount = 5
        
        # التحقق من صحة عدد الرسائل
        if amount <= 0:
            embed = discord.Embed(
                title="❌ خطأ",
                description="يجب أن يكون عدد الرسائل المراد حذفها أكبر من صفر.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # حذف رسالة الأمر أولاً
        await ctx.message.delete()
        
        # حذف الرسائل المحددة
        deleted = await ctx.channel.purge(limit=amount)
        
        # إرسال رسالة تأكيد قابلة للاختفاء بعد فترة
        confirmation = await ctx.send(
            embed=discord.Embed(
                title="✅ تم الحذف",
                description=f"تم حذف **{len(deleted)}** رسالة من قبل {ctx.author.mention}.",
                color=discord.Color.green()
            )
        )
        
        # حذف رسالة التأكيد بعد 3 ثوانٍ
        await asyncio.sleep(3)
        await confirmation.delete()
    
    @clear.error
    async def clear_error(self, ctx, error):
        """معالجة الأخطاء الخاصة بأمر الحذف"""
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ خطأ في الصلاحيات",
                description="ليس لديك الصلاحيات اللازمة لاستخدام هذا الأمر.\nتحتاج إلى صلاحية `إدارة الرسائل`.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="❌ خطأ في المعلمات",
                description="يرجى إدخال عدد صحيح للرسائل المراد حذفها.",
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

async def setup(bot):
    """إعداد الأمر وإضافته إلى البوت"""
    await bot.add_cog(Clear(bot)) 