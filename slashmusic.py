import discord
from discord.ext import commands, tasks
from async_timeout import timeout
import asyncio
import yt_dlp as youtube_dl
import traceback
import time
from itertools import cycle
import itertools
import functools
import time
import random
from discord_slash import SlashCommand, SlashCommandOptionType, SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '/downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

guild_ids = [690553932627312680, 455481676542377995]

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
players = {}
queues = {}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.1):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('webpage_url')
        self.uploader = data.get('uploader')
        self.duration = time.strftime('%H:%M:%S', time.gmtime(data.get('duration')))

        self.thumbnail = data.get('thumbnail')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop= loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)




class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]

class Player:
    def __init__(self, ctx):
        self.guild = ctx.guild
        self.bot = ctx.bot

        self.queue = SongQueue()
        self.next = asyncio.Event()
        self._loop = False

        self.bot.loop.create_task(self.player_loop(ctx))


    @property
    def loop(self):
        return self._loop


    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    async def player_loop(self, ctx):
        while not self.bot.is_closed():
            print("loop")
           # self.next.clear()
            try:
                async with timeout(300):
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                break

            print("got a source from the queue")
            self.guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            await ctx.send(f':headphones: **Now Playing:** `{source.title}`')
            await self.next.wait()




def get_player(ctx):
    try:
        player = players[ctx.guild.id]
        print('loaded existing player')
    except KeyError:
        player = Player(ctx)
        players[ctx.guild.id] = player
        print('created new player')
    return player

class slashmusic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="join", description="Joins a voice channel", guild_ids=guild_ids)
    async def join(self, ctx: SlashContext):
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f':loud_sound:**Joined `{channel}` and bound to `{ctx.channel}`**')
        

    @cog_ext.cog_slash(name="leave", description="Leaves a voice channel", guild_ids=guild_ids)
    async def leave(self, ctx: SlashContext):
        """leaves the voice channel"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        await ctx.voice_client.disconnect()
        await ctx.send(":white_check_mark: **Succesfully disconnected**")
    
    play = [
        {
            "name" : "url",
            "description" : "Url or word",
            "required" : True,
            "type" : "3"
        }
    ]

    @cog_ext.cog_slash(name="play", description="An play command", guild_ids=guild_ids, options = play)
    async def play(self, ctx: SlashContext, url):

        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not in a voice channel!")
                raise commands.CommandError("Author not in a voice channel")

        source = await YTDLSource.from_url(url, loop=self.bot.loop)
        player = get_player(ctx)
        print("Inserting new source into queue.")
        await player.queue.put(source)

        
        
        embed= discord.Embed(

            title=source.title,
            url=source.url,
            color=0xffffff

        )

        embed.set_author(name="Added to queue", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=source.thumbnail)
        embed.add_field(name="Uploaded By", value=source.uploader)
        embed.add_field(name="Duration", value=source.duration)


        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="pause", description="An pause command", guild_ids=guild_ids,)
    async def pause(self, ctx: SlashContext):

        if ctx.voice_client is None:
            return await ctx.send("**Not connected to a voice channel**")

        ctx.voice_client.pause()

        await ctx.send(':musical_note:**Music has been paused**:musical_note:')

    @cog_ext.cog_slash(name="resume", description="An resume command", guild_ids=guild_ids)
    async def resume(self, ctx: SlashContext):

        if ctx.voice_client is None:
            return await ctx.send("**Not connected to a voice channel**")

        ctx.voice_client.resume()

        await ctx.send(':musical_note:**Music has been resumed**:musical_note:')

    @cog_ext.cog_slash(name="stop", description="An stop command", guild_ids=guild_ids)
    async def stop(self, ctx: SlashContext):

        if ctx.voice_client is None:
            return await ctx.send("**Not connected to a voice channel**")

        player = get_player(ctx)

        player.queue.clear()
        ctx.voice_client.stop()

        await ctx.send("**Music has been stopped!**")

def setup(bot):
    bot.add_cog(slashmusic(bot))
