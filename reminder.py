import discord
from discord.ext import commands

class reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def remind(self, ctx):
        user = ctx.author

        
