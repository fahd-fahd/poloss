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
            description="اختر أحد خيارات الموسيقى أدناه أو استخدم الأوامر المباشرة:",
            color=discord.Color.blurple()
        )
        
        # إضافة معلومات عن الأوامر المباشرة
        embed.add_field(
            name="🔊 الأوامر السريعة",
            value="**!تشغيل** أو **!p** + رابط/اسم أغنية: لتشغيل موسيقى\n"
                  "**!إيقاف** أو **!s**: لإيقاف الموسيقى\n"
                  "**!تخطي** أو **!sk**: لتخطي الأغنية الحالية\n"
                  "**!صوت** أو **!v**: للتحكم بالصوت",
            inline=False
        )
        
        embed.set_footer(text="يمكنك استخدام أزرار التنقل أدناه أو الأوامر المباشرة")
        
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
            description="اختر إحدى الألعاب أدناه أو استخدم الأوامر المباشرة:",
            color=discord.Color.green()
        )
        
        # إضافة معلومات عن الأوامر المباشرة
        embed.add_field(
            name="🎲 الأوامر السريعة",
            value="**!صيد** أو **!fish**: للعب الصيد\n"
                  "**!سباق** أو **!horserace**: للعب سباق الخيول\n"
                  "**!نرد** أو **!dice**: للعب النرد\n"
                  "**!بلاك_جاك** أو **!blackjack**: للعب بلاك جاك",
            inline=False
        )
        
        embed.set_footer(text="العب واربح المزيد من العملات!")
        
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
            description="اختر أحد خيارات البنك أدناه أو استخدم الأوامر المباشرة:",
            color=discord.Color.gold()
        )
        
        # إضافة معلومات عن الأوامر المباشرة
        embed.add_field(
            name="💵 الأوامر السريعة",
            value="**!رصيد** أو **!balance**: لعرض رصيدك\n"
                  "**!يومي** أو **!daily**: للحصول على المكافأة اليومية\n"
                  "**!تحويل** أو **!transfer**: لتحويل الأموال\n"
                  "**!حماية** أو **!protection**: لحماية أموالك\n"
                  "**!سرقة** أو **!steal**: لمحاولة سرقة الآخرين",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ نظام الحماية",
            value="استخدم **!حماية** لشراء حماية من السرقة بثلاثة مستويات:\n"
                  "- 3 ساعات مقابل 2500 عملة\n"
                  "- 8 ساعات مقابل 5000 عملة\n"
                  "- 24 ساعة مقابل 15000 عملة",
            inline=False
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
        embed = discord.Embed(
            title="🔗 انضمام لرابط دعوة",
            description="يرجى إدخال رابط الدعوة الذي تريد الانضمام إليه:",
            color=discord.Color.blue()
        )
        
        # إضافة تلميح للاستخدام المباشر
        embed.add_field(
            name="💡 تلميح",
            value="يمكنك استخدام `!دعوة` أو `!invite` مباشرة:\n"
                  "`!دعوة رابط_الدعوة`",
            inline=False
        )
        
        message = await interaction.followup.send(embed=embed)
        
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
        embed = discord.Embed(
            title="🎵 تشغيل موسيقى",
            description="أرسل رابط أو اسم الأغنية التي تريد تشغيلها.",
            color=discord.Color.green()
        )
        
        # إضافة تلميح للاستخدام المباشر
        embed.add_field(
            name="💡 تلميح سريع",
            value="في المرة القادمة، يمكنك استخدام:\n"
                 "`!p رابط_أو_اسم_الأغنية`\n"
                 "`!تشغيل رابط_أو_اسم_الأغنية`\n\n"
                 "البوت سينضم تلقائيًا للقناة الصوتية التي أنت فيها!",
            inline=False
        )
        
        # إضافة أمثلة للاستخدام
        embed.add_field(
            name="📝 أمثلة",
            value="`!p https://www.youtube.com/watch?v=dQw4w9WgXcQ`\n"
                 "`!تشغيل ديسباسيتو`\n"
                 "`!p أغنية عربية`",
            inline=False
        )
        
        message = await interaction.followup.send(embed=embed)
        
        # انتظار رد المستخدم
        try:
            response = await self.bot.wait_for(
                'message',
                check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id,
                timeout=60.0
            )
            
            # رسالة الانتظار
            wait_embed = discord.Embed(
                title="⏳ جاري التشغيل...",
                description=f"جاري تشغيل: `{response.content}`",
                color=discord.Color.blue()
            )
            
            wait_embed.set_footer(text="سيتم الانضمام تلقائيًا إلى القناة الصوتية الخاصة بك")
            
            await message.edit(embed=wait_embed)
            
            # تنفيذ أمر التشغيل
            play_command = self.bot.get_command('تشغيل') or self.bot.get_command('play')
            if play_command:
                ctx = await self.bot.get_context(response)
                await ctx.invoke(play_command, query=response.content)
                
                # حذف رسالة الطلب بعد التشغيل
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
                error_embed = discord.Embed(
                    title="❌ خطأ",
                    description="عذراً، أمر التشغيل غير متاح حالياً.",
                    color=discord.Color.red()
                )
                await message.edit(embed=error_embed)
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ انتهت المهلة",
                description="انتهت مهلة الانتظار. يرجى المحاولة مرة أخرى باستخدام `!p` أو `!تشغيل`",
                color=discord.Color.orange()
            )
            await message.edit(embed=timeout_embed)
    
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
        
        # إنشاء رسالة توضيحية
        embed = discord.Embed(
            title="🎣 لعبة الصيد",
            description="جاري بدء لعبة الصيد...",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="💡 تلميح",
            value="يمكنك استخدام الأمر `!صيد` أو `!fish` مباشرة في المرات القادمة!",
            inline=False
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
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
        
        # إنشاء رسالة توضيحية
        embed = discord.Embed(
            title="💵 عرض الرصيد",
            description="جاري عرض رصيدك...",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="💡 تلميح",
            value="يمكنك استخدام الأمر `!رصيد` أو `!balance` مباشرة في المرات القادمة!",
            inline=False
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
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
    
    @ui.button(label="🛡️ حماية", style=discord.ButtonStyle.success)
    async def protection_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر الحماية من السرقة"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة
        await interaction.message.delete()
        
        # تنفيذ أمر الحماية
        protection_command = self.bot.get_command('حماية') or self.bot.get_command('protection')
        if protection_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(protection_command)
        else:
            await interaction.followup.send("عذراً، أمر الحماية غير متاح حالياً.")
    
    @ui.button(label="🕵️ سرقة", style=discord.ButtonStyle.danger)
    async def steal_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر السرقة"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه القائمة ليست لك!", ephemeral=True)
        
        # إغلاق القائمة الحالية
        await interaction.message.delete()
        
        # إعداد أمر السرقة
        message = await interaction.followup.send("يرجى إدخال اسم المستخدم الذي تريد سرقته:")
        
        # انتظار رد المستخدم
        try:
            response = await self.bot.wait_for(
                'message',
                check=lambda m: m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id,
                timeout=30.0
            )
            
            # تنفيذ أمر السرقة
            steal_command = self.bot.get_command('سرقة') or self.bot.get_command('steal')
            if steal_command:
                ctx = await self.bot.get_context(response)
                
                # معالجة معلمات الأمر
                if len(response.content.strip()) > 0:
                    target = response.content.strip()
                    await ctx.invoke(steal_command, target=target)
                else:
                    await interaction.followup.send("يرجى تحديد اسم المستخدم للسرقة.")
                
                # حذف رسالة الطلب
                try:
                    await message.delete()
                except:
                    pass
            else:
                await interaction.followup.send("عذراً، أمر السرقة غير متاح حالياً.")
        except asyncio.TimeoutError:
            await message.edit(content="انتهت المهلة. يرجى المحاولة مرة أخرى.")
    
    @ui.button(label="🔙 رجوع", style=discord.ButtonStyle.secondary)
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
        
        # إضافة معلومات الفئات
        embed.add_field(
            name="🎵 الموسيقى",
            value="تشغيل الموسيقى والتحكم بالقنوات الصوتية",
            inline=True
        )
        
        embed.add_field(
            name="🎮 الألعاب",
            value="العاب متنوعة لربح العملات",
            inline=True
        )
        
        embed.add_field(
            name="💰 البنك",
            value="التحكم برصيدك والسرقة والحماية",
            inline=True
        )
        
        embed.add_field(
            name="🔗 الانضمام لرابط",
            value="الانضمام إلى روم من خلال رابط دعوة",
            inline=True
        )
        
        # إضافة معلومات إضافية
        embed.add_field(
            name="💡 استخدام سريع",
            value="يمكنك استخدام الأوامر مباشرة بدلاً من القائمة:\n"
                 "`!p` أو `!تشغيل`: لتشغيل موسيقى\n"
                 "`!رصيد`: لعرض رصيدك\n"
                 "`!سرقة @user`: لسرقة مستخدم\n"
                 "`!دعوة رابط`: للانضمام لرابط دعوة",
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