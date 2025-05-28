import io

import discord
from discord import app_commands
from discord.ext import commands


class StatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    group = app_commands.Group(
        name="stat", description="ああbotの統計をなんかするコマンドです。"
    )

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
