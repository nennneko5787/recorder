import random

import discord
from discord import app_commands
from discord.ext import commands

SIZE = 5


class LightsOutView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.state = [
            [random.choice([True, False]) for _ in range(SIZE)] for _ in range(SIZE)
        ]
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        for y in range(SIZE):
            for x in range(SIZE):
                label = "◯" if self.state[y][x] else "●"
                self.add_item(self.LightsOutButton(x, y, label, self))

    def toggle(self, x, y):
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < SIZE and 0 <= ny < SIZE:
                self.state[ny][nx] = not self.state[ny][nx]

    def is_cleared(self):
        return all(not cell for row in self.state for cell in row)

    class LightsOutButton(discord.ui.Button):
        def __init__(self, x, y, label, view):
            super().__init__(
                style=discord.ButtonStyle.secondary,
                label=label,
                row=y,
                custom_id=f"{x}-{y}",
            )
            self.x = x
            self.y = y
            self.view_ref = view

        async def callback(self, interaction: discord.Interaction):
            view = self.view_ref
            view.toggle(self.x, self.y)
            if view.is_cleared():
                await interaction.response.edit_message(
                    content="🎉 全マスOFF！クリア！", view=None
                )
            else:
                view.update_buttons()
                await interaction.response.edit_message(
                    content="ライトアウト：ボタンを押して全OFFにしよう！", view=view
                )


class LightOutCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="lightoutgame", description="楽しいライトアウトっていうゲームだよ！"
    )
    async def lightOutGame(self, interaction: discord.Interaction):
        view = LightsOutView()
        await interaction.response.send_message(
            "ライトアウト：ボタンを押して全OFFにしよう！", view=view
        )


async def setup(bot):
    await bot.add_cog(LightOutCog(bot))
