#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import re

class InviteHandler(commands.Cog):
    """معالج روابط الدعوة"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name="دعوة",
        aliases=["invite", "join", "انضمام"],
        description="معالجة رابط دعوة ديسكورد"
    )
    async def join_invite(self, ctx, invite_link: str = None):
        """
        معالجة رابط دعوة ديسكورد
        
        المعلمات:
            invite_link (str): رابط الدعوة المراد الانضمام إليه
        """
        # حذف رسالة الأمر للحفاظ على نظافة القناة
        try:
            await ctx.message.delete()
        except:
            pass
        
        # التحقق من وجود رابط
        if not invite_link:
            embed = discord.Embed(
                title="❌ خطأ في الأمر",
                description="يرجى تحديد رابط الدعوة.\n"
                            "مثال: `!دعوة https://discord.gg/example`",
                color=discord.Color.red()
            )
            message = await ctx.send(embed=embed)
            # حذف رسالة الخطأ بعد 5 ثوانٍ
            await message.delete(delay=5)
            return
        
        # البحث عن كود الدعوة في الرابط
        discord_invite_pattern = r'(?:https?://)?(?:www\.)?discord(?:app)?\.(?:com/invite|gg)/([a-zA-Z0-9-]+)'
        match = re.search(discord_invite_pattern, invite_link)
        
        if not match:
            embed = discord.Embed(
                title="❌ رابط غير صالح",
                description="الرابط المدخل ليس رابط دعوة ديسكورد صالح.\n"
                            "يجب أن يكون بصيغة: `https://discord.gg/example`",
                color=discord.Color.red()
            )
            message = await ctx.send(embed=embed)
            # حذف رسالة الخطأ بعد 5 ثوانٍ
            await message.delete(delay=5)
            return
        
        invite_code = match.group(1)
        
        # محاولة الحصول على معلومات الدعوة
        try:
            invite = await self.bot.fetch_invite(invite_code)
            
            # إنشاء رسالة تأكيد مع معلومات الدعوة
            embed = discord.Embed(
                title="🔗 معلومات الدعوة",
                description=f"تم العثور على دعوة إلى **{invite.guild.name}**",
                color=discord.Color.blue()
            )
            
            # إضافة المعلومات
            embed.add_field(
                name="👥 عدد الأعضاء",
                value=f"{invite.approximate_member_count:,} عضو",
                inline=True
            )
            
            embed.add_field(
                name="🌐 قناة الدعوة",
                value=f"#{invite.channel.name}" if hasattr(invite.channel, 'name') else "قناة خاصة",
                inline=True
            )
            
            # إضافة رابط القفز إلى الدعوة
            embed.url = invite_link
            
            # إضافة صورة السيرفر
            if invite.guild.icon:
                embed.set_thumbnail(url=invite.guild.icon.url)
            
            # إنشاء أزرار التفاعل
            join_view = JoinInviteView(ctx.author, invite_link)
            
            # إرسال رسالة التأكيد
            message = await ctx.send(embed=embed, view=join_view)
            
            # حفظ رسالة التأكيد في كائن الأزرار
            join_view.message = message
            
        except discord.NotFound:
            embed = discord.Embed(
                title="❌ دعوة غير موجودة",
                description="لم يتم العثور على الدعوة المحددة. قد تكون منتهية الصلاحية أو غير صالحة.",
                color=discord.Color.red()
            )
            message = await ctx.send(embed=embed)
            # حذف رسالة الخطأ بعد 5 ثوانٍ
            await message.delete(delay=5)
        
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ خطأ في الصلاحيات",
                description="ليس لدي صلاحية للوصول إلى معلومات هذه الدعوة.",
                color=discord.Color.red()
            )
            message = await ctx.send(embed=embed)
            # حذف رسالة الخطأ بعد 5 ثوانٍ
            await message.delete(delay=5)
        
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ أثناء معالجة الدعوة: {str(e)}",
                color=discord.Color.red()
            )
            message = await ctx.send(embed=embed)
            # حذف رسالة الخطأ بعد 5 ثوانٍ
            await message.delete(delay=5)


class JoinInviteView(discord.ui.View):
    """واجهة أزرار الانضمام للدعوة"""
    
    def __init__(self, author, invite_link, timeout=60):
        super().__init__(timeout=timeout)
        self.author = author
        self.invite_link = invite_link
        self.message = None
    
    @discord.ui.button(label="✅ انضمام", style=discord.ButtonStyle.success)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر الانضمام للدعوة"""
        # التحقق من المستخدم
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("هذه الدعوة ليست لك!", ephemeral=True)
        
        # فتح الرابط للمستخدم
        await interaction.response.send_message(
            f"انقر هنا للانضمام: {self.invite_link}\n"
            "(سيتم حذف هذه الرسالة خلال 15 ثانية)",
            ephemeral=True,
            delete_after=15
        )
        
        # حذف رسالة التأكيد
        await self.message.delete()
    
    @discord.ui.button(label="❌ إلغاء", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر إلغاء الدعوة"""
        # التحقق من المستخدم
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("هذه الدعوة ليست لك!", ephemeral=True)
        
        # حذف رسالة التأكيد
        await interaction.response.defer()
        await self.message.delete()
    
    async def on_timeout(self):
        """إجراء انتهاء المهلة"""
        # حذف الرسالة عند انتهاء المهلة
        if self.message:
            try:
                await self.message.delete()
            except:
                pass


async def setup(bot):
    """إعداد الأمر وإضافته إلى البوت"""
    await bot.add_cog(InviteHandler(bot)) 