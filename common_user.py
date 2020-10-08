from configparser import ConfigParser
from inspect import cleandoc
from os.path import exists

import discord
from discord.ext import commands


def setup(bot):
    if exists("config.ini"):
        config = ConfigParser()
        config.read("config.ini")

    bot.add_cog(User(bot))


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, read_messages=True)
    async def donate(self, ctx):
        await ctx.send(cleandoc(f"""
            To donate to support the development and hosting of {self.bot.user.mention}, you can donate via Patreon (Fees) or directly via DonateBot.io!
            <https://donatebot.io/checkout/693901918342217758?buyer={ctx.author.id}>
            https://www.patreon.com/Gnome_the_Bot_Maker
        """))

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, read_messages=True)
    async def botstats(self, ctx):
        message = cleandoc(f"""
          {self.bot.user.name} in {len(self.bot.guilds)} servers
          {self.bot.user.name} can be used by {sum([guild.member_count for guild in self.bot.guilds]):,} people"""
        )

        embed=discord.Embed(title=f"{self.bot.user.name} Stats", description=message, url="https://discord.gg/zWPWwQC", color=0x5bc0ec)
        embed.set_thumbnail(url="https://publicdomainvectors.org/photos/1462438735.png")
        await ctx.send(embed=embed)

    @commands.command(aliases=["ping"])
    @commands.bot_has_permissions(read_messages=True, send_messages=True)
    async def lag(self, ctx):
        before = time.monotonic()
        message1 = await ctx.send("Loading!")
        ping = (time.monotonic() - before) * 1000
        await message1.edit(content=f"Current Latency: `{int(ping)}ms`")

    @commands.command()
    @commands.bot_has_permissions(read_messages=True, send_messages=True)
    async def suggest(self, ctx, *, suggestion):
        if suggestion.lower().replace("*", "") == "suggestion":
            return await ctx.send("Hey! You are meant to replace `*suggestion*` with your actual suggestion!")

        if exists("config.ini"):
            if ctx.message.author.id not in self.bot.blocked_users:
                files = None
                webhooks = await self.bot.channels["suggestions"].webhooks()

                if len(webhooks) == 0:
                    webhook = await self.bot.channels["suggestions"].create_webhook(name="SUGGESTIONS")
                else:
                    webhook = webhooks[0]

                if ctx.message.attachments:
                    files = [await attachment.to_file() for attachment in ctx.message.attachments]

                await webhook.send(suggestion, username=str(ctx.author), avatar_url=ctx.author.avatar_url, files=files)

        else:
            await self.bot.get_channel(696325283296444498).send(f"{str(ctx.author)} in {ctx.guild.name} suggested: {suggestion}")
        await ctx.send("Suggestion noted")

    @commands.command()
    @commands.bot_has_permissions(read_messages=True, send_messages=True)
    async def invite(self, ctx):
        try:
            if str(ctx.guild.id) == str(config["Main"]["main_server"]):
                await ctx.send(f"Check out <#694127922801410119> to invite {self.bot.user.mention}!")
            else:
                await ctx.send(f"Join https://discord.gg/zWPWwQC and look in #{self.bot.get_channel(694127922801410119).name} to invite {self.bot.user.mention}!")
        except:
            await ctx.send(f"To invite {self.bot.user.mention}, join <https://discord.gg/zWPWwQC> and the invites are in '#invites-and-rules'!")
