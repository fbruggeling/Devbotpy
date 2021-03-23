import discord.ext
import random
import asyncio
import logging as log
import aiohttp
import json
import time
import os
import discord
import requests
import sys
from discord import Game
from discord.ext import commands

class Extensions(commands.Cog):
    __slots__ = ('bot', 'log')
    
    def __init__(self, bot):
        self.bot = bot
        self.log = log

    @commands.is_owner()
    @commands.command(hidden=True)
    async def reload(self, ctx, *, extension):
    #async def reload(self, ctx):
        """Reload an extension"""
        #await ctx.message.delete()
        async with ctx.typing():
            embed = discord.Embed(description="**Reloading extension** " + extension, color=0x0066cc)
            await ctx.send(embed=embed)
            try:
                self.bot.reload_extension(extension)
                print('Reloaded extension ' + str(extension))
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                await ctx.send('Failed to reload extension {}\n{}'.format(extension, exc))
                print('Failed to reload extension {}\n{}'.format(extension, exc))
    
    @commands.is_owner()
    @commands.command(hidden=True)
    async def load(self, ctx, *, extension):
    #async def reload(self, ctx):
        """Reload an extension"""
        #await ctx.message.delete()
        async with ctx.typing():
            embed = discord.Embed(description="**Loading extension** " + extension, color=0x0066cc)
            await ctx.send(embed=embed)
            try:
                self.bot.load_extension(extension)
                print('Reloaded extension ' + str(extension))
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                await ctx.send('Failed to load extension {}\n{}'.format(extension, exc))
                print('Failed to reload extension {}\n{}'.format(extension, exc))
     
    @commands.is_owner()
    @commands.command(hidden=True)
    async def unload(self, ctx, *, extension):
    #async def reload(self, ctx):
        """Reload an extension"""
        #await ctx.message.delete()
        async with ctx.typing():
            embed = discord.Embed(description="**Unloading extension** " + extension, color=0x0066cc)
            await ctx.send(embed=embed)
            try:
                self.bot.unload_extension(extension)
                print('Reloaded extension ' + str(extension))
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                await ctx.send('Failed to unload extension {}\n{}'.format(extension, exc))
                print('Failed to reload extension {}\n{}'.format(extension, exc))
    @commands.is_owner()
    @commands.command(hidden=True)
    async def restart(self, ctx):
        try:
            await bot.close()
        except:
            pass
        finally:
            sys.exit()
                
def setup(bot):
    bot.add_cog(Extensions(bot))