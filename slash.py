import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashCommandOptionType, SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

class slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="ping", description="Ping Pong!", guild_ids=[455481676542377995])
    async def ping(self, ctx):
        await ctx.send(':ping_pong:Pong! ' + str(round(self.bot.latency, 1)) + 'ms')

    options = [
    {
        "name" : "name",
        "description" : "Your new presence",
        "required" : True,
        "type" : "3"

    }
    ]

    @cog_ext.cog_slash(name="presence", description="an presence command", guild_ids=[455481676542377995], options= options)
    async def presence(self, ctx, name):
     await self.bot.change_presence(activity=discord.Game(name=name))
     await ctx.send("Presence was changed")


def setup(bot):
    bot.add_cog(slash(bot))