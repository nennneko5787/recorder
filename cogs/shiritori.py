import asyncio
import re
import unicodedata

import discord
from discord import app_commands
from discord.ext import commands

games = {}


def katakana_to_hiragana(text: str) -> str:
    return "".join(chr(ord(ch) - 0x60) if "ァ" <= ch <= "ン" else ch for ch in text)


def is_valid_word(word: str) -> bool:
    # ひらがな or 許可された記号のみ
    return re.fullmatch(r"[ぁ-んー・、。！？゛゜]+", word) is not None


def normalize_hiragana(word: str) -> str:
    word = katakana_to_hiragana(word)
    word = unicodedata.normalize("NFKC", word)
    return word


def extract_first_last(word: str) -> tuple[str, str]:
    # 語頭・語尾として使える文字を抽出
    chars = [c for c in word if "ぁ" <= c <= "ん"]
    if len(chars) < 1:
        return "", ""
    return chars[0], chars[-1]


class ShiritoriGame:
    def __init__(self, channel):
        self.channel = channel
        self.words = ["しりとり"]
        self.last_word = "しりとり"
        self.active = True
        self.lock = asyncio.Lock()
        self.message = None
        self.last_user_id = None

    def validate_word(self, user, word):
        word = normalize_hiragana(word)

        if not is_valid_word(word):
            return (
                False,
                "❌ 単語はひらがな・カタカナと記号（ー・、。！？）のみ使用できます。",
            )

        if user.id == self.last_user_id:
            return False, "❌ 同じ人が連続で単語を送ることはできません。"

        if word in self.words:
            return False, f"❌ 『{word}』はすでに使われました！"

        _, prev_last = extract_first_last(self.last_word)
        current_first, _ = extract_first_last(word)

        if current_first != prev_last:
            return (
                False,
                f"❌ 『{word}』は『{self.last_word}』の最後の文字『{prev_last}』から始まっていません！",
            )

        self.words.append(word)
        self.last_word = word
        self.last_user_id = user.id

        flow = " → ".join(self.words)
        content = f"📜 単語の流れ：{flow}\n✅ {user.mention} が送信しました！"
        return True, content


class WordModal(discord.ui.Modal):
    def __init__(self, game: ShiritoriGame, user: discord.User, view: discord.ui.View):
        super().__init__(title="しりとり単語入力")
        self.game = game
        self.user = user
        self.view = view

        self.word_input = discord.ui.TextInput(
            label="単語",
            placeholder="ひらがな or カタカナ（ー、！、？など一部記号OK）",
            required=True,
            max_length=20,
        )
        self.add_item(self.word_input)

    async def on_submit(self, interaction: discord.Interaction):
        async with self.game.lock:
            if not self.game.active:
                await interaction.response.send_message(
                    "ゲームは終了しています。", ephemeral=True
                )
                return

            word = self.word_input.value.strip()
            success, content = self.game.validate_word(self.user, word)

            if success:
                await self.game.message.edit(content=content, view=self.view)
                await interaction.response.defer()
            else:
                await interaction.response.send_message(content, ephemeral=True)


class ShiritoriView(discord.ui.View):
    def __init__(self, game: ShiritoriGame):
        super().__init__(timeout=None)
        self.game = game

    @discord.ui.button(label="単語を送る", style=discord.ButtonStyle.primary)
    async def send_word(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not self.game.active:
            await interaction.response.send_message(
                "ゲームは終了しています。", ephemeral=True
            )
            return

        await interaction.response.send_modal(
            WordModal(self.game, interaction.user, self)
        )


class ShiritoriCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="shiritori", description="しりとりを開始する")
    async def shiritori_start(self, interaction: discord.Interaction):
        if interaction.guild.id in games:
            await interaction.response.send_message(
                "すでにゲームが進行中です。", ephemeral=True
            )
            return

        game = ShiritoriGame(channel=interaction.channel)
        games[interaction.guild.id] = game

        view = ShiritoriView(game)
        await interaction.response.send_message(
            "🎮 しりとりを始めましょう！最初の単語は『しりとり』です！ボタンを押して単語を送ってください！",
            view=view,
        )
        game.message = await interaction.original_response()


async def setup(bot: commands.Bot):
    await bot.add_cog(ShiritoriCog(bot))
