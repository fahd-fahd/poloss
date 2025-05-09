#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import random
import asyncio
import datetime

class Fishing(commands.Cog):
    """لعبة صيد الأسماك"""
    
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}
        
        # تحميل إعدادات الصيد من التكوين
        self.config = self.bot.config.get('games', {})
        self.fishing_items = self.config.get('fishingItems', [
            {"name": "سمكة عادية", "value": 50, "chance": 0.5},
            {"name": "سمكة نادرة", "value": 150, "chance": 0.3},
            {"name": "سمكة نادرة جداً", "value": 500, "chance": 0.15},
            {"name": "كنز", "value": 1000, "chance": 0.05}
        ])
        
        # إعداد عناصر الصيد بناءً على قيم الفرص
        self.weighted_items = []
        for item in self.fishing_items:
            self.weighted_items.extend([item] * int(item["chance"] * 100))
    
    @commands.command(
        name="صيد",
        aliases=["fish", "fishing", "صيد_السمك"],
        description="صيد الأسماك للحصول على عملات"
    )
    async def fish(self, ctx):
        """
        لعبة صيد الأسماك للحصول على عملات
        """
        user_id = ctx.author.id
        
        # التحقق من فترة الانتظار
        if user_id in self.cooldowns:
            remaining = self.cooldowns[user_id] - datetime.datetime.utcnow()
            if remaining.total_seconds() > 0:
                minutes, seconds = divmod(int(remaining.total_seconds()), 60)
                await ctx.send(f"⏳ {ctx.author.mention} يرجى الانتظار **{minutes} دقيقة و {seconds} ثانية** قبل الصيد مرة أخرى.")
                return
        
        # إنشاء رسالة مضمنة
        embed = discord.Embed(
            title="🎣 لعبة صيد السمك",
            description="أنت تلقي بصنارتك في الماء...",
            color=discord.Color.blue()
        )
        
        # إضافة صورة العضو
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        # إرسال الرسالة المضمنة
        message = await ctx.send(embed=embed)
        
        # إضافة رموز انتظار للتفاعل
        for i in range(3):
            embed.description = f"أنت تلقي بصنارتك في الماء{'.' * (i + 1)}"
            await message.edit(embed=embed)
            await asyncio.sleep(1)
        
        # تحديد ما تم اصطياده
        caught_item = random.choice(self.weighted_items)
        
        # تحديث الرسالة المضمنة
        embed.title = f"🎣 {ctx.author.display_name} اصطاد شيئاً!"
        embed.description = f"لقد اصطدت **{caught_item['name']}**!\nقيمتها: **{caught_item['value']}** {self.bot.config.get('bank', {}).get('currencyEmoji', '💰')}"
        embed.color = discord.Color.green()
        
        # إضافة التذييل
        embed.set_footer(text="يمكنك استخدام الأمر مرة أخرى بعد 5 دقائق")
        
        await message.edit(embed=embed)
        
        # تعيين فترة الانتظار (5 دقائق)
        self.cooldowns[user_id] = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        
        # إضافة العملات إلى رصيد المستخدم
        try:
            if hasattr(self.bot, 'db'):
                user_collection = self.bot.db.users
                result = await user_collection.update_one(
                    {"user_id": user_id},
                    {"$inc": {"balance": caught_item['value']}},
                    upsert=True
                )
                
                if result.modified_count == 0 and result.upserted_id is None:
                    # إذا لم يتم العثور على المستخدم وعدم وجود upsert، إنشاء وثيقة جديدة
                    default_balance = self.bot.config.get('bank', {}).get('initialBalance', 1000)
                    await user_collection.insert_one({
                        "user_id": user_id,
                        "balance": default_balance + caught_item['value'],
                        "created_at": datetime.datetime.utcnow().isoformat()
                    })
        except Exception as e:
            # في حالة حدوث خطأ، سجل الخطأ ولكن استمر
            print(f"خطأ في تحديث رصيد المستخدم: {str(e)}")

async def setup(bot):
    """إعداد الأمر وإضافته إلى البوت"""
    await bot.add_cog(Fishing(bot)) 