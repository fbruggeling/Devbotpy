import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from logdna import LogDNAHandler
import logging
import asyncio
import youtube_dl
import json
import requests

def get_prefix(bot, msg):
    with open('prefixes.json') as prefix_file:
        prefixes = json.load(prefix_file)
    guilds = []
    for guild in prefixes[str(bot.user.id)]:
        guilds.append(str(guild))
    if not msg.guild:
        return commands.when_mentioned_or('*')(bot, msg)
    elif str(msg.guild.id) in guilds:
        return commands.when_mentioned_or(prefixes[str(bot.user.id)][str(msg.guild.id)])(bot, msg)
    else:
        return commands.when_mentioned_or('*')(bot, msg)


bot = commands.Bot(command_prefix=get_prefix)
client = discord.Client()
slash = SlashCommand(bot, sync_commands=True, override_type=True) # Declares slash commands through the cl
extensions = ["Commands", "extensions", "music3", "slash", "slashmusic"]



@bot.event
async def on_ready():
    print('ready')

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="The code"), status=discord.Status.dnd)



@bot.event
async def on_message(ctx):
    if ctx.content.lower().startswith("im ") or ctx.content.lower().startswith("i'm "):
        if ctx.content.lower().startswith("im "):
            msg = ctx.content.lower().replace("im ", "", 1)
        elif ctx.content.lower().startswith("i'm "):
            msg = ctx.content.lower().replace("i'm ", "", 1)
        channel = bot.get_channel(ctx.channel.id)
        await channel.send("Hello " + msg + ", I'm god.")

    await bot.process_commands(ctx)

options = [
    {
        "name" : "name",
        "description" : "Your new presence",
        "required" : True,
        "type" : "3"

    }
]

# @slash.slash(name="presence", description="an presence command", guild_ids=[455481676542377995], options= options)
# async def presence(ctx, name):
#     await bot.change_presence(activity=discord.Game(name=name))
#     await ctx.send("Presence was changed")

# @slash.slash(name="ping", description="Ping Pong!")
# async def ping(ctx):
#     await ctx.send(':ping_pong:Pong! ' + str(round(bot.latency, 1)) + 'ms')

key = '101ce33a48b84f927f5c884d80943590'

options = {
  'hostname': 'Devbot',
  'ip': '10.0.1.1',
  'mac': 'C0:FF:EE:C0:FF:EE'
}

log= logging.getLogger('logdna')
log.setLevel(logging.INFO)
options['index_meta'] = True
main_handler = LogDNAHandler(key, options)
log.addHandler(main_handler)
log.info("Info message")

dc_log = logging.getLogger('discord')
dc_log.setLevel(logging.INFO)
handler = LogDNAHandler(key, options)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
dc_log.addHandler(handler)


class MijnLoggerVoorYTDL:
    def __init__(self, key):
        self.key = key
        self.options = {'hostname': 'Devbot'}
        self.log = logging.getLogger('logdna')
        self.log.setLevel(logging.INFO)
        self.options['index_meta'] = True,
        self.handler = LogDNAHandler(self.key, self.options)
        self.log.addHandler(self.handler)

    def info(self, inhoud):
        self.log.info(inhoud)

    def warning(self, inhoud):
        self.log.warning(inhoud)

    def error(self, inhoud):
        self.log.error(inhoud)

    def exception(self, inhoud):
        self.log.exception(inhoud)

    def debug(self, inhoud):
        # Tijdelijk log.info ipv log.debug door bugs in library logdna
        self.log.info(inhoud)

for extension in extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print(exc)


bot.run("NTc1NzI3NTg4MTUzMDk4MjYw.XNMKGQ.QeJm3qHvgj6R8BYkcPTrweRT48U")
