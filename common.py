import asyncio
from configparser import ConfigParser
import os
import shutil
import time
import typing
from inspect import cleandoc

import discord
from discord.ext import commands, tasks


def setup(bot):
    bot.add_cog(Gnome(bot))

class Gnome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_trusted(ctx):
        if not os.path.exists("config.ini") and ctx.author.id in (341486397917626381, 438418848811581452):
            return True
        elif os.path.exists("config.ini"):
            config = ConfigParser()
            config.read("config.ini")
            if str(ctx.author.id) in config["Main"]["trusted_ids"]: return True

        raise commands.errors.NotOwner

    #////////////////////////////////////////////////////////
    @commands.command()
    @commands.bot_has_permissions(send_messages=True, read_messages=True)
    async def donate(self, ctx):
        await ctx.send(f"To donate to support the development and hosting of {self.bot.user.mention}, you can donate via Patreon!\nhttps://www.patreon.com/Gnome_the_Bot_Maker")

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

    @commands.command()
    @commands.bot_has_permissions(read_messages=True, send_messages=True)
    async def lag(self, ctx):
        before = time.monotonic()
        message1 = await ctx.send("Loading!")
        ping = (time.monotonic() - before) * 1000
        await message1.edit(content=f"Current Latency: `{int(ping)}ms`")

    @commands.command()
    @commands.bot_has_permissions(read_messages=True, send_messages=True)
    async def suggest(self, ctx, *, suggestion):
        if suggestion.lower() == "*suggestion*":
            return await ctx.send("Hey! You are meant to replace `*suggestion*` with your actual suggestion!")

        if os.path.exists("config.ini"):
            if ctx.message.author.id not in self.bot.blocked_users:
                webhook = await self.bot.channels["suggestions"].create_webhook(name=str(ctx.message.author))
                if ctx.message.attachments:
                    files = [await attachment.to_file() for attachment in ctx.message.attachments]
                else:
                    files = None
                await webhook.send(suggestion, avatar_url=ctx.message.author.avatar_url, files=files)
                await webhook.delete()
        else:
            await self.bot.get_channel(696325283296444498).send(f"{str(ctx.author)} in {ctx.guild.name} suggested: {suggestion}")
        await ctx.send("Suggestion noted")

    @commands.command()
    @commands.bot_has_permissions(read_messages=True, send_messages=True)
    async def invite(self, ctx):
        try:
            config = ConfigParser()
            config.read("config.ini")
            if str(ctx.guild.id) == str(config["Main"]["main_server"]):
                await ctx.send(f"Check out <#694127922801410119> to invite {self.bot.user.mention}!")
            else:
                await ctx.send(f"Join https://discord.gg/zWPWwQC and look in #{self.bot.get_channel(694127922801410119).name} to invite {self.bot.user.mention}!")
        except:
            await ctx.send(f"To invite {self.bot.user.mention}, join <https://discord.gg/zWPWwQC> and the invites are in '#invites-and-rules'!")

    @commands.command()
    @commands.check(is_trusted)
    @commands.bot_has_permissions(read_messages=True, send_messages=True)
    async def getinvite(self, ctx, guild: int):
        invite = False
        guild = self.bot.get_guild(guild)

        for channel in guild.channels:
            try:    invite = str(await channel.create_invite())
            except: continue
            if invite:
                return await ctx.send(f"Invite to {guild.name} | {guild.id}: {invite}")

        await ctx.send("Error: No permissions to make an invite!")

    @commands.command()
    @commands.check(is_trusted)
    @commands.bot_has_permissions(read_messages=True, send_messages=True)
    async def dm(self, ctx, todm: discord.User, *, message):
        embed = discord.Embed(title="Message from the developers:", description=message)
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)

        sent = await todm.send(embed=embed)
        await ctx.send(f"Sent message to {str(todm)}:", embed=sent.embeds[0])

    @commands.command()
    @commands.check(is_trusted)
    @commands.bot_has_permissions(read_messages=True, send_messages=True, embed_links=True)
    async def r(self, ctx, *, message):
        async for history_message in ctx.channel.history(limit=10):
            if history_message.author.discriminator == "0000":
                converter = commands.UserConverter()
                todm = await converter.convert(ctx,history_message.author.name)
                return await self.dm(ctx, todm, message=message)
        await ctx.send("Webhook not found")

    @commands.command()
    @commands.check(is_trusted)
    @commands.bot_has_permissions(read_messages=True, send_messages=True)
    async def refreshroles(self, ctx):
        targetguild = self.bot.get_guild(693901918342217758)
        switch = {
          513423712582762502: 738009431052386304, #tts
          565820959089754119: 738009620601241651, #f@h
          689564772512825363: 738009624443224195 #channel
        }

        role = targetguild.get_role(switch[self.bot.user.id])
        owner_id_list = [guild.owner.id for guild in self.bot.guilds]

        for member in targetguild.members:
            owner = member
            member_roles = [I_have_role.id for I_have_role in member.roles]

            if role.id in member_roles:
                if member.id not in owner_id_list:
                    await member.remove_roles(role)

                    nope = 0
                    for id in [738009431052386304, 738009620601241651, 738009624443224195]:
                        if id not in member_roles:
                            nope += 1
                    if nope == 3:
                        await member.remove_roles(targetguild.get_role(703307566654160969))

                    embed = discord.Embed(description=f"Role Removed: Removed {role.mention} from {owner.mention}\n**Reason:** No longer Owner of a Server")
                    embed.set_author(name=f"{str(owner)} (ID {owner.id})", icon_url=owner.avatar_url)
                    embed.set_thumbnail(url=owner.avatar_url)

                    await self.bot.get_channel(696347411966066689).send(embed=embed)
            else:
                if member.id in owner_id_list:
                    await member.add_roles(role)

                    embed = discord.Embed(description=f"Role Added: Gave {role.mention} to {owner.mention}\n**Reason:** Owner of a Server but not added by on_guild_join")
                    embed.set_author(name=f"{str(owner)} (ID {owner.id})", icon_url=owner.avatar_url)
                    embed.set_thumbnail(url=owner.avatar_url)

                    await self.bot.get_channel(696347411966066689).send(embed=embed)

            member_roles = [I_have_role.id for I_have_role in member.roles]
            for a_id in (738009431052386304, 738009620601241651, 738009624443224195):
                if a_id in member_roles and 703307566654160969 not in member_roles:
                    await member.add_roles(targetguild.get_role(703307566654160969))
                    await self.bot.get_channel(696347411966066689).send(f"Added highlighted owner of a server to {member.mention}")
                    break
        await ctx.send("Done!")

    @commands.command()
    @commands.check(is_trusted)
    @commands.bot_has_permissions(read_messages=True, send_messages=True, embed_links=True)
    async def lookupinfo(self, ctx, mode, *, guild):
        mode = mode.lower()
        guild_object = False

        if mode == "id":
            guild_object = self.bot.get_guild(int(guild))

        elif mode == "name":
            for all_guild in self.bot.guilds:
                if guild in all_guild.name:
                    guild_object = all_guild

        if guild_object is False:
            raise commands.BadArgument

        embed = discord.Embed(title=guild_object.name)
        embed.add_field(name="Guild ID", value=guild_object.id, inline=False)
        embed.add_field(name="Owner Name | ID", value=f"{guild_object.owner.name} | {guild_object.owner.id}", inline=False)
        embed.add_field(name="Member Count", value=guild_object.member_count, inline=False)
        embed.set_thumbnail(url=str(guild_object.icon_url))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(is_trusted)
    @commands.bot_has_permissions(read_messages=True, send_messages=True, attach_files=True)
    async def serverlist(self, ctx):
        servers = [guild.name for guild in self.bot.guilds]

        if len(str(servers)) >= 2000:
            with open("servers.txt", "w") as f: f.write(str(servers))
            await ctx.send(file=discord.File("servers.txt"))
        else:
            await ctx.send(servers)

    @commands.command()
    @commands.is_owner()
    @commands.bot_has_permissions(read_messages=True, send_messages=True, manage_messages=True, manage_webhooks=True)
    async def sudo(self, ctx, user: typing.Union[discord.Member, discord.User, str], *, message):
        """mimics another user"""
        await ctx.message.delete()
        if isinstance(user, str):
            name = user
            avatar = "https://cdn.discordapp.com/avatars/689564772512825363/f05524fd9e011108fd227b85c53e3d87.png"
        else:
            name = user.display_name
            avatar = user.avatar_url

        webhooks = await ctx.channel.webhooks()
        if len(webhooks) == 0:
            webhook = await ctx.channel.create_webhook(name="Temp Webhook For -sudo")
            await webhook.send(message, username=name, avatar_url=avatar)
            await webhook.delete()
        else:
            webhook = webhooks[0]
            await webhook.send(message, username=name, avatar_url=avatar)

    @commands.command()
    @commands.is_owner()
    @commands.bot_has_permissions(read_messages=True, send_messages=True)
    async def say(self, ctx, channel: discord.TextChannel, *, tosay):
        try:    await ctx.message.delete()
        except: pass

        await channel.send(tosay)

    @commands.command()
    @commands.is_owner()
    async def reload_cog(self, ctx, *, toreload: str):
        try:
            self.bot.reload_extension(toreload)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command()
    @commands.is_owner()
    async def end(self, ctx):
        await self.bot.close()

    @commands.command()
    @commands.is_owner()
    async def leaveguild(self, ctx, guild : int):
        await self.bot.get_guild(guild).leave()
#//////////////////////////////////////////////////////

    @commands.command()
    @commands.check(is_trusted)
    async def changeactivity(self, ctx, *, activity: str):
        with open("activity.txt", "w") as f1, open("activitytype.txt") as f2, open("status.txt") as f3:
            f1.write(activity)
            activitytype = f2.read()
            status = f3.read()
        activitytype = getattr(discord.ActivityType, activitytype)
        status = getattr(discord.Status, status)
        await self.bot.change_presence(status=status, activity=discord.Activity(name=activity, type=activitytype))
        await ctx.send(f"Changed activity to: {activity}")

    @commands.command()
    @commands.check(is_trusted)
    async def changetype(self, ctx, *, activitytype: str):
        with open("activity.txt") as f1, open("activitytype.txt", "w") as f2, open("status.txt") as f3:
            activity = f1.read()
            f2.write(activitytype)
            status = f3.read()
        activitytype1 = getattr(discord.ActivityType, activitytype)
        status = getattr(discord.Status, status)
        await self.bot.change_presence(status=status, activity=discord.Activity(name=activity, type=activitytype1))
        await ctx.send(f"Changed activity type to: {activitytype}")

    @commands.command()
    @commands.check(is_trusted)
    async def changestatus(self, ctx, *, status: str):
        with open("activity.txt") as f1, open("activitytype.txt") as f2, open("status.txt", "w") as f3:
            activity = f1.read()
            activitytype = f2.read()
            f3.write(status)
        activitytype = getattr(discord.ActivityType, activitytype)
        status1 = getattr(discord.Status, status)
        await self.bot.change_presence(status=status1, activity=discord.Activity(name=activity, type=activitytype))
        await ctx.send(f"Changed status to: {status}")
