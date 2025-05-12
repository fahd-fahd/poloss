#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import os

# Add import for the ComprehensiveMenuView
from discord import ui

class Help(commands.Cog):
    """أوامر المساعدة والمعلومات"""
    
    def __init__(self, bot):
        self.bot = bot
        self.bot_name = self.bot.config.get('bot', {}).get('botName', 'Discord Bot')
    
    @commands.command(
        name="مساعدة",
        aliases=["help", "h", "commands", "أوامر"],
        description="عرض قائمة الأوامر المتاحة"
    )
    async def help(self, ctx, category=None):
        """
        عرض قائمة الأوامر المتاحة أو معلومات حول فئة محددة
        
        المعلمات:
            category (str, اختياري): اسم فئة الأوامر المراد عرض معلوماتها
        """
        # If category is None, always show the interactive menu
        if category is None:
            try:
                from commands.general.menu import ComprehensiveMenuView
                
                # Create embed for the comprehensive menu
                embed = discord.Embed(
                    title=f"🤖 مساعدة {self.bot_name}",
                    description="اختر مباشرة أحد الأزرار أدناه للوصول إلى الأوامر:",
                    color=discord.Color.blue()
                )
                
                # Add bot avatar if available
                if self.bot.user.avatar:
                    embed.set_thumbnail(url=self.bot.user.avatar.url)
                
                # Create and show the interactive button menu
                view = ComprehensiveMenuView(self.bot, ctx)
                message = await ctx.send(embed=embed, view=view)
                
                # Save message reference to the view
                view.message = message
                return
            except (ImportError, AttributeError) as e:
                # If there's an error importing ComprehensiveMenuView, log it and fall back to text
                print(f"Error displaying interactive menu: {str(e)}")
        
        # Fall back to text-based help for specific categories or if interactive menu is not available
        prefix = os.getenv("PREFIX", "!")
        
        if category is None:
            # إنشاء قائمة بجميع فئات الأوامر
            embed = discord.Embed(
                title=f"🤖 مساعدة {self.bot_name}",
                description=f"قائمة بجميع فئات الأوامر المتاحة. استخدم `{prefix}مساعدة [اسم الفئة]` لعرض الأوامر في فئة محددة.",
                color=discord.Color.blue()
            )
            
            # فرز الفئات أبجديًا
            sorted_categories = sorted(list(self.bot.categories))
            
            for cog_name in sorted_categories:
                # الحصول على وصف الفئة
                cog_description = f"أوامر {cog_name}"
                
                # الحصول على قائمة بأوامر هذه الفئة
                commands_list = []
                for command in self.bot.commands:
                    if command.cog and command.cog.qualified_name.lower() == cog_name.lower():
                        commands_list.append(command.name)
                
                if commands_list:
                    # عرض عدد الأوامر في كل فئة
                    embed.add_field(
                        name=f"📂 {cog_name.capitalize()} ({len(commands_list)})",
                        value=cog_description,
                        inline=False
                    )
            
            # إضافة معلومات التذييل
            embed.set_footer(text=f"عدد الفئات: {len(sorted_categories)} | إجمالي الأوامر: {len(self.bot.commands)}")
            
        else:
            # البحث عن الفئة المحددة
            category = category.lower()
            found = False
            
            for cog_name in self.bot.categories:
                if cog_name.lower() == category:
                    found = True
                    
                    # إنشاء قائمة بأوامر الفئة المحددة
                    embed = discord.Embed(
                        title=f"📂 أوامر فئة {cog_name.capitalize()}",
                        description=f"قائمة بجميع الأوامر المتاحة في فئة {cog_name}.",
                        color=discord.Color.green()
                    )
                    
                    # إضافة الأوامر
                    for command in self.bot.commands:
                        if command.cog and command.cog.qualified_name.lower() == cog_name.lower():
                            command_desc = command.description or command.help or "لا يوجد وصف"
                            embed.add_field(
                                name=f"{prefix}{command.name}",
                                value=command_desc,
                                inline=False
                            )
                    
                    # إضافة معلومات التذييل
                    command_count = sum(1 for cmd in self.bot.commands if cmd.cog and cmd.cog.qualified_name.lower() == cog_name.lower())
                    embed.set_footer(text=f"عدد الأوامر في هذه الفئة: {command_count}")
                    break
            
            if not found:
                # إذا لم يتم العثور على الفئة
                embed = discord.Embed(
                    title="❌ خطأ",
                    description=f"لم يتم العثور على فئة بالاسم '{category}'.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="الفئات المتاحة",
                    value="\n".join([f"• {cat}" for cat in sorted(list(self.bot.categories))]),
                    inline=False
                )
        
        # إضافة صورة Bot
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        await ctx.send(embed=embed)

async def setup(bot):
    """إعداد الأمر وإضافته إلى البوت"""
    await bot.add_cog(Help(bot)) 