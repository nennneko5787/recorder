import asyncio
import io

import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji

from utils.wrap import fw_wrap


class MiqCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.makeItAQuoteContext = app_commands.ContextMenu(
            name="めーくいっとあくおーと",
            callback=self.makeItAQuote,
        )
        self.bot.tree.add_command(self.makeItAQuoteContext)

    def drawText(
        self,
        im,
        ofs,
        string,
        font="./fonts/NotoSansJP-Medium.ttf",
        size=16,
        color=(0, 0, 0, 255),
        split_len=None,
        padding=4,
        disable_dot_wrap=False,
    ):
        ImageDraw.Draw(im)
        fontObj = ImageFont.truetype(font, size=size)

        pure_lines = []
        pos = 0
        l = ""

        if not disable_dot_wrap:
            for char in string:
                if char == "\n":
                    pure_lines.append(l)
                    l = ""
                    pos += 1
                elif char == "、" or char == ",":
                    pure_lines.append(l + ("、" if char == "、" else ","))
                    l = ""
                    pos += 1
                elif char == "。" or char == ".":
                    pure_lines.append(l + ("。" if char == "。" else "."))
                    l = ""
                    pos += 1
                else:
                    l += char
                    pos += 1

            if l:
                pure_lines.append(l)
        else:
            pure_lines = string.split("\n")

        lines = []

        for line in pure_lines:
            lines.extend(fw_wrap(line, width=split_len))

        dy = 0

        draw_lines = []

        for line in lines:
            tsize = fontObj.getbbox(line)

            ofs_y = ofs[1] + dy
            t_height = tsize[1]

            x = int(ofs[0] - (tsize[0] / 2))
            draw_lines.append((x, ofs_y, line))
            ofs_y += t_height + padding
            dy += t_height + padding

        adj_y = -30 * (len(draw_lines) - 1)
        for dl in draw_lines:
            with Pilmoji(im) as p:
                p.text((dl[0], (adj_y + dl[1])), dl[2], font=fontObj, fill=color)

        real_y = ofs[1] + adj_y + dy

        return (0, dy, real_y)

    def createMakeItAQuote(
        self, member: discord.Member, message: discord.Message, iconFile: bytes
    ) -> io.BytesIO:
        img = Image.new("RGBA", (1280, 720), "#00000000")
        icon = Image.open(io.BytesIO(iconFile))
        icon = icon.resize((720, 720), Image.Resampling.LANCZOS)

        base = Image.open("base-gd.png").convert("RGBA")

        img.paste(icon, (0, 0))
        img.paste(base, (0, 0), base)

        tsize_t = self.drawText(
            img,
            (890, 270),
            message.content,
            size=55,
            color=(255, 255, 255, 255),
            split_len=20,
        )

        name_y = tsize_t[2] + 50
        tsize_name = self.drawText(
            img,
            (890, name_y),
            f"@{member.display_name}",
            size=28,
            color=(255, 255, 255, 255),
            split_len=25,
            disable_dot_wrap=True,
        )

        id_y = name_y + tsize_name[1] + 10
        self.drawText(
            img,
            (890, id_y),
            member.name,
            size=18,
            color=(180, 180, 180, 255),
            split_len=45,
            disable_dot_wrap=True,
        )

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    async def makeItAQuote(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        await interaction.response.defer()
        pic = await asyncio.to_thread(
            self.createMakeItAQuote,
            message.author,
            message,
            await message.author.display_avatar.read(),
        )
        await interaction.followup.send(file=discord.File(pic, "miq.png"))


async def setup(bot: commands.Bot):
    await bot.add_cog(MiqCog(bot))
