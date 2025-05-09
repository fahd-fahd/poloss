#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import random
import asyncio
import datetime

class Card:
    """فئة تمثل بطاقة لعب"""
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
    
    def __str__(self):
        suits = {
            'hearts': '♥️',
            'diamonds': '♦️',
            'clubs': '♣️',
            'spades': '♠️'
        }
        values = {
            1: 'A',
            11: 'J',
            12: 'Q',
            13: 'K'
        }
        
        card_value = values.get(self.value, str(self.value))
        return f"{card_value}{suits[self.suit]}"
    
    def get_value(self):
        """الحصول على قيمة البطاقة في لعبة البلاك جاك"""
        if self.value == 1:  # Ace
            return 11
        elif self.value > 10:  # Face cards
            return 10
        else:
            return self.value

class Deck:
    """فئة تمثل مجموعة من البطاقات"""
    def __init__(self):
        self.cards = []
        self.build()
    
    def build(self):
        """إنشاء مجموعة كاملة من البطاقات"""
        for suit in ['hearts', 'diamonds', 'clubs', 'spades']:
            for value in range(1, 14):
                self.cards.append(Card(suit, value))
    
    def shuffle(self):
        """خلط البطاقات"""
        random.shuffle(self.cards)
    
    def deal(self):
        """سحب بطاقة من المجموعة"""
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            # إذا نفدت البطاقات، أعد بناء المجموعة
            self.build()
            self.shuffle()
            return self.cards.pop()

class Hand:
    """فئة تمثل يد اللاعب"""
    def __init__(self):
        self.cards = []
        self.value = 0
    
    def add_card(self, card):
        """إضافة بطاقة إلى اليد"""
        self.cards.append(card)
    
    def calculate_value(self):
        """حساب قيمة اليد"""
        self.value = 0
        has_ace = False
        
        for card in self.cards:
            card_value = card.get_value()
            self.value += card_value
            
            # تتبع وجود الـ Ace
            if card.value == 1:
                has_ace = True
        
        # إذا تجاوزت القيمة 21 وكان هناك Ace، اعتبر الـ Ace بقيمة 1 بدلاً من 11
        if self.value > 21 and has_ace:
            self.value -= 10
        
        return self.value
    
    def get_cards_display(self, hide_first=False):
        """الحصول على عرض نصي للبطاقات"""
        if not self.cards:
            return "لا توجد بطاقات"
        
        if hide_first:
            return "?? " + " ".join(str(card) for card in self.cards[1:])
        else:
            return " ".join(str(card) for card in self.cards)

class Blackjack(commands.Cog):
    """لعبة البلاك جاك (21)"""
    
    def __init__(self, bot):
        self.bot = bot
        self.currency_emoji = self.bot.config.get('bank', {}).get('currencyEmoji', '💰')
        self.min_bet = self.bot.config.get('games', {}).get('minBet', 10)
        self.max_bet = self.bot.config.get('games', {}).get('maxBet', 10000)
        self.games = {}  # تخزين الألعاب النشطة
        self.deck = Deck()
        self.deck.shuffle()
    
    @commands.command(
        name="بلاك_جاك",
        aliases=["blackjack", "bj", "21", "بلاكجاك"],
        description="لعبة البلاك جاك (21)"
    )
    async def blackjack(self, ctx, amount: str = None):
        """
        لعبة البلاك جاك (21)
        
        المعلمات:
            amount (str): المبلغ الذي تريد المراهنة عليه
        
        أمثلة:
            !بلاك_جاك 100
            !blackjack 500
            !bj all
            !21 كل
        """
        # التحقق من عدم وجود لعبة جارية لهذا المستخدم
        if ctx.author.id in self.games:
            embed = discord.Embed(
                title="❌ لعبة جارية",
                description=f"أنت بالفعل تلعب لعبة بلاك جاك. يرجى إنهاء اللعبة الحالية أولاً.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من المبلغ
        if not amount:
            embed = discord.Embed(
                title="❌ خطأ في الأمر",
                description=f"يجب عليك تحديد المبلغ للمراهنة.\n"
                            f"مثال: `!بلاك_جاك 100` أو `!بلاك_جاك كل`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # تحويل المبلغ
        try:
            if amount.lower() in ['all', 'كل', 'الكل']:
                # الحصول على رصيد المستخدم
                user_data = await self._get_user_data(ctx.author.id)
                bet_amount = user_data['balance']
            else:
                # تحويل المبلغ إلى رقم
                bet_amount = int(amount.replace(',', '').strip())
        except ValueError:
            embed = discord.Embed(
                title="❌ خطأ في المبلغ",
                description=f"يرجى إدخال مبلغ صالح للمراهنة.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من صحة المبلغ
        if bet_amount < self.min_bet:
            embed = discord.Embed(
                title="❌ خطأ في المبلغ",
                description=f"الحد الأدنى للمراهنة هو {self.min_bet} {self.currency_emoji}.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        if bet_amount > self.max_bet:
            embed = discord.Embed(
                title="❌ خطأ في المبلغ",
                description=f"الحد الأقصى للمراهنة هو {self.max_bet} {self.currency_emoji}.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # التحقق من رصيد المستخدم
        user_data = await self._get_user_data(ctx.author.id)
        if user_data['balance'] < bet_amount:
            embed = discord.Embed(
                title="❌ رصيد غير كافٍ",
                description=f"ليس لديك رصيد كافٍ للمراهنة بهذا المبلغ.\n"
                            f"رصيدك الحالي: **{user_data['balance']:,}** {self.currency_emoji}",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # بدء اللعبة
        player_hand = Hand()
        dealer_hand = Hand()
        
        # توزيع البطاقات الأولية
        player_hand.add_card(self.deck.deal())
        dealer_hand.add_card(self.deck.deal())
        player_hand.add_card(self.deck.deal())
        dealer_hand.add_card(self.deck.deal())
        
        # حساب القيم
        player_value = player_hand.calculate_value()
        dealer_value = dealer_hand.calculate_value()
        
        # إعداد اللعبة
        self.games[ctx.author.id] = {
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'bet_amount': bet_amount,
            'user_data': user_data,
            'message': None
        }
        
        # عرض البطاقات الأولية
        embed = await self._create_game_embed(ctx.author, player_hand, dealer_hand, bet_amount, hide_dealer=True)
        message = await ctx.send(embed=embed)
        self.games[ctx.author.id]['message'] = message
        
        # التحقق من البلاك جاك الأولي
        if player_value == 21:
            if dealer_value == 21:
                # تعادل - كلاهما لديه بلاك جاك
                await self._end_game(ctx, "push")
            else:
                # اللاعب لديه بلاك جاك
                await self._end_game(ctx, "blackjack")
        else:
            # إضافة ردود الفعل للتحكم
            await message.add_reaction("👊")  # hit
            await message.add_reaction("🛑")  # stand
            await message.add_reaction("🏳️")  # surrender
            
            # بدء استقبال التفاعلات
            self.bot.loop.create_task(self._reaction_handler(ctx, message))
    
    async def _reaction_handler(self, ctx, message):
        """
        معالج التفاعلات للعبة
        
        المعلمات:
            ctx (Context): سياق الأمر
            message (Message): رسالة اللعبة
        """
        def check(reaction, user):
            return user.id == ctx.author.id and reaction.message.id == message.id and str(reaction.emoji) in ["👊", "🛑", "🏳️"]
        
        while ctx.author.id in self.games:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                
                # إزالة تفاعل المستخدم
                await reaction.remove(user)
                
                if str(reaction.emoji) == "👊":  # hit
                    await self._hit(ctx)
                elif str(reaction.emoji) == "🛑":  # stand
                    await self._stand(ctx)
                elif str(reaction.emoji) == "🏳️":  # surrender
                    await self._surrender(ctx)
                
            except asyncio.TimeoutError:
                # انتهت المهلة - قم بالوقوف تلقائيًا
                if ctx.author.id in self.games:
                    await self._stand(ctx)
                break
    
    async def _hit(self, ctx):
        """
        سحب بطاقة إضافية
        
        المعلمات:
            ctx (Context): سياق الأمر
        """
        if ctx.author.id not in self.games:
            return
        
        game = self.games[ctx.author.id]
        player_hand = game['player_hand']
        dealer_hand = game['dealer_hand']
        bet_amount = game['bet_amount']
        
        # إضافة بطاقة جديدة
        player_hand.add_card(self.deck.deal())
        player_value = player_hand.calculate_value()
        
        # تحديث الرسالة
        embed = await self._create_game_embed(ctx.author, player_hand, dealer_hand, bet_amount, hide_dealer=True)
        await game['message'].edit(embed=embed)
        
        # التحقق من تجاوز الـ 21
        if player_value > 21:
            await self._end_game(ctx, "bust")
    
    async def _stand(self, ctx):
        """
        الوقوف (إنهاء دور اللاعب)
        
        المعلمات:
            ctx (Context): سياق الأمر
        """
        if ctx.author.id not in self.games:
            return
        
        game = self.games[ctx.author.id]
        player_hand = game['player_hand']
        dealer_hand = game['dealer_hand']
        bet_amount = game['bet_amount']
        
        # كشف بطاقات الديلر
        embed = await self._create_game_embed(ctx.author, player_hand, dealer_hand, bet_amount, hide_dealer=False)
        await game['message'].edit(embed=embed)
        
        # الديلر يسحب بطاقات حتى يصل إلى 17 على الأقل
        dealer_value = dealer_hand.calculate_value()
        
        while dealer_value < 17:
            # تأخير لإظهار حركة الديلر
            await asyncio.sleep(1)
            
            dealer_hand.add_card(self.deck.deal())
            dealer_value = dealer_hand.calculate_value()
            
            # تحديث الرسالة
            embed = await self._create_game_embed(ctx.author, player_hand, dealer_hand, bet_amount, hide_dealer=False)
            await game['message'].edit(embed=embed)
        
        # تحديد الفائز
        player_value = player_hand.calculate_value()
        
        if dealer_value > 21:
            # الديلر تجاوز الـ 21
            await self._end_game(ctx, "dealer_bust")
        elif player_value > dealer_value:
            # اللاعب لديه قيمة أعلى
            await self._end_game(ctx, "win")
        elif dealer_value > player_value:
            # الديلر لديه قيمة أعلى
            await self._end_game(ctx, "lose")
        else:
            # تعادل
            await self._end_game(ctx, "push")
    
    async def _surrender(self, ctx):
        """
        الاستسلام (استرداد نصف الرهان)
        
        المعلمات:
            ctx (Context): سياق الأمر
        """
        if ctx.author.id not in self.games:
            return
        
        await self._end_game(ctx, "surrender")
    
    async def _end_game(self, ctx, result):
        """
        إنهاء اللعبة وحساب النتيجة
        
        المعلمات:
            ctx (Context): سياق الأمر
            result (str): نتيجة اللعبة
        """
        if ctx.author.id not in self.games:
            return
        
        game = self.games[ctx.author.id]
        player_hand = game['player_hand']
        dealer_hand = game['dealer_hand']
        bet_amount = game['bet_amount']
        user_data = game['user_data']
        
        # حساب المكسب/الخسارة
        new_balance = user_data['balance']
        result_text = ""
        
        if result == "blackjack":
            # اللاعب لديه بلاك جاك (الربح 1.5 ضعف الرهان)
            winnings = int(bet_amount * 1.5)
            new_balance += winnings
            result_text = f"🎉 **بلاك جاك!** لقد ربحت **{winnings:,}** {self.currency_emoji}"
            color = discord.Color.gold()
        elif result == "win":
            # اللاعب فاز
            winnings = bet_amount
            new_balance += winnings
            result_text = f"🎉 **فزت!** لقد ربحت **{winnings:,}** {self.currency_emoji}"
            color = discord.Color.green()
        elif result == "dealer_bust":
            # الديلر تجاوز الـ 21
            winnings = bet_amount
            new_balance += winnings
            result_text = f"🎉 **فزت!** الديلر تجاوز الـ 21. لقد ربحت **{winnings:,}** {self.currency_emoji}"
            color = discord.Color.green()
        elif result == "push":
            # تعادل
            result_text = f"🤝 **تعادل!** تم إرجاع رهانك **{bet_amount:,}** {self.currency_emoji}"
            color = discord.Color.blue()
        elif result == "surrender":
            # الاستسلام
            loss = bet_amount // 2  # خسارة نصف الرهان
            new_balance -= loss
            result_text = f"🏳️ **استسلمت.** خسرت **{loss:,}** {self.currency_emoji}"
            color = discord.Color.orange()
        elif result == "bust":
            # اللاعب تجاوز الـ 21
            new_balance -= bet_amount
            result_text = f"💥 **تجاوزت الـ 21!** خسرت **{bet_amount:,}** {self.currency_emoji}"
            color = discord.Color.red()
        else:  # "lose"
            # اللاعب خسر
            new_balance -= bet_amount
            result_text = f"😔 **خسرت.** خسرت **{bet_amount:,}** {self.currency_emoji}"
            color = discord.Color.red()
        
        # تحديث قاعدة البيانات
        if hasattr(self.bot, 'db'):
            await self.bot.db.users.update_one(
                {"user_id": ctx.author.id},
                {"$set": {"balance": new_balance}}
            )
        
        # عرض النتيجة النهائية
        player_value = player_hand.calculate_value()
        dealer_value = dealer_hand.calculate_value()
        
        embed = discord.Embed(
            title="🃏 نتيجة البلاك جاك",
            description=f"**يدك:** {player_hand.get_cards_display()} ({player_value})\n"
                        f"**يد الديلر:** {dealer_hand.get_cards_display()} ({dealer_value})\n\n"
                        f"{result_text}",
            color=color
        )
        
        embed.add_field(
            name="💳 رصيدك الحالي",
            value=f"**{new_balance:,}** {self.currency_emoji}",
            inline=True
        )
        
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        # تحديث الرسالة
        await game['message'].edit(embed=embed)
        
        # إزالة ردود الفعل
        try:
            await game['message'].clear_reactions()
        except:
            pass
        
        # إزالة اللعبة من القائمة النشطة
        del self.games[ctx.author.id]
    
    async def _create_game_embed(self, user, player_hand, dealer_hand, bet_amount, hide_dealer=True):
        """
        إنشاء رسالة مضمنة للعبة
        
        المعلمات:
            user (User): المستخدم
            player_hand (Hand): يد اللاعب
            dealer_hand (Hand): يد الديلر
            bet_amount (int): مبلغ الرهان
            hide_dealer (bool): إخفاء البطاقة الأولى للديلر
        
        Returns:
            Embed: الرسالة المضمنة
        """
        player_value = player_hand.calculate_value()
        
        if hide_dealer:
            # إخفاء البطاقة الأولى والقيمة
            dealer_display = dealer_hand.get_cards_display(hide_first=True)
            dealer_value_text = "?"
        else:
            # عرض جميع البطاقات والقيمة
            dealer_display = dealer_hand.get_cards_display()
            dealer_value = dealer_hand.calculate_value()
            dealer_value_text = str(dealer_value)
        
        embed = discord.Embed(
            title="🃏 لعبة البلاك جاك",
            description=f"الرهان: **{bet_amount:,}** {self.currency_emoji}\n\n"
                        f"**يدك:** {player_hand.get_cards_display()} ({player_value})\n"
                        f"**يد الديلر:** {dealer_display} ({dealer_value_text})",
            color=discord.Color.blue()
        )
        
        # إضافة التعليمات
        if player_value < 21:
            embed.add_field(
                name="📋 التعليمات",
                value="👊 سحب بطاقة\n"
                      "🛑 الوقوف\n"
                      "🏳️ الاستسلام (استرداد نصف الرهان)",
                inline=False
            )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        return embed
    
    async def _get_user_data(self, user_id):
        """
        الحصول على بيانات المستخدم من قاعدة البيانات
        
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
                'balance': self.bot.config.get('bank', {}).get('initialBalance', 1000),
                'bank_profile': {
                    'level': 1,
                    'daily': {
                        'last_claim': None,
                        'streak': 0
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
                'balance': self.bot.config.get('bank', {}).get('initialBalance', 1000),
                'bank_profile': {
                    'level': 1,
                    'daily': {
                        'last_claim': None,
                        'streak': 0
                    }
                },
                'created_at': datetime.datetime.utcnow().isoformat()
            }
            # حفظ البيانات الجديدة في قاعدة البيانات
            await users_collection.insert_one(user_data)
        
        return user_data

async def setup(bot):
    """إعداد الأمر وإضافته إلى البوت"""
    await bot.add_cog(Blackjack(bot)) 