#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import random
import asyncio
import datetime
from discord import ui

class EnhancedGamesView(ui.View):
    """واجهة محسنة للألعاب تعرض جميع أزرار الألعاب في مكان واحد"""
    
    def __init__(self, bot, ctx, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
        self.message = None
    
    @ui.button(label="🎣 لعبة الصيد", style=discord.ButtonStyle.primary, emoji="🎣", row=0)
    async def fishing_game_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة الصيد"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الواجهة ليست لك!", ephemeral=True)
        
        # تنفيذ لعبة الصيد بشكل تفاعلي
        await interaction.response.defer(ephemeral=False)
        
        # الحصول على معلومات المستخدم
        user_id = interaction.user.id
        
        # الحصول على كوغ لعبة الصيد للتحقق من فترات الانتظار
        fishing_cog = self.bot.get_cog("Fishing")
        if not fishing_cog:
            return await interaction.followup.send("❌ عذراً، لعبة الصيد غير متاحة حالياً.")
        
        # التحقق من فترة الانتظار
        if hasattr(fishing_cog, 'cooldowns') and user_id in fishing_cog.cooldowns:
            remaining = fishing_cog.cooldowns[user_id] - datetime.datetime.utcnow()
            if remaining.total_seconds() > 0:
                minutes, seconds = divmod(int(remaining.total_seconds()), 60)
                await interaction.followup.send(f"⏳ {interaction.user.mention} يرجى الانتظار **{minutes} دقيقة و {seconds} ثانية** قبل الصيد مرة أخرى.", ephemeral=True)
                return
        
        # إضافة تأثيرات رسومية محسنة للصيد
        embed = discord.Embed(
            title="🎣 لعبة صيد السمك المطورة",
            description="أنت تلقي بصنارتك في المحيط... ✨",
            color=discord.Color.blue()
        )
        
        # إضافة صورة العضو
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        # إرسال الرسالة المضمنة
        fishing_message = await interaction.followup.send(embed=embed)
        
        # إضافة رموز انتظار للتفاعل مع تحسينات بصرية
        fishing_stages = [
            "🌊 أنت تلقي بصنارتك في المحيط الأزرق...",
            "🌊 الماء يتحرك... شيء ما يقترب! 👀",
            "🌊 سمكة كبيرة تسبح بالقرب من الصنارة! 🐟",
            "🌊 تشعر بشد قوي على الصنارة...! 🎣"
        ]
        
        for stage in fishing_stages:
            embed.description = stage
            await fishing_message.edit(embed=embed)
            await asyncio.sleep(1)
        
        # تحديد ما تم اصطياده بنظام محسن
        fishing_items = fishing_cog.fishing_items if hasattr(fishing_cog, 'fishing_items') else [
            {"name": "سمكة عادية", "value": 50, "chance": 0.5, "emoji": "🐟"},
            {"name": "سمكة نادرة", "value": 150, "chance": 0.3, "emoji": "🐠"},
            {"name": "سمكة نادرة جداً", "value": 500, "chance": 0.15, "emoji": "🦑"},
            {"name": "كنز", "value": 1000, "chance": 0.05, "emoji": "💎"},
            {"name": "سمكة ذهبية", "value": 2000, "chance": 0.03, "emoji": "🐡"},
            {"name": "وحش بحري", "value": 3000, "chance": 0.01, "emoji": "🐙"},
            {"name": "تاج ملكي", "value": 5000, "chance": 0.005, "emoji": "👑"}
        ]
        
        # إضافة الرموز التعبيرية إذا لم تكن موجودة
        for item in fishing_items:
            if "emoji" not in item:
                if "عادية" in item["name"]:
                    item["emoji"] = "🐟"
                elif "نادرة" in item["name"] and "جداً" not in item["name"]:
                    item["emoji"] = "🐠"
                elif "نادرة جداً" in item["name"]:
                    item["emoji"] = "🦑"
                elif "كنز" in item["name"]:
                    item["emoji"] = "💎"
                elif "ذهبية" in item["name"]:
                    item["emoji"] = "🐡"
                elif "وحش" in item["name"]:
                    item["emoji"] = "🐙"
                else:
                    item["emoji"] = "🎣"
        
        # اختيار عنصر بناءً على قيم الفرص
        weights = [item["chance"] for item in fishing_items]
        caught_item = random.choices(fishing_items, weights=weights, k=1)[0]
        
        # تحديث الرسالة المضمنة مع تأثيرات بصرية محسنة
        embed.title = f"🎣 {interaction.user.display_name} اصطاد شيئاً رائعاً!"
        embed.description = f"**{caught_item['emoji']} لقد اصطدت {caught_item['name']}!**\n\nقيمتها: **{caught_item['value']}** {self.bot.config.get('bank', {}).get('currencyEmoji', '💰')}"
        embed.color = discord.Color.gold()
        
        # إضافة تأثيرات إضافية بناءً على قيمة العنصر المصطاد
        if caught_item["value"] >= 1000:
            embed.description += "\n\n🎉 **مبارك!** لقد اصطدت عنصراً نادراً!"
            
        if caught_item["value"] >= 3000:
            embed.description += "\n🔥 **رائع جداً!** هذا نادر حقاً!"
            
        # إظهار فرصة الصيد
        chance_percentage = caught_item["chance"] * 100
        if chance_percentage < 1:
            chance_text = f"{chance_percentage:.2f}%"
        else:
            chance_text = f"{chance_percentage:.0f}%"
            
        embed.add_field(name="فرصة الصيد", value=f"{chance_text}", inline=True)
        
        # إضافة التذييل
        cooldown_minutes = 5  # فترة الانتظار الافتراضية
        embed.set_footer(text=f"يمكنك استخدام اللعبة مرة أخرى بعد {cooldown_minutes} دقائق")
        
        await fishing_message.edit(embed=embed)
        
        # تعيين فترة الانتظار (5 دقائق)
        if hasattr(fishing_cog, 'cooldowns'):
            fishing_cog.cooldowns[user_id] = datetime.datetime.utcnow() + datetime.timedelta(minutes=cooldown_minutes)
        
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
    
    @ui.button(label="🎲 لعبة النرد", style=discord.ButtonStyle.primary, emoji="🎲", row=0)
    async def dice_game_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة النرد المطورة"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الواجهة ليست لك!", ephemeral=True)
        
        # إنشاء مودال للعبة النرد لاختيار نوع الرهان والمبلغ
        class DiceModal(ui.Modal, title="لعبة النرد 🎲"):
            bet_type = ui.TextInput(
                label="نوع الرهان (عالي/منخفض/رقم من 1-6)",
                placeholder="مثال: عالي أو 6",
                required=True
            )
            
            bet_amount = ui.TextInput(
                label="المبلغ",
                placeholder="مثال: 100 أو كل",
                required=True
            )
            
            async def on_submit(self, dice_interaction: discord.Interaction):
                # التحقق من صحة المدخلات
                try:
                    amount = self.bet_amount.value.lower()
                    
                    # الحصول على رصيد المستخدم
                    user_id = dice_interaction.user.id
                    user_balance = 1000  # قيمة افتراضية
                    
                    try:
                        if hasattr(self.view.bot, 'db'):
                            user_doc = await self.view.bot.db.users.find_one({"user_id": user_id})
                            if user_doc:
                                user_balance = user_doc.get("balance", 1000)
                    except Exception as e:
                        print(f"خطأ في الحصول على رصيد المستخدم: {str(e)}")
                    
                    # معالجة مبلغ الرهان
                    if amount == "كل" or amount == "all":
                        bet_amount = user_balance
                    else:
                        try:
                            bet_amount = int(amount)
                        except ValueError:
                            return await dice_interaction.response.send_message(
                                "❌ المبلغ غير صحيح. يجب أن يكون رقماً أو 'كل'.",
                                ephemeral=True
                            )
                    
                    # التحقق من الرصيد
                    if bet_amount <= 0:
                        return await dice_interaction.response.send_message(
                            "❌ يجب أن يكون المبلغ أكبر من صفر.",
                            ephemeral=True
                        )
                    
                    if bet_amount > user_balance:
                        return await dice_interaction.response.send_message(
                            f"❌ ليس لديك رصيد كافٍ. رصيدك الحالي: {user_balance}",
                            ephemeral=True
                        )
                    
                    # التحقق من نوع الرهان
                    choice = self.bet_type.value.lower()
                    valid_choice = False
                    
                    if choice in ["عالي", "high", "h", "مرتفع"]:
                        bet_type = "high"
                        bet_name = "الأرقام العالية (4-6)"
                        valid_choice = True
                        win_range = [4, 5, 6]
                    elif choice in ["منخفض", "low", "l", "منخفض"]:
                        bet_type = "low"
                        bet_name = "الأرقام المنخفضة (1-3)"
                        valid_choice = True
                        win_range = [1, 2, 3]
                    elif choice.isdigit() and 1 <= int(choice) <= 6:
                        bet_type = "number"
                        bet_number = int(choice)
                        bet_name = f"الرقم {choice}"
                        valid_choice = True
                        win_range = [bet_number]
                    
                    if not valid_choice:
                        return await dice_interaction.response.send_message(
                            "❌ نوع الرهان غير صحيح. يجب أن يكون 'عالي'، 'منخفض'، أو رقم من 1 إلى 6.",
                            ephemeral=True
                        )
                    
                    # بدء لعبة النرد
                    await dice_interaction.response.defer(ephemeral=False)
                    
                    # إنشاء رسالة مضمنة للعبة
                    embed = discord.Embed(
                        title="🎲 لعبة النرد",
                        description=f"{dice_interaction.user.mention} راهن على **{bet_name}** بمبلغ **{bet_amount}**",
                        color=discord.Color.blue()
                    )
                    
                    # عرض الرسالة الأولية
                    dice_message = await dice_interaction.followup.send(embed=embed)
                    
                    # تقليب النرد (تأثير بصري)
                    for i in range(3):
                        embed.description = f"{dice_interaction.user.mention} راهن على **{bet_name}** بمبلغ **{bet_amount}**\n\n🎲 النرد يتقلب..."
                        await dice_message.edit(embed=embed)
                        await asyncio.sleep(1)
                    
                    # تحديد نتيجة النرد
                    dice_result = random.randint(1, 6)
                    dice_emoji = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"][dice_result - 1]
                    
                    # تحديد النتيجة
                    win = dice_result in win_range
                    
                    # حساب المكسب/الخسارة
                    if bet_type == "number":
                        # الرهان على رقم محدد يعطي مكافأة أكبر (5 أضعاف)
                        win_amount = bet_amount * 5 if win else -bet_amount
                    else:
                        # الرهان على عالي/منخفض يعطي ضعف المبلغ
                        win_amount = bet_amount if win else -bet_amount
                    
                    # تحديث الرصيد
                    try:
                        if hasattr(self.view.bot, 'db'):
                            await self.view.bot.db.users.update_one(
                                {"user_id": user_id},
                                {"$inc": {"balance": win_amount}},
                                upsert=True
                            )
                    except Exception as e:
                        print(f"خطأ في تحديث رصيد المستخدم: {str(e)}")
                    
                    # عرض النتيجة
                    if win:
                        embed.title = "🎲 لقد ربحت! 🎉"
                        embed.color = discord.Color.green()
                        embed.description = f"{dice_interaction.user.mention} راهن على **{bet_name}** بمبلغ **{bet_amount}** وربح **{abs(win_amount)}**!"
                    else:
                        embed.title = "🎲 للأسف خسرت!"
                        embed.color = discord.Color.red()
                        embed.description = f"{dice_interaction.user.mention} راهن على **{bet_name}** بمبلغ **{bet_amount}** وخسر!"
                    
                    # إضافة معلومات النرد
                    embed.add_field(name="نتيجة النرد", value=f"{dice_emoji} **{dice_result}**", inline=True)
                    
                    # إضافة الرصيد الجديد
                    try:
                        new_balance = user_balance + win_amount
                        embed.add_field(name="رصيدك الجديد", value=f"**{new_balance}**", inline=True)
                    except:
                        pass
                    
                    # تحديث الرسالة
                    await dice_message.edit(embed=embed)
                    
                except Exception as e:
                    await dice_interaction.followup.send(f"❌ حدث خطأ: {str(e)}", ephemeral=True)
        
        # عرض المودال
        modal = DiceModal()
        modal.view = self
        await interaction.response.send_modal(modal)
    
    @ui.button(label="🏇 سباق الخيول", style=discord.ButtonStyle.primary, emoji="��", row=0)
    async def horserace_game_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة سباق الخيول"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الواجهة ليست لك!", ephemeral=True)
        
        await interaction.response.defer()
        
        # تنفيذ أمر سباق الخيول
        horserace_command = self.bot.get_command('سباق') or self.bot.get_command('horserace')
        if horserace_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(horserace_command)
        else:
            await interaction.followup.send("❌ عذراً، لعبة سباق الخيول غير متاحة حالياً.", ephemeral=True)
    
    @ui.button(label="🃏 بلاك جاك", style=discord.ButtonStyle.primary, emoji="🃏", row=0)
    async def blackjack_game_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر لعبة بلاك جاك"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الواجهة ليست لك!", ephemeral=True)
        
        # إنشاء مودال للعبة بلاك جاك لاختيار المبلغ
        class BlackjackModal(ui.Modal, title="لعبة بلاك جاك 🃏"):
            bet_amount = ui.TextInput(
                label="المبلغ",
                placeholder="مثال: 100 أو كل",
                required=True
            )
            
            async def on_submit(self, bj_interaction: discord.Interaction):
                # تنفيذ أمر بلاك جاك مع المبلغ المدخل
                blackjack_command = self.view.bot.get_command('بلاك_جاك') or self.view.bot.get_command('blackjack')
                if blackjack_command:
                    ctx = await self.view.bot.get_context(self.view.ctx.message)
                    await bj_interaction.response.defer()
                    await ctx.invoke(blackjack_command, amount=self.bet_amount.value)
                else:
                    await bj_interaction.response.send_message("❌ عذراً، لعبة بلاك جاك غير متاحة حالياً.", ephemeral=True)
        
        # عرض المودال
        modal = BlackjackModal()
        modal.view = self
        await interaction.response.send_modal(modal)
    
    @ui.button(label="💰 رصيدي", style=discord.ButtonStyle.success, emoji="💰", row=1)
    async def balance_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر عرض الرصيد"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الواجهة ليست لك!", ephemeral=True)
        
        await interaction.response.defer()
        
        # تنفيذ أمر الرصيد
        balance_command = self.bot.get_command('رصيد') or self.bot.get_command('balance')
        if balance_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(balance_command)
        else:
            await interaction.followup.send("❌ عذراً، أمر الرصيد غير متاح حالياً.", ephemeral=True)
    
    @ui.button(label="📅 المكافأة اليومية", style=discord.ButtonStyle.success, emoji="📅", row=1)
    async def daily_reward_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر المكافأة اليومية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الواجهة ليست لك!", ephemeral=True)
        
        await interaction.response.defer()
        
        # تنفيذ أمر المكافأة اليومية
        daily_command = self.bot.get_command('يومي') or self.bot.get_command('daily')
        if daily_command:
            ctx = await self.bot.get_context(self.ctx.message)
            await ctx.invoke(daily_command)
        else:
            await interaction.followup.send("❌ عذراً، أمر المكافأة اليومية غير متاح حالياً.", ephemeral=True)
    
    @ui.button(label="🔄 تحويل", style=discord.ButtonStyle.success, emoji="🔄", row=1)
    async def transfer_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر تحويل الرصيد"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الواجهة ليست لك!", ephemeral=True)
        
        # إنشاء مودال لتحويل الرصيد
        class TransferModal(ui.Modal, title="تحويل الرصيد 🔄"):
            user_id = ui.TextInput(
                label="معرف أو منشن المستخدم",
                placeholder="مثال: @User أو 12345678901234567",
                required=True
            )
            
            amount = ui.TextInput(
                label="المبلغ",
                placeholder="مثال: 100",
                required=True
            )
            
            async def on_submit(self, transfer_interaction: discord.Interaction):
                # تنفيذ أمر التحويل مع المعلمات المدخلة
                transfer_command = self.view.bot.get_command('تحويل') or self.view.bot.get_command('transfer')
                if transfer_command:
                    ctx = await self.view.bot.get_context(self.view.ctx.message)
                    await transfer_interaction.response.defer()
                    await ctx.invoke(transfer_command, user=self.user_id.value, amount=self.amount.value)
                else:
                    await transfer_interaction.response.send_message("❌ عذراً، أمر التحويل غير متاح حالياً.", ephemeral=True)
        
        # عرض المودال
        modal = TransferModal()
        modal.view = self
        await interaction.response.send_modal(modal)
    
    @ui.button(label="🔙 القائمة الرئيسية", style=discord.ButtonStyle.danger, emoji="🔙", row=1)
    async def main_menu_button(self, interaction: discord.Interaction, button: ui.Button):
        """زر العودة إلى القائمة الرئيسية"""
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("هذه الواجهة ليست لك!", ephemeral=True)
        
        # فتح القائمة الرئيسية من جديد (استخدام ComprehensiveMenuView)
        try:
            from commands.general.menu import ComprehensiveMenuView
            
            # إنشاء رسالة مضمنة للقائمة الشاملة
            embed = discord.Embed(
                title="🤖 أوامر البوت التفاعلية",
                description="اختر مباشرة أحد الأزرار أدناه للوصول إلى الأوامر:",
                color=discord.Color.blue()
            )
            
            # إضافة صورة البوت
            if self.bot.user.avatar:
                embed.set_thumbnail(url=self.bot.user.avatar.url)
            
            # إنشاء كائن القائمة الشاملة المحسنة
            view = ComprehensiveMenuView(self.bot, self.ctx)
            
            # تحديث الرسالة بالقائمة الجديدة
            await interaction.response.edit_message(embed=embed, view=view)
            
            # حفظ الرسالة في كائن القائمة
            view.message = self.message
        except Exception as e:
            # في حالة حدوث خطأ، نعرض رسالة خطأ
            await interaction.response.send_message(f"❌ حدث خطأ أثناء فتح القائمة الرئيسية: {str(e)}", ephemeral=True)

class EnhancedGames(commands.Cog):
    """نظام الألعاب المحسن"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name="العاب",
        aliases=["games", "g", "ألعاب", "العب", "h"],
        description="عرض واجهة تفاعلية محسنة للألعاب"
    )
    async def games(self, ctx):
        """
        عرض واجهة تفاعلية محسنة للألعاب
        
        استخدم هذا الأمر للوصول إلى جميع ألعاب البوت من مكان واحد.
        """
        # إنشاء رسالة مضمنة لواجهة الألعاب المحسنة
        embed = discord.Embed(
            title="🎮 الألعاب المطورة",
            description="اختر أي لعبة من الأزرار أدناه للبدء فوراً:",
            color=discord.Color.purple()
        )
        
        # إضافة معلومات حول الألعاب المتاحة
        embed.add_field(
            name="🎲 ألعاب الحظ",
            value="النرد 🎲 | بلاك جاك 🃏 | سباق الخيول 🏇",
            inline=False
        )
        
        embed.add_field(
            name="📊 الاقتصاد",
            value="رصيدك 💰 | المكافأة اليومية 📅 | تحويل 🔄",
            inline=False
        )
        
        # إضافة تذييل
        embed.set_footer(text="جميع الألعاب متاحة الآن بواجهة تفاعلية مطورة!")
        
        # إضافة صورة البوت
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        elif self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        # إنشاء واجهة الألعاب المحسنة
        view = EnhancedGamesView(self.bot, ctx)
        
        # إرسال الرسالة مع الواجهة
        message = await ctx.send(embed=embed, view=view)
        
        # حفظ الرسالة في كائن الواجهة
        view.message = message

async def setup(bot):
    """إعداد وإضافة نظام الألعاب المحسن إلى البوت"""
    await bot.add_cog(EnhancedGames(bot)) 