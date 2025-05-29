import io
from typing import List, Literal, Tuple, Union

import discord
from PIL import Image, ImageDraw, ImageFont, ImageOps


def generateRankingImage(
    title: str,
    ptStr: str,
    users: List[Tuple[Union[discord.User, discord.Member, str], int, bytes]],
    theme: Literal["ダーク", "ライト"] = "ダーク",
):
    width = 800
    iconSize = 48
    padding = 10
    spacing = iconSize + 20
    topMargin = 40
    bottomMargin = 20
    titleHeight = 60

    height = titleHeight + topMargin + len(users) * spacing + bottomMargin

    img = Image.new(
        "RGB",
        (width, height),
        color=(255, 255, 255) if theme == "ライト" else (0, 0, 0),
    )
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("./fonts/NotoSansJP-Medium.ttf", 24)
    smallFont = ImageFont.truetype("./fonts/NotoSansJP-Medium.ttf", 16)
    titleFont = ImageFont.truetype("./fonts/NotoSansJP-Medium.ttf", 28)

    titleWidth = draw.textlength(title, font=titleFont)
    draw.text(
        ((width - titleWidth) // 2, 20),
        title,
        font=titleFont,
        fill=(0, 0, 0) if theme == "ライト" else (255, 255, 255),
    )

    yOffset = topMargin + titleHeight

    for i, (user, count, icon) in enumerate(users):
        if isinstance(user, discord.abc.Snowflake):
            displayName = user.display_name
            userName = f"@{user.name}"
            try:
                avatarImg = Image.open(io.BytesIO(icon)).convert("RGBA")
                avatarImg = ImageOps.fit(
                    avatarImg, (iconSize, iconSize), centering=(0.5, 0.5)
                )
                img.paste(avatarImg, (padding, yOffset), avatarImg)
            except Exception:
                pass
        else:
            displayName = user
            userName = ""

        draw.text(
            (padding + iconSize + 10, yOffset),
            f"{i+1}位: {displayName} - " + ptStr.format(pt=count),
            font=font,
            fill=(0, 0, 0) if theme == "ライト" else (255, 255, 255),
        )
        if userName:
            draw.text(
                (padding + iconSize + 10, yOffset + 30),
                userName,
                font=smallFont,
                fill=(100, 100, 100) if theme == "ライト" else (155, 155, 155),
            )

        yOffset += spacing

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
