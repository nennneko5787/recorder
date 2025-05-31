import os

import discord
import dotenv
from discord.ext import commands

dotenv.load_dotenv()
discord.opus._load_default()


bot = commands.Bot([], intents=discord.Intents.all())


@bot.event
async def setup_hook():
    await bot.load_extension("cogs.record")
    await bot.load_extension("cogs.oneday")
    await bot.load_extension("cogs.stat")
    await bot.load_extension("cogs.aichat")
    await bot.load_extension("cogs.miq")
    await bot.load_extension("cogs.tools")
    await bot.load_extension("cogs.guide")
    await bot.load_extension("cogs.lightout")
    await bot.load_extension("cogs.splash")
    await bot.load_extension("cogs.shiritori")
    await bot.tree.sync()


bot.run(os.getenv("discord"))
