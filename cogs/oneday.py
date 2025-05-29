import asyncio
import json
from typing import Dict, List, Literal, Union

import aiofiles
import discord
from discord import app_commands
from discord.ext import commands

from utils import imageUtils


class OneDayCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.coin: Dict[int, int] = {}
        self.speed: List[Dict[str, Union[int, float]]] = []
        self.lateness: Dict[int, int] = {}
        self.gay: Dict[int, int] = {}

    async def cog_load(self):
        async with aiofiles.open("coin.json") as f:
            data = json.loads(await f.read())
            self.coin = {int(k): v for k, v in data.items()}

        async with aiofiles.open("speed.json") as f:
            self.speed = json.loads(await f.read())

        async with aiofiles.open("lateness.json") as f:
            data = json.loads(await f.read())
            self.lateness = {int(k): v for k, v in data.items()}

        async with aiofiles.open("gay.json") as f:
            data = json.loads(await f.read())
            self.gay = {int(k): v for k, v in data.items()}

    group = app_commands.Group(name="oneday", description="1day-chatのツール類。")

    @group.command(
        name="coinrank", description="今までのコインロール取得回数のランキング。"
    )
    @app_commands.describe(top="何位まで表示するか。デフォルトは5です。")
    async def coinRanking(
        self,
        interaction: discord.Interaction,
        theme: Literal["ダーク", "ライト"] = "ダーク",
        top: app_commands.Range[int, 1] = 5,
    ):
        await interaction.response.defer()

        sortedRecords = sorted(self.coin.items(), key=lambda x: x[1], reverse=True)[
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
            "コインロールランキング",
            "{pt}回",
            users,
            theme,
        )
        file = discord.File(fp=buffer, filename="ranking.png")
        await interaction.followup.send(file=file)

    @group.command(
        name="spdrank", description="今までのコインロール取得速度のランキング。"
    )
    @app_commands.describe(top="何位まで表示するか。デフォルトは5です。")
    async def speedRanking(
        self,
        interaction: discord.Interaction,
        theme: Literal["ダーク", "ライト"] = "ダーク",
        top: app_commands.Range[int, 1] = 5,
    ):
        await interaction.response.defer()

        # 重複OKですべての速度データを速い順にソート
        sortedRecords = sorted(self.speed, key=lambda x: x["speed"])[:top]

        users = []
        for record in sortedRecords:
            user_id = record["user"]
            spd = round(record["speed"], 2)
            try:
                user = await interaction.guild.fetch_member(user_id)
                users.append((user, spd, await user.display_avatar.read()))
            except:
                try:
                    user = await interaction.client.fetch_user(user_id)
                    users.append((user, spd, await user.display_avatar.read()))
                except:
                    users.append((str(user_id), spd, b""))

        buffer = await asyncio.to_thread(
            imageUtils.generateRankingImage,
            "コインロール最速取得ランキング",
            "{pt}秒",
            users,
            theme,
        )
        file = discord.File(fp=buffer, filename="ranking.png")
        await interaction.followup.send(file=file)

    @group.command(
        name="laterank", description="今までのコインロール遅刻ポイントのランキング。"
    )
    @app_commands.describe(top="何位まで表示するか。デフォルトは5です。")
    async def lateRanking(
        self,
        interaction: discord.Interaction,
        theme: Literal["ダーク", "ライト"] = "ダーク",
        top: app_commands.Range[int, 1] = 5,
    ):
        await interaction.response.defer()

        sortedRecords = sorted(self.lateness.items(), key=lambda x: x[1], reverse=True)[
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
            "コインロール遅刻ランキング",
            "{pt}ポイント",
            users,
            theme,
        )
        file = discord.File(fp=buffer, filename="ranking.png")
        await interaction.followup.send(file=file)

    @group.command(
        name="gayrank", description="今までゲイロールが付与されたランキング。"
    )
    @app_commands.describe(top="何位まで表示するか。デフォルトは5です。")
    async def gayRanking(
        self,
        interaction: discord.Interaction,
        theme: Literal["ダーク", "ライト"] = "ダーク",
        top: app_commands.Range[int, 1] = 5,
    ):
        await interaction.response.defer()

        sortedRecords = sorted(self.gay.items(), key=lambda x: x[1], reverse=True)[:top]

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
            "ゲイロール付与ランキング",
            "{pt}回",
            users,
            theme,
        )
        file = discord.File(fp=buffer, filename="ranking.png")
        await interaction.followup.send(file=file)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        beforeRoles = set(before.roles)
        afterRoles = set(after.roles)

        # 追加されたロールを取得
        addedRoles = afterRoles - beforeRoles

        # もしゲイロールが追加されたならば
        gayRole = discord.utils.get(addedRoles, name="gay")
        if gayRole:
            if not after.id in self.gay:
                self.gay[after.id] = 0
            self.gay[after.id] += 1
            async with aiofiles.open("gay.json", "w") as f:
                await f.write(json.dumps(self.gay))

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.TextChannel):
        if channel.name != "1day-chat":
            return

        def check(m: discord.Message):
            return m.author.id == 1362354606923059322 and m.channel == channel

        message = await self.bot.wait_for("message", check=check)

        before = message.created_at.timestamp()

        def check(m: discord.Message):
            return m.channel == channel

        message = await self.bot.wait_for("message", check=check)
        between = message.created_at.timestamp() - before

        if not message.author.id in self.coin:
            self.coin[message.author.id] = 0
        self.coin[message.author.id] += 1

        self.speed.append(
            {
                "user": message.author.id,
                "speed": between,
            }
        )

        asyncio.create_task(
            channel.send(
                f"{message.author.mention} さんが**{self.coin[message.author.id]}**回目のコインロール獲得です！\nタイム: {between}秒"
            )
        )

        def check(m: discord.Message):
            return (
                m.channel == channel and not m.author.bot and m.author != message.author
            )

        try:
            msg1 = await self.bot.wait_for("message", check=check)

            if not msg1.author.id in self.lateness:
                self.lateness[msg1.author.id] = 0
            self.lateness[msg1.author.id] += 2
        except Exception as e:
            print(e)

        def check(m: discord.Message):
            return (
                m.channel == channel
                and not m.author.bot
                and m.author != message.author
                and m.author != msg1.author
            )

        try:
            msg2 = await self.bot.wait_for("message", check=check)

            if not msg2.author.id in self.lateness:
                self.lateness[msg2.author.id] = 0
            self.lateness[msg2.author.id] += 1
        except Exception as e:
            print(e)

        async with aiofiles.open("coin.json", "w") as f:
            await f.write(json.dumps(self.coin))

        async with aiofiles.open("speed.json", "w") as f:
            await f.write(json.dumps(self.speed))

        async with aiofiles.open("lateness.json", "w") as f:
            await f.write(json.dumps(self.lateness))


async def setup(bot: commands.Bot):
    await bot.add_cog(OneDayCog(bot))
