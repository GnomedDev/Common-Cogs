from configparser import ConfigParser
from os.path import exists

import discord
from discord.ext import commands

switch = {
    513423712582762502: 738009431052386304, #tts
    565820959089754119: 738009620601241651, #f@h
    689564772512825363: 738009624443224195 #channel
}

if exists("config.ini"):
    config = ConfigParser()
    config.read("config.ini")

def setup(bot):
    bot.add_cog(Gnome(bot))

class Gnome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_trusted(ctx):
        if not exists("config.ini") and ctx.author.id in (341486397917626381, 438418848811581452):  return True
        elif exists("config.ini") and str(ctx.author.id) in config["Main"]["trusted_ids"]:  return True

        raise commands.errors.NotOwner

    #////////////////////////////////////////////////////////
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
        if not self.bot.supportserver.chunked:
            await self.bot.supportserver.chunk(cache=True)

        ofs_role = self.bot.supportserver.get_role(switch[self.bot.user.id])
        highlighted_ofs = self.bot.supportserver.get_role(703307566654160969)

        people_with_owner_of_server = [member.id for member in ofs_role.members]
        supportserver_members = [member.id for member in self.bot.supportserver.members]

        chunked_guilds = [guild for guild in self.bot.guilds if guild.chunked]
        chunked_owner_list = [guild.owner.id for guild in chunked_guilds]

        owner_of_server_roles = (738009431052386304, 738009620601241651, 738009624443224195)

        for guild_owner in chunked_owner_list:
            if guild_owner.id not in supportserver_members: continue

            guild_owner = self.bot.supportserver.get_member(guild_owner.id)
            additional_message = False
            embed = False

            if guild_owner.id not in people_with_owner_of_server:
                await guild_owner.add_roles(ofs_role)

                embed = discord.Embed(description=f"Role Added: Gave {role.mention} to {owner.mention}")
                embed.set_author(name=f"{str(owner)} (ID {owner.id})", icon_url=owner.avatar_url)
                embed.set_thumbnail(url=owner.avatar_url)

            for role in owner_of_server_roles:
                if role in guild_owner.roles and highlighted_ofs not in guild_owner.roles:
                    additional_message = f"Added highlighted owner of a server to {member.mention}"
                    await guild_owner.add_roles(highlighted_ofs)
                    break

            if embed or additional_message:
                if not embed: embed = None
                if not additional_message: additional_message = None

                await self.bot.channels["logs"].send(additional_message, embed=embed)

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
