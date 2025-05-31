import discord
import selfcord
from discord import app_commands
from discord.ext import commands


class AutoLeaveModal(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(
            title="DMグループからの自動退出", timeout=None, custom_id="test-modal-1"
        )

        self.token = discord.ui.TextInput(
            label="Discordのユーザートークン(いくつかの/で区切ることをおすすめします)",
            placeholder="持ってないなら実行できません、ネットで取り方を探してきてください",
            style=discord.TextStyle.long,
            required=True,
        )

        self.rule = discord.ui.TextInput(
            label="注意点",
            default="""・Discordの利用規約に違反する「セルフボット」を使ってDMグループから退出するため、アカウントがBANされる可能性があります。
アカウントがBANされたとしても本Bot作成者は責任を負えません。自己責任でお願いします。
・本ツールのコードは公開されています。( https://github.com/nennneko5787/recorder/blob/main/cogs/tools.py )""",
            required=False,
        )

        self.add_item(self.token)
        self.add_item(self.rule)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        client = selfcord.Client()

        await interaction.followup.send(
            "DMグループからの退出を開始しました...", ephemeral=True
        )

        await client.login("".join(self.token.value.split("/")))

        count = 0
        for channel in client.private_channels:
            if channel.type == discord.ChannelType.group:
                if channel.owner.is_blocked():
                    await channel.leave()
                    count += 1

        await interaction.followup.send(
            f"{count}個のDMグループから退出しました。", ephemeral=True
        )


class AutoLeaveCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    group = app_commands.Group(
        name="tools", description="使えるかもしれないし使えないかもしれないツール類。"
    )

    @group.command(
        name="autoleaver",
        description="ブロックしているユーザーのDMグループから退出します。",
    )
    async def autoLeaveCommand(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AutoLeaveModal())

    @group.command(
        name="rmention",
        description="ランダムメンションを行います。",
    )
    async def randomMentionCommand(self, interaction: discord.Interaction):
        await interaction.response.send_message("<@1048448686914551879>")


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoLeaveCog(bot))
