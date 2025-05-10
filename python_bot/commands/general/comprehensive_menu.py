#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import sys
from pathlib import Path

# إضافة مسار البوت إلى مسار البحث
sys.path.append(str(Path(__file__).parent.parent.parent))

# استيراد وحدة الترجمة
try:
    from utils.translator import get_user_language, t
except ImportError:
    # دالة مؤقتة في حالة عدم وجود وحدة الترجمة
    def get_user_language(bot, user_id):
        return "ar"
    
    def t(key, language="ar"):
        return key

class ComprehensiveMenu(commands.Cog):
    """أمر القائمة الشاملة الذي يعرض جميع الأوامر في صفحة واحدة"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name="قائمة_كاملة",
        aliases=["cm", "all", "شامل", "quick", "سريع", "كامل"],
        description="عرض قائمة شاملة تحتوي على جميع الأوامر الأساسية في صفحة واحدة"
    )
    async def comprehensive_menu(self, ctx):
        """
        عرض قائمة شاملة لجميع الأوامر الأساسية في صفحة واحدة
        
        استخدم هذا الأمر لعرض جميع الأوامر الأساسية مباشرة بدون تنقل.
        """
        # تحديد اللغة المستخدمة
        language = get_user_language(self.bot, ctx.author.id)
        
        # إنشاء رسالة مضمنة للقائمة الشاملة
        embed = discord.Embed(
            title="⚡ القائمة الشاملة" if language == "ar" else "⚡ Comprehensive Menu",
            description="جميع الأوامر الأساسية في مكان واحد!" if language == "ar" else "All essential commands in one place!",
            color=discord.Color.purple()
        )
        
        # إضافة قسم الموسيقى
        embed.add_field(
            name="🎵 أوامر الموسيقى" if language == "ar" else "🎵 Music Commands",
            value="**!تشغيل** أو **!p** + رابط/اسم: تشغيل موسيقى\n"
                 "**!إيقاف** أو **!s**: إيقاف الموسيقى\n"
                 "**!تخطي** أو **!sk**: تخطي الأغنية الحالية\n"
                 "**!صوت** أو **!v** + رقم: ضبط مستوى الصوت\n"
                 "**!بحث** أو **!search** + كلمة: البحث عن أغنية" if language == "ar" else 
                 "**!play** or **!p** + link/name: Play music\n"
                 "**!stop** or **!s**: Stop music\n"
                 "**!skip** or **!sk**: Skip current song\n"
                 "**!volume** or **!v** + number: Adjust volume\n"
                 "**!search** + term: Search for a song",
            inline=False
        )
        
        # إضافة قسم البنك
        embed.add_field(
            name="💰 أوامر البنك" if language == "ar" else "💰 Bank Commands",
            value="**!رصيد** أو **!balance**: عرض رصيدك\n"
                 "**!يومي** أو **!daily**: المكافأة اليومية\n"
                 "**!تحويل** أو **!transfer**: تحويل أموال\n"
                 "**!حماية** أو **!protection**: حماية من السرقة\n"
                 "**!سرقة** أو **!steal**: محاولة سرقة شخص آخر" if language == "ar" else 
                 "**!balance**: View your balance\n"
                 "**!daily**: Get daily reward\n"
                 "**!transfer**: Transfer money\n"
                 "**!protection**: Protect from stealing\n"
                 "**!steal**: Try to steal from someone",
            inline=False
        )
        
        # إضافة قسم الألعاب
        embed.add_field(
            name="🎮 أوامر الألعاب" if language == "ar" else "🎮 Game Commands",
            value="**!صيد** أو **!fish**: لعبة الصيد\n"
                 "**!سباق** أو **!horserace**: سباق الخيول\n"
                 "**!نرد** أو **!dice**: لعبة النرد\n"
                 "**!بلاك_جاك** أو **!blackjack**: لعبة بلاك جاك" if language == "ar" else 
                 "**!fish**: Fishing game\n"
                 "**!horserace**: Horse racing\n"
                 "**!dice**: Dice game\n"
                 "**!blackjack**: Blackjack game",
            inline=False
        )
        
        # إضافة قسم الدعوات
        embed.add_field(
            name="🔗 أوامر الدعوات" if language == "ar" else "🔗 Invite Commands",
            value="**!دعوة** أو **!invite** + رابط: الانضمام لرابط دعوة\n"
                 "**!إنشاء_دعوة** أو **!create_invite**: إنشاء رابط دعوة" if language == "ar" else 
                 "**!invite** + link: Join an invite link\n"
                 "**!create_invite**: Create an invite link",
            inline=False
        )
        
        # إضافة قسم الاختصارات
        embed.add_field(
            name="⚡ اختصارات سريعة" if language == "ar" else "⚡ Quick Shortcuts",
            value="**!h**: القائمة التفاعلية\n"
                 "**!m**: هذه القائمة الشاملة" if language == "ar" else 
                 "**!h**: Interactive menu\n"
                 "**!m**: This comprehensive menu",
            inline=False
        )
        
        # إضافة صورة البوت
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        # إضافة تذييل
        embed.set_footer(
            text="استخدم الأمر !h للقائمة التفاعلية الكاملة" if language == "ar" else "Use !h command for the full interactive menu"
        )
        
        # إرسال القائمة
        await ctx.send(embed=embed)

async def setup(bot):
    """إضافة الصنف للبوت"""
    await bot.add_cog(ComprehensiveMenu(bot)) 