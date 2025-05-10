#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
from discord import ui

class MainMenuView(ui.View):
    """واجهة القائمة الرئيسية التفاعلية"""
    
    def __init__(self, bot, ctx, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
    
    @ui.button(label="🎵 الموسيقى", style=discord.ButtonStyle.primary)
    async def music_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر قائمة الموسيقى"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إنشاء قائمة الموسيقى
        music_view = MusicMenuView(self.bot, self.ctx)
        
        # تحديث الرسالة بقائمة الموسيقى
        embed = discord.Embed(
            title="🎵 قائمة الموسيقى",
            description="اختر أحد خيارات الموسيقى أدناه:",
            color=discord.Color.blurple()
        )
        await interaction.response.edit_message(embed=embed, view=music_view)
    
    @ui.button(label="🎮 الألعاب", style=discord.ButtonStyle.success)
    async def games_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر قائمة الألعاب"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إنشاء قائمة الألعاب
        games_view = GamesMenuView(self.bot, self.ctx)
        
        # تحديث الرسالة بقائمة الألعاب
        embed = discord.Embed(
            title="🎮 قائمة الألعاب",
            description="اختر إحدى الألعاب أدناه:",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=games_view)
    
    @ui.button(label="💰 البنك", style=discord.ButtonStyle.secondary)
    async def bank_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر قائمة البنك"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إنشاء قائمة البنك
        bank_view = BankMenuView(self.bot, self.ctx)
        
        # تحديث الرسالة بقائمة البنك
        embed = discord.Embed(
            title="💰 قائمة البنك",
            description="اختر أحد خيارات البنك أدناه:",
            color=discord.Color.gold()
        )
        await interaction.response.edit_message(embed=embed, view=bank_view)
    
    @ui.button(label="🔗 انضمام لرابط", style=discord.ButtonStyle.primary)
    async def join_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر الانضمام لرابط دعوة"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # حذف رسالة القائمة
        await interaction.message.delete()
        
        # إعداد أمر الدعوة
        message = await interaction.followup.send("يرجى إدخال رابط الدعوة الذي تريد الانضمام إليه:")
        
        # انتظار رد المستخدم
        try:
            response = await self.bot.wait_for(
                'message',
                check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id,
                timeout=30.0
            )
            
            # تنفيذ أمر الدعوة
            invite_command = self.bot.get_command('دعوة') or self.bot.get_command('invite')
            if invite_command:
                ctx = await self.bot.get_context(response)
                await ctx.invoke(invite_command, invite_link=response.content)
                
                # حذف رسالة الطلب
                try:
                    await message.delete()
                except:
                    pass
                
                # حذف رسالة المستخدم
                try:
                    await response.delete()
                except:
                    pass
            else:
                await interaction.followup.send("عذراً، أمر الانضمام غير متاح حالياً.")
        except asyncio.TimeoutError:
            await message.edit(content="انتهت المهلة. يرجى المحاولة مرة أخرى.")
    
    @ui.button(label="❌ إغلاق", style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر إغلاق القائمة"""
        # التحقق من المستخدم
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # حذف الرسالة
        await interaction.message.delete()
    
    async def on_timeout(self):
        """عند انتهاء مهلة القائمة"""
        # تعطيل جميع الأزرار
        for item in self.children:
            item.disabled = True
        
        # تحديث الرسالة
        try:
            await self.message.edit(view=self)
        except:
            pass


class MusicMenuView(ui.View):
    """واجهة قائمة الموسيقى التفاعلية"""
    
    def __init__(self, bot, ctx, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
    
    @ui.button(label="▶️ تشغيل", style=discord.ButtonStyle.primary)
    async def play_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر تشغيل الموسيقى"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.message.delete()
        
        # إعداد أمر التشغيل
        message = await interaction.followup.send("يرجى كتابة اسم الأغنية أو رابط YouTube للتشغيل:")
        
        # انتظار رد المستخدم
        try:
            response = await self.bot.wait_for(
                'message',
                check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id,
                timeout=30.0
            )
            
            # تنفيذ أمر التشغيل
            play_command = self.bot.get_command('تشغيل') or self.bot.get_command('play')
            if play_command:
                ctx = await self.bot.get_context(response)
                await ctx.invoke(play_command, query=response.content)
                
                # حذف رسالة الطلب
                try:
                    await message.delete()
                except:
                    pass
            else:
                await interaction.followup.send("عذراً، أمر التشغيل غير متاح حالياً.")
        except asyncio.TimeoutError:
            await message.edit(content="انتهت المهلة. يرجى المحاولة مرة أخرى.")
    
    @ui.button(label="⏹️ إيقاف", style=discord.ButtonStyle.secondary)
    async def stop_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر إيقاف الموسيقى"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة
        await interaction.message.delete()
        
        # تنفيذ أمر الإيقاف
        stop_command = self.bot.get_command('إيقاف') or self.bot.get_command('stop')
        if stop_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(stop_command)
        else:
            await interaction.followup.send("عذراً، أمر الإيقاف غير متاح حالياً.")
    
    @ui.button(label="⏭️ تخطي", style=discord.ButtonStyle.secondary)
    async def skip_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر تخطي الأغنية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة
        await interaction.message.delete()
        
        # تنفيذ أمر التخطي
        skip_command = self.bot.get_command('تخطي') or self.bot.get_command('skip')
        if skip_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(skip_command)
        else:
            await interaction.followup.send("عذراً، أمر التخطي غير متاح حالياً.")
    
    @ui.button(label="🔍 بحث", style=discord.ButtonStyle.primary)
    async def search_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر البحث عن موسيقى"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.message.delete()
        
        # إعداد أمر البحث
        message = await interaction.followup.send("يرجى كتابة اسم الأغنية للبحث عنها:")
        
        # انتظار رد المستخدم
        try:
            response = await self.bot.wait_for(
                'message',
                check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id,
                timeout=30.0
            )
            
            # تنفيذ أمر البحث
            search_command = self.bot.get_command('بحث') or self.bot.get_command('search')
            if search_command:
                ctx = await self.bot.get_context(response)
                await ctx.invoke(search_command, query=response.content)
                
                # حذف رسالة الطلب
                try:
                    await message.delete()
                except:
                    pass
            else:
                await interaction.followup.send("عذراً، أمر البحث غير متاح حالياً.")
        except asyncio.TimeoutError:
            await message.edit(content="انتهت المهلة. يرجى المحاولة مرة أخرى.")
    
    @ui.button(label="🔙 رجوع", style=discord.ButtonStyle.danger)
    async def back_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر الرجوع للقائمة الرئيسية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # العودة إلى القائمة الرئيسية
        main_view = MainMenuView(self.bot, self.ctx)
        
        # تحديث الرسالة بالقائمة الرئيسية
        embed = discord.Embed(
            title="🤖 القائمة الرئيسية",
            description="اختر أحد الخيارات أدناه:",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=main_view)


class GamesMenuView(ui.View):
    """واجهة قائمة الألعاب التفاعلية"""
    
    def __init__(self, bot, ctx, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
    
    @ui.button(label="🎣 صيد", style=discord.ButtonStyle.primary)
    async def fishing_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة الصيد"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة
        await interaction.message.delete()
        
        # تنفيذ أمر الصيد
        fishing_command = self.bot.get_command('صيد') or self.bot.get_command('fish')
        if fishing_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(fishing_command)
        else:
            await interaction.followup.send("عذراً، لعبة الصيد غير متاحة حالياً.")
    
    @ui.button(label="🏇 سباق الخيول", style=discord.ButtonStyle.primary)
    async def horserace_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة سباق الخيول"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة
        await interaction.message.delete()
        
        # تنفيذ أمر سباق الخيول
        horserace_command = self.bot.get_command('سباق') or self.bot.get_command('horserace')
        if horserace_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(horserace_command)
        else:
            await interaction.followup.send("عذراً، لعبة سباق الخيول غير متاحة حالياً.")
    
    @ui.button(label="🎲 النرد", style=discord.ButtonStyle.primary)
    async def dice_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة النرد"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة
        await interaction.message.delete()
        
        # تنفيذ أمر النرد
        dice_command = self.bot.get_command('نرد') or self.bot.get_command('dice')
        if dice_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(dice_command)
        else:
            await interaction.followup.send("عذراً، لعبة النرد غير متاحة حالياً.")
    
    @ui.button(label="🃏 بلاك جاك", style=discord.ButtonStyle.primary)
    async def blackjack_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة بلاك جاك"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة
        await interaction.message.delete()
        
        # تنفيذ أمر بلاك جاك
        blackjack_command = self.bot.get_command('بلاك_جاك') or self.bot.get_command('blackjack')
        if blackjack_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(blackjack_command)
        else:
            await interaction.followup.send("عذراً، لعبة بلاك جاك غير متاحة حالياً.")
    
    @ui.button(label="🔙 رجوع", style=discord.ButtonStyle.danger)
    async def back_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر الرجوع للقائمة الرئيسية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # العودة إلى القائمة الرئيسية
        main_view = MainMenuView(self.bot, self.ctx)
        
        # تحديث الرسالة بالقائمة الرئيسية
        embed = discord.Embed(
            title="🤖 القائمة الرئيسية",
            description="اختر أحد الخيارات أدناه:",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=main_view)


class BankMenuView(ui.View):
    """واجهة قائمة البنك التفاعلية"""
    
    def __init__(self, bot, ctx, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
    
    @ui.button(label="💵 الرصيد", style=discord.ButtonStyle.primary)
    async def balance_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر عرض الرصيد"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة
        await interaction.message.delete()
        
        # تنفيذ أمر الرصيد
        balance_command = self.bot.get_command('رصيد') or self.bot.get_command('balance')
        if balance_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(balance_command)
        else:
            await interaction.followup.send("عذراً، أمر الرصيد غير متاح حالياً.")
    
    @ui.button(label="🎁 المكافأة اليومية", style=discord.ButtonStyle.primary)
    async def daily_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر المكافأة اليومية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة
        await interaction.message.delete()
        
        # تنفيذ أمر المكافأة اليومية
        daily_command = self.bot.get_command('يومي') or self.bot.get_command('daily')
        if daily_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(daily_command)
        else:
            await interaction.followup.send("عذراً، أمر المكافأة اليومية غير متاح حالياً.")
    
    @ui.button(label="💸 تحويل", style=discord.ButtonStyle.primary)
    async def transfer_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر التحويل"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.message.delete()
        
        # إعداد أمر التحويل
        message = await interaction.followup.send("يرجى إدخال اسم المستخدم والمبلغ للتحويل (مثال: @User 100):")
        
        # انتظار رد المستخدم
        try:
            response = await self.bot.wait_for(
                'message',
                check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id,
                timeout=30.0
            )
            
            # تنفيذ أمر التحويل
            transfer_command = self.bot.get_command('تحويل') or self.bot.get_command('transfer')
            if transfer_command:
                ctx = await self.bot.get_context(response)
                
                # معالجة معلمات الأمر
                args = response.content.split()
                if len(args) >= 2:
                    recipient = args[0]
                    amount = args[1]
                    
                    await ctx.invoke(transfer_command, recipient=recipient, amount=amount)
                else:
                    await interaction.followup.send("الصيغة غير صحيحة. يرجى استخدام الصيغة: @User 100")
                
                # حذف رسالة الطلب
                try:
                    await message.delete()
                except:
                    pass
            else:
                await interaction.followup.send("عذراً، أمر التحويل غير متاح حالياً.")
        except asyncio.TimeoutError:
            await message.edit(content="انتهت المهلة. يرجى المحاولة مرة أخرى.")
    
    @ui.button(label="🔙 رجوع", style=discord.ButtonStyle.danger)
    async def back_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر الرجوع للقائمة الرئيسية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # العودة إلى القائمة الرئيسية
        main_view = MainMenuView(self.bot, self.ctx)
        
        # تحديث الرسالة بالقائمة الرئيسية
        embed = discord.Embed(
            title="🤖 القائمة الرئيسية",
            description="اختر أحد الخيارات أدناه:",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=main_view)


class Menu(commands.Cog):
    """أوامر القوائم التفاعلية"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name="h",
        aliases=["menu", "قائمة"],
        description="عرض قائمة تفاعلية للأوامر"
    )
    async def menu(self, ctx):
        """
        عرض قائمة تفاعلية للأوامر
        
        استخدم هذا الأمر لعرض واجهة تفاعلية سهلة الاستخدام للوصول إلى جميع أوامر البوت.
        """
        # إنشاء نص القائمة الرئيسية
        embed = discord.Embed(
            title="🤖 القائمة الرئيسية",
            description="مرحبًا! اختر أحد الخيارات أدناه للوصول إلى الأوامر:",
            color=discord.Color.blue()
        )
        
        # إضافة معلومات إضافية
        embed.add_field(
            name="💡 معلومة",
            value="استخدم الأزرار أدناه للتنقل بين القوائم المختلفة.",
            inline=False
        )
        
        # إضافة صورة البوت
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        # إنشاء كائن القائمة
        view = MainMenuView(self.bot, ctx)
        
        # إرسال الرسالة مع القائمة
        message = await ctx.send(embed=embed, view=view)
        
        # حفظ الرسالة في كائن القائمة لاستخدامها لاحقًا
        view.message = message


async def setup(bot):
    """إعداد الأمر وإضافته إلى البوت"""
    # استيراد asyncio هنا لتجنب مشاكل الاستيراد الدائري
    import asyncio
    
    # إضافة asyncio كمتغير عالمي للوحدة
    globals()['asyncio'] = asyncio
    
    # إضافة الأمر للبوت
    await bot.add_cog(Menu(bot)) 