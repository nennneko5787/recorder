import random

import discord
from discord import app_commands
from discord.ext import commands


class GuideCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def randomTaka(self) -> str:
        num = random.random()
        if num <= 0.01:  # 1%
            return "親愛なるたか将軍様"
        elif num <= 0.02:  # 1%
            return "たかなる"
        else:
            return "たかさん"

    group = app_commands.Group(name="guide", description="ああBotの歩き方をご紹介。")

    @group.command(name="intro", description="ガイドの説明。")
    async def introCommand(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            discord.Embed(
                title="ようこそ ああ(Botのサーバー)へ！",
                description=f"""このコマンドグループでは{self.randomTaka()}が運営する「ああ(Botのサーバー)」での話し方について解説します。
なおこのガイドは**非公式**かつ**不定期更新**なので**最新の情報が反映されていない**可能性があります。ご了承ください。""",
                color=discord.Color.blurple(),
            )
        )

    @group.command(name="gairai", description="特定外来生物システムの説明。")
    async def gairaiCommand(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=discord.Embed(
                title="特定外来生物システムとは",
                description="""特定外来生物は、**スパム**や**特定の行動**をするメンバーを**自動で検知し隔離**するためのシステムです。
以下の行動を行うと特定外来生物ロールが付きます。
- 7秒間に6回以上のメッセージを送信する。
- everyone, here を送信する。(sayコマンドを含む)
- スパムロールがついた状態でサーバーから退出する。
- 警告(文字の大きさやリンクなど)が出ているときにもう一回警告を出す。
- チカチカするリアクションをつける。
- その他ガイジ行動を起こす。""",
                color=discord.Color.blurple(),
            ).add_field(
                name="間違って特定外来生物に指定されてしまった！",
                value="""**間違えてもそんなところには行くことはありません。**
もし**本当に間違えて行ってしまった**のならば**コインロールを持ったメンバー**の人にメンションしてみてください。""",
                inline=True,
            )
        )

    @group.command(name="bedrock", description="ベッドロックの説明。")
    async def bedrockCommand(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=discord.Embed(
                title="ベッドロックどこですか",
                description=f"""<#1362411697821974538> に貼ってあるサーバーへ行ってください。メンバー一覧にベッドロックがあるはずです。""",
                color=discord.Color.blurple(),
            ).add_field(
                name="call権限の値段、毎回変わってるんですが…詐欺ですか？",
                value="""call権限の値段は__mを /datacheck コマンドで確認できる人数と定義__すると
**call権限の値段 = random.randint(m - 50, m)**
となります。(わからなければrandom.randintをgooleで検索してください。""",
                inline=False,
            )
        )

    @group.command(name="1day", description="1day-chatとコインロールの説明。")
    async def oneDayCommand(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=discord.Embed(
                title="<#1378025158228312126> とはなんですか？",
                description="""
**0:00に消される**チャンネルです。
**危ない話題**を扱うことができます。
…が、現在はこちらのチャンネルでは以下のイベントが人気です。""",
                color=discord.Color.blurple(),
            )
            .add_field(
                name="コインロールってなんですか？",
                value="""**特別な権限**がついた、**一日限りのロール**です。
ついている権限は以下のとおりです。
- revoteコマンドの使用権限 - revote @ユーザー で特定外来生物の投票をやり直すことができます。
- situgayコマンドの使用権限 - situgay @ユーザー でﾝｱｯｰ""",
                inline=False,
            )
            .add_field(
                name="コインロールはどうやって手に入れますか？",
                value="""<#1378025158228312126> でチャンネルが作り直された後にしつじが爆発の画像を送るのでその後一番最初にメッセージを送信するとコインロールを獲得できます。""",
                inline=False,
            )
        )

    @group.command(name="supporter", description="サポーターロールの説明。")
    async def supportCommand(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=discord.Embed(
                title="サポーターロールとはなんですか？",
                description=f"""{self.randomTaka()}に100円以上を献上した神につくロールです。
このロールには、以下の特典がついてきます。
- 特定外来生物システムによるスパム検知の回避(sayコマンド経由のeveryoneや、チカチカするリアクションをつけることによる特定外来生物認定は**回避できません**)
- 特別なチャンネルへの招待
- reasonコマンドの権限""",
                color=discord.Color.blurple(),
            ).add_field(
                name="どうやったらもらえますか？",
                value=f"""{self.randomTaka()}にDMでPayPayかKyashの受取リンクを、「サポーターロールがほしいです！」という文言とともに送ってください。""",
                inline=False,
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(GuideCog(bot))
