import asyncio
import io
import json
from typing import Dict, Literal

import aiofiles
import discord
from discord import app_commands
from discord.ext import commands

from utils import imageUtils


class StatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.messages: Dict[int, int] = {}

    async def cog_load(self):
        async with aiofiles.open("messages.json") as f:
            data = json.loads(await f.read())
            self.messages = {int(k): v for k, v in data.items()}

    async def cog_unload(self):
        async with aiofiles.open("messages.json", "w") as f:
            await f.write(json.dumps(self.messages))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author.id in self.messages:
            self.messages[message.author.id] = 0
        self.messages[message.author.id] += 1

    group = app_commands.Group(
        name="stat", description="ああbotの統計をなんかするコマンドです。"
    )

    @group.command(name="msgrank", description="今までのメッセージ送信数のランキング。")
    @app_commands.describe(top="何位まで表示するか。デフォルトは5です。")
    async def messageRanking(
        self,
        interaction: discord.Interaction,
        theme: Literal["ダーク", "ライト"] = "ダーク",
        top: app_commands.Range[int, 1] = 5,
    ):
        await interaction.response.defer()

        sortedRecords = sorted(self.messages.items(), key=lambda x: x[1], reverse=True)[
            :top
        ]

        # ユーザー名を取得
        users = []
        for user_id, count in sortedRecords:
            try:
                user = await interaction.guild.fetch_member(user_id)
                users.append((user, count, await user.display_avatar.read()))
            except:
                try:
                    user = await interaction.client.fetch_user(user_id)
                    users.append((user, count, await user.display_avatar.read()))
                except:
                    users.append((str(user_id), count, b""))

        buffer = await asyncio.to_thread(
            imageUtils.generateRankingImage,
            "メッセージ数ランキング",
            "{pt}メッセージ",
            users,
            theme,
        )
        file = discord.File(fp=buffer, filename="ranking.png")
        await interaction.followup.send(file=file)

    @group.command(name="gairais", description="外来生物のリストを取得します。")
    async def gairaisCommand(self, interaction: discord.Interaction):
        await interaction.response.defer()
        gairaiList = discord.utils.get(
            interaction.guild.roles, name="特定外来生物"
        ).members
        file = discord.File(
            io.BytesIO(
                f"[{', '.join([str(member.id) for member in gairaiList])}]".encode()
            ),
            filename="gairais.json",
        )
        await interaction.followup.send(file=file)

    @group.command(name="hijacks", description="クソ乗っ取られのリストを取得します。")
    async def hijackCommand(self, interaction: discord.Interaction):
        await interaction.response.defer()
        gairaiList = discord.utils.get(
            interaction.guild.roles, name="クソ乗っ取られ"
        ).members
        file = discord.File(
            io.BytesIO(
                f"[{', '.join([str(member.id) for member in gairaiList])}]".encode()
            ),
            filename="hijacks.json",
        )
        await interaction.followup.send(file=file)

    @group.command(name="endangered", description="絶滅危惧種のリストを取得します。")
    async def endangeredCommand(self, interaction: discord.Interaction):
        await interaction.response.defer()
        gairaiList = discord.utils.get(
            interaction.guild.roles, name="絶滅危惧種"
        ).members
        file = discord.File(
            io.BytesIO(
                f"[{', '.join([str(member.id) for member in gairaiList])}]".encode()
            ),
            filename="endangered.json",
        )
        await interaction.followup.send(file=file)

    @group.command(name="supporter", description="サポーターのリストを取得します。")
    async def supporterCommand(self, interaction: discord.Interaction):
        await interaction.response.defer()
        gairaiList = discord.utils.get(
            interaction.guild.roles, name="サポーター"
        ).members
        file = discord.File(
            io.BytesIO(
                f"[{', '.join([str(member.id) for member in gairaiList])}]".encode()
            ),
            filename="supporter.json",
        )
        await interaction.followup.send(file=file)

    @group.command(name="booster", description="ブースターのリストを取得します。")
    async def supporterCommand(self, interaction: discord.Interaction):
        await interaction.response.defer()
        gairaiList = discord.utils.get(interaction.guild.roles, name="Booster!").members
        file = discord.File(
            io.BytesIO(
                f"[{', '.join([str(member.id) for member in gairaiList])}]".encode()
            ),
            filename="booster.json",
        )
        await interaction.followup.send(file=file)


async def setup(bot: commands.Bot):
    await bot.add_cog(StatCog(bot))
