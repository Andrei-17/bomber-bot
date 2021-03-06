from discord.ext import commands
from discord.utils import get
import discord
import functions
import datetime
import main

class DevCommands(commands.Cog):
    months = {
        "01":"January",
        "02":"February",
        "03":"March",
        "04":"April",
        "05":"May",
        "06":"June",
        "07":"July",
        "08":"August",
        "09":"September",
        "10":"October",
        "11":"November",
        "12":"December"
    }

    def __init__(self, client):
        self.client = client

    async def isDev(ctx):
        config = functions.getConfig()
        if ctx.message.author.guild.id == config["myGuild"]:
            for role in ctx.message.author.roles:
                if role.id == config["developer"]:
                    return True
        return False

    @commands.Cog.listener()
    async def on_ready(self):
        config = functions.getConfig()
        self.myGuild = get(self.client.guilds, id=config["myGuild"])
        self.myLog = get(self.myGuild.channels, id=config["myLog"])
        self.devRole = get(self.myGuild.roles, id=config["developer"])

    def getRegionText(self, region):
        text = str(region)
        newText = ""
        for char in text:
            if char == "-":
                newText += " "
            else:
                newText += char
        finalText = ""
        for word in newText.split():
            if word != "us":
                finalText += f"{word.capitalize()} "
            else:
                finalText += "US "
        if finalText.endswith(" "):
            finalText = finalText[:-1]
        return finalText

    def getBots(self, guild):
        num = 0
        for member in guild.members:
            if member.bot:
                num += 1
        return num

    def getGuildRoles(self, guild):
        roles = guild.me.roles
        text = ""
        if len(roles) == 1:
            roles.append("It seems like the bot does not have any role.")
        for role in roles:
            if str(role) != "@everyone":
                text += "\n-{}".format(str(role))
        return text

    def getErrorEmbed(self):
        embed = discord.Embed(colour=discord.Colour(0xcf3737), description="An errror occurred.\n\nCheck if the ID is correct.")
        embed.set_thumbnail(url="https://i.ibb.co/vPCz0jL/706450053656608768.gif")
        embed.set_author(name="Error!", url="https://discordapp.com", icon_url="https://i.ibb.co/vPCz0jL/706450053656608768.gif")
        return embed

    def getGuildJoinTime(self, guild):
        dateList = str(datetime.datetime.utcfromtimestamp(guild.me.joined_at.timestamp())).split()
        date = dateList[0].split("-")
        return f"{date[2]} {self.months[date[1]]} {date[0]} at {dateList[1][:-10]}"

    @commands.command()
    @commands.check(isDev)
    async def guilds(self, ctx):
        guilds = self.client.guilds
        messages = []
        index = 0
        for guild in guilds:
            if index == 0:
                message = "\u0060\u0060\u0060\n"
            message += "{}  \u007c  {}".format(guild.id, len(guild.members),str(guild))
            spacesNum = 4 - len(str(len(guild.members)))
            message += (" " * spacesNum)
            message += "\u007c  {}\n".format(str(guild))
            index += 1
            if index > 4:
                message += "\u0060\u0060\u0060"
                messages.append(message)
                index = 0
        if not message in messages:
            message += "\u0060\u0060\u0060"
            messages.append(message)
        await ctx.send("Current guilds: {}".format(len(guilds)))
        for elem in messages:
            await ctx.send(elem)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        embed = discord.Embed(title=str(guild), colour=discord.Colour(0x497aad),
                              description=f":crown: **Owner**: <@{guild.owner_id}>\n:man_raising_hand: **Users**: {len(guild.members)}\n:robot: **Bots**: {self.getBots(guild)}\n\n:globe_with_meridians: **Region**: {self.getRegionText(guild.region)}\n:bar_chart: **Total servers**: {len(self.client.guilds)}",
                              timestamp=datetime.datetime.utcfromtimestamp(datetime.datetime.now().timestamp()))
        embed.set_thumbnail(url=guild.icon_url)
        embed.set_author(name="Just joined a new server!", icon_url="https://i.ibb.co/MP2yJy8/509735362994896924.gif")
        embed.set_footer(text=str(guild.id))

        await self.myLog.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        embed = discord.Embed(title=str(guild), colour=discord.Colour(0xc76c5a),
                              description=f":crown: **Owner**: <@{guild.owner_id}>\n:man_raising_hand: **Users**: {len(guild.members)}\n:robot: **Bots**: {self.getBots(guild)}\n\n:globe_with_meridians: **Region**: {self.getRegionText(guild.region)}\n:bar_chart: **Total servers**: {len(self.client.guilds)}",
                              timestamp=datetime.datetime.utcfromtimestamp(datetime.datetime.now().timestamp()))
        embed.set_thumbnail(url=guild.icon_url)
        embed.set_author(name="Just been kicked from a server!", icon_url="https://i.ibb.co/8Y0W9Fk/angery.gif")
        embed.set_footer(text=str(guild.id))

        await self.myLog.send(embed=embed)

    @commands.command()
    @commands.check(isDev)
    async def info(self, ctx, id):
        if id.isdecimal():
            guild = get(self.client.guilds, id=int(id))
            if guild != None:
                embed = discord.Embed(colour=discord.Colour(0x497aad), description=f":crown: **Owner**: <@{guild.owner_id}>\n:man_raising_hand: **Users**: {len(guild.members)}\n:robot: **Bots**: {self.getBots(guild)}\n\n:globe_with_meridians: **Region**: {self.getRegionText(guild.region)}\n:date: **Joined**: {self.getGuildJoinTime(guild)}\n\n<:arrowroles:735564270552744098> **Bot Roles** <:arrowroles:735564270552744098>{self.getGuildRoles(guild)}")
                embed.set_thumbnail(url=guild.icon_url)
                embed.set_author(name=str(guild))
            else:
                embed = self.getErrorEmbed()
        else:
            embed = self.getErrorEmbed()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(isDev)
    async def presence(self, ctx, activity):
        activity = activity.lower()
        if activity == "online":
            await self.client.change_presence(status=discord.Status.online)
            activityText = "Online"
        elif activity == "dnd":
            await self.client.change_presence(status=discord.Status.dnd)
            activityText = "Do Not Disturb"
        elif activity == "idle":
            await self.client.change_presence(status=discord.Status.idle)
            activityText = "Idle"
        elif activity == "invisible":
            await self.client.change_presence(status=discord.Status.invisible)
            activityText = "Invisible"
        else:
            activityText = None
        if activityText:
            await ctx.send("The presence has been changed to: {}.".format(activityText))
        else:
            await ctx.send("The activity you specified is incorrect.")

def setup(client):
    client.add_cog(DevCommands(client))
