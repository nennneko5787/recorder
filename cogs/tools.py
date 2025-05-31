import asyncio
import io
import os
import random

import discord
import dotenv
import httpx
import selfcord
from discord import app_commands
from discord.ext import commands

dotenv.load_dotenv()


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
            placeholder="何故消した？",
            default="""・Discordの利用規約に違反する「セルフボット」を使ってDMグループから退出するため、アカウントがBANされる可能性があります。
アカウントがBANされたとしても本Bot作成者は責任を負えません。自己責任でお願いします。
・本ツールのコードは公開されています。( https://github.com/nennneko5787/recorder/blob/main/cogs/tools.py )""",
            style=discord.TextStyle.long,
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
        self.selfbot = selfcord.Client()
        self.http = httpx.AsyncClient()

    async def cog_load(self):
        await self.selfbot.login(os.getenv("selftoken"))

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

    @group.command(
        name="namelookup", description="pomelo usernameが空いているか検索します。"
    )
    async def nameLookupCommand(self, interaction: discord.Interaction, pomelo: str):
        await interaction.response.defer()
        if await self.selfbot.check_pomelo_username(pomelo):
            await interaction.followup.send(
                f"指定されたユーザー名「{pomelo}」はすでに使用されています。"
            )
        else:
            await interaction.followup.send(
                f"指定されたユーザー名「{pomelo}」はまだ使用されていません。"
            )

    @group.command(
        name="namesuggestion", description="あなたに新しいpomelo usernameを提案します。"
    )
    async def nameSuggestionCommand(
        self, interaction: discord.Interaction, name: str = None
    ):
        await interaction.response.defer()
        if not name:
            name = interaction.user.display_name
        await interaction.followup.send(
            f"あなたにおすすめのユーザーネームは `{await self.selfbot.pomelo_suggestion(name)}` です。"
        )

    @group.command(
        name="quote", description="このチャンネルでのユーザーの名言を取得します。"
    )
    async def quoteCommand(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        limit: app_commands.Range[int, 10, 1000] = 50,
    ):
        await interaction.response.defer()

        channel = await self.selfbot.fetch_channel(interaction.channel_id)
        messages = [
            message async for message in channel.search(limit=limit, authors=[user])
        ]
        message = random.choice(messages)

        response = await self.http.post(
            "https://api.voids.top/quote",
            json={
                "username": user.name,
                "display_name": user.display_name,
                "text": message.clean_content,
                "avatar": user.display_avatar.url,
                "color": True,
            },
        )
        jsonData = response.json()

        response = await self.http.get(jsonData["url"])
        img_bytes = io.BytesIO(response.content)

        # Pillow処理を非同期にオフロード
        output_buffer = await asyncio.to_thread(self.process_image, img_bytes)

        await interaction.followup.send(
            message.jump_url, file=discord.File(output_buffer, "miq.png")
        )

    def process_image(self, img_bytes: io.BytesIO) -> io.BytesIO:
        from PIL import Image, ImageDraw, ImageFont

        img = Image.open(img_bytes).convert("RGBA")
        draw = ImageDraw.Draw(img)

        font_path = "./fonts/NotoSansJP-Medium.ttf"
        font_size = int(img.height * 0.03)
        font = ImageFont.truetype(font_path, font_size)

        text = "discord.gg/aa-bot に今すぐ参加！"
        x, y, x2, y2 = draw.textbbox((0, 0), text, font=font)
        text_width = x2 - x
        text_height = y2 - y

        margin = 10
        x = img.width - text_width - margin
        y = img.height - text_height - margin
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

        output_buffer = io.BytesIO()
        img.save(output_buffer, format="PNG")
        output_buffer.seek(0)
        return output_buffer


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoLeaveCog(bot))
