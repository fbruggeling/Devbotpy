import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext

class slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    guild_ids = [690553932627312680, 455481676542377995]

    @cog_ext.cog_slash(name="ping", description="Ping Pong!", guild_ids=guild_ids)
    async def ping(self, ctx: SlashContext):
        await ctx.send(':ping_pong:Pong! ' + str(round(self.bot.latency, 1)) + 'ms')

    options = [
    {
        "name" : "name",
        "description" : "Your new presence",
        "required" : True,
        "type" : "3"

    }
    ]

    @cog_ext.cog_slash(name="presence", description="an presence command", guild_ids=guild_ids, options= options)
    async def presence(self, ctx: SlashContext, name):
     await self.bot.change_presence(activity=discord.Game(name=name))
     await ctx.send("Presence was changed")

    @cog_ext.cog_slash(name="")


def setup(bot):
    bot.add_cog(slash(bot))