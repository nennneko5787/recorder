import asyncio
import io

import discord
import httpx
from discord import app_commands
from discord.ext import commands


class MiqCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.http = httpx.AsyncClient()

        self.makeItAQuoteContext = app_commands.ContextMenu(
            name="めーくいっとあくおーと",
            callback=self.makeItAQuote,
        )
        self.bot.tree.add_command(self.makeItAQuoteContext)

    async def makeItAQuote(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        await interaction.response.defer()

        response = await self.http.post(
            "https://api.voids.top/quote",
            json={
                "username": message.author.name,
                "display_name": message.author.display_name,
                "text": message.clean_content,
                "avatar": message.author.display_avatar.url,
                "color": True,
            },
        )
        jsonData = response.json()

        response = await self.http.get(jsonData["url"])
        img_bytes = io.BytesIO(response.content)

        # Pillow処理を非同期にオフロード
        output_buffer = await asyncio.to_thread(self.process_image, img_bytes)

        await interaction.followup.send(file=discord.File(output_buffer, "miq.png"))

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
    await bot.add_cog(MiqCog(bot))
