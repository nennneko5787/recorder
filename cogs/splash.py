import asyncio
import random
import time
from typing import Dict, List, Optional

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View


class EntryView(View):
    def __init__(self, game: "PaintGame"):
        super().__init__(timeout=None)
        self.game = game
        self.join_button = Button(label="参加", style=discord.ButtonStyle.primary)
        self.join_button.callback = self.join
        self.add_item(self.join_button)

    async def join(self, interaction: discord.Interaction):
        if self.game.task:
            await interaction.response.send_message(
                "すでにゲームが開始中です。", ephemeral=True
            )
            return
        await self.game.add_player(interaction)


class PaintButton(Button):
    def __init__(self, x: int, y: int, game: "PaintGame"):
        super().__init__(label=" ", style=discord.ButtonStyle.secondary, row=y)
        self.x = x
        self.y = y
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        await self.game.paint(self.x, self.y, interaction)


class PaintView(View):
    def __init__(self, game):
        super().__init__(timeout=None)
        self.game = game
        self.buttons = [[PaintButton(x, y, game) for x in range(5)] for y in range(5)]
        for row in self.buttons:
            for btn in row:
                self.add_item(btn)

    def update_buttons(self):
        for y in range(5):
            for x in range(5):
                color = self.game.board[y][x]
                button = self.buttons[y][x]
                if color == "🔴":
                    button.label = "󠄺"
                    button.style = discord.ButtonStyle.danger
                elif color == "🔵":
                    button.label = "󠄺"
                    button.style = discord.ButtonStyle.primary
                else:
                    button.label = "󠄺"
                    button.style = discord.ButtonStyle.secondary


class PaintGame:
    def __init__(
        self,
        bot: discord.Client,
        channel: discord.abc.Messageable,
        user: discord.User,
        max_players: int = 2,
    ):
        self.bot = bot
        self.channel = channel
        self.max_players = max_players
        self.teams: Dict[str, List[discord.User]] = {"🔴": [user], "🔵": []}
        self.player_colors: Dict[discord.User, str] = {user: "🔴"}
        self.board: List[List[Optional[str]]] = [
            [None for _ in range(5)] for _ in range(5)
        ]
        self.lock = asyncio.Lock()
        self.paint_view = PaintView(self)
        self.task: Optional[asyncio.Task] = None
        self.cooldowns: Dict[int, float] = {}
        self.cooldown_interval = 1.5
        self.time: float = 0
        self.entry_message: Optional[discord.Message] = None

    def player_count(self) -> int:
        return len(self.teams["🔴"]) + len(self.teams["🔵"])

    def get_entry_embed(self) -> discord.Embed:
        embed = discord.Embed(title="ペイントバトル参加受付中！", color=0x00FFCC)
        embed.add_field(
            name="🔴 チーム",
            value="\n".join(u.mention for u in self.teams["🔴"]) or "なし",
            inline=True,
        )
        embed.add_field(
            name="🔵 チーム",
            value="\n".join(u.mention for u in self.teams["🔵"]) or "なし",
            inline=True,
        )
        embed.set_footer(text=f"現在: {self.player_count()}/{self.max_players}人")
        return embed

    def get_game_embed(self, remaining: Optional[int] = None) -> discord.Embed:
        red_count = sum(row.count("🔴") for row in self.board)
        blue_count = sum(row.count("🔵") for row in self.board)
        embed = discord.Embed(title="🎮 ペイントバトル", color=0x5865F2)
        embed.add_field(
            name="🔴 チーム",
            value="\n".join(u.mention for u in self.teams["🔴"]) or "なし",
            inline=True,
        )
        embed.add_field(
            name="🔵 チーム",
            value="\n".join(u.mention for u in self.teams["🔵"]) or "なし",
            inline=True,
        )
        embed.add_field(
            name="統計",
            value=f"🔴 {red_count} マス\n🔵 {blue_count} マス",
            inline=False,
        )
        if remaining is not None:
            embed.set_footer(text=f"残り時間: {remaining}秒")
        return embed

    async def start_entry(self):
        self.entry_view = EntryView(self)
        self.entry_message = await self.channel.send(
            embed=self.get_entry_embed(),
            view=self.entry_view,
        )

    async def add_player(self, interaction: discord.Interaction):
        if any(interaction.user in team for team in self.teams.values()):
            await interaction.response.send_message(
                "すでに参加しています。", ephemeral=True
            )
            return

        if self.player_count() >= self.max_players:
            await interaction.response.send_message("満員です！", ephemeral=True)
            return

        team = "🔴" if len(self.teams["🔴"]) <= len(self.teams["🔵"]) else "🔵"
        self.teams[team].append(interaction.user)
        self.player_colors[interaction.user] = team
        await interaction.response.send_message(
            f"{team}チームで参加しました！", ephemeral=True
        )

        # エントリーEmbed更新
        if self.entry_message:
            await self.entry_message.edit(
                embed=self.get_entry_embed(), view=self.entry_view
            )

        if self.player_count() == self.max_players:
            await self.start_game()

    async def start_game(self):
        self.time = time.time()
        self.paint_view.update_buttons()
        await self.channel.send(embed=self.get_game_embed(), view=self.paint_view)
        self.task = self.bot.loop.create_task(self.game_timer())

    async def paint(self, x: int, y: int, interaction: discord.Interaction):
        if time.time() >= self.time + 60:
            await interaction.response.send_message(
                "すでに終わっているゲームです。", ephemeral=True
            )
            return

        now = time.time()
        last = self.cooldowns.get(interaction.user.id, 0)
        if now - last < self.cooldown_interval:
            await interaction.response.defer(ephemeral=True)
            return
        self.cooldowns[interaction.user.id] = now

        async with self.lock:
            if interaction.user not in self.player_colors:
                await interaction.response.send_message(
                    "プレイヤーではありません。", ephemeral=True
                )
                return

            self.board[y][x] = self.player_colors[interaction.user]
            self.paint_view.update_buttons()
            remaining = int(self.time + 60 - time.time())
            await interaction.response.edit_message(
                embed=self.get_game_embed(remaining), view=self.paint_view
            )

    async def game_timer(self):
        await asyncio.sleep(60)
        await self.end_game()

    async def end_game(self):
        red = sum(row.count("🔴") for row in self.board)
        blue = sum(row.count("🔵") for row in self.board)

        if red > blue:
            result = f"🏆 🔴 チームの勝ち！"
        elif blue > red:
            result = f"🏆 🔵 チームの勝ち！"
        else:
            result = "🤝 引き分け！"

        embed = self.get_game_embed(remaining=0)
        embed.title = "🎉 ゲーム終了！"
        embed.description = result
        await self.channel.send(embed=embed)


class SplashCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="paintgame", description="ペイントバトルを始める")
    async def paint_game_command(
        self,
        interaction: discord.Interaction,
        players: app_commands.Range[int, 2, 8] = 2,
    ):
        await interaction.response.send_message("ゲームを作成中...", ephemeral=True)
        game = PaintGame(
            interaction.client,
            interaction.channel,
            interaction.user,
            max_players=players,
        )
        await game.start_entry()


async def setup(bot: commands.Bot):
    await bot.add_cog(SplashCog(bot))
