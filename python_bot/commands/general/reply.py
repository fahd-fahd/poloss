#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands

class Reply(commands.Cog):
    """أوامر عامة"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name="رد",
        aliases=["reply", "رد_على", "r"],
        description="الرد على رسالة محددة"
    )
    async def reply_to_message(self, ctx, message_id: str = None, *, content: str = None):
        """
        الرد على رسالة محددة
        
        المعلمات:
            message_id (str): معرف الرسالة أو رابطها المراد الرد عليها
            content (str): محتوى الرد
        """
        # التحقق من وجود جميع المعلمات
        if not message_id:
            embed = discord.Embed(
                title="❌ خطأ في الأمر",
                description="يرجى تحديد معرف الرسالة المراد الرد عليها.\n"
                            "مثال: `!رد 123456789 مرحبًا بك!`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        if not content:
            embed = discord.Embed(
                title="❌ خطأ في الأمر",
                description="يرجى إدخال محتوى الرد.\n"
                            f"مثال: `!رد {message_id} مرحبًا بك!`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        try:
            # تنظيف معرف الرسالة إذا كان رابطًا
            if 'discord.com/channels/' in message_id:
                parts = message_id.split('/')
                message_id = parts[-1]
            
            # محاولة تحويل معرف الرسالة إلى رقم
            message_id = int(message_id)
            
            # البحث عن الرسالة
            target_message = None
            
            # البحث في القناة الحالية أولاً
            try:
                target_message = await ctx.channel.fetch_message(message_id)
            except discord.NotFound:
                # إذا لم يتم العثور على الرسالة في القناة الحالية، ابحث في القنوات الأخرى المتاحة
                for channel in ctx.guild.text_channels:
                    # تخطي القنوات التي لا يمكن للمستخدم رؤيتها
                    if not channel.permissions_for(ctx.author).read_messages:
                        continue
                    
                    try:
                        target_message = await channel.fetch_message(message_id)
                        if target_message:
                            break
                    except (discord.NotFound, discord.Forbidden):
                        continue
            
            # إذا لم يتم العثور على الرسالة
            if not target_message:
                embed = discord.Embed(
                    title="❌ خطأ",
                    description="لم يتم العثور على الرسالة المحددة. تأكد من أن معرف الرسالة صحيح وأن لديك الصلاحيات اللازمة.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
            
            # الرد على الرسالة المحددة
            await target_message.reply(content)
            
            # تأكيد نجاح العملية مع رابط القفز إلى الرسالة
            message_url = f"https://discord.com/channels/{ctx.guild.id}/{target_message.channel.id}/{target_message.id}"
            embed = discord.Embed(
                title="✅ تم الرد بنجاح",
                description=f"تم الرد على [الرسالة]({message_url}) بنجاح.",
                color=discord.Color.green()
            )
            
            # حذف رسالة الأمر (اختياري)
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass
            
            # إرسال تأكيد في قناة الأمر إذا كانت مختلفة عن قناة الرسالة
            if target_message.channel.id != ctx.channel.id:
                await ctx.send(embed=embed)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ خطأ",
                description="معرف الرسالة يجب أن يكون رقمًا صحيحًا أو رابطًا لرسالة.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ أثناء محاولة الرد على الرسالة: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    """إعداد الأمر وإضافته إلى البوت"""
    await bot.add_cog(Reply(bot)) 