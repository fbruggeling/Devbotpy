import discord
from discord.ext import commands
from async_timeout import timeout
import asyncio
import youtube_dl
import traceback
import functools
import itertools
import math
import random

ctx = commands.Context

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '/downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
players = {}
queues = {}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.1):
        super().__init__(source,  volume)

        self.data = data
        self.requester = ctx.author
        self.channel = ctx.channel

        self.title = data.get('title')
        self.url = data.get('webpage_url')
        self.uploader = data.get('uploader')
        self.duration = data.get('duration')

        self.thumbnail = data.get('thumbnail')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{}'.format(days))
        if hours > 0:
            duration.append('{}'.format(hours))
        if minutes > 0:
            duration.append('{}'.format(minutes))
        if seconds > 0:
            duration.append('{}'.format(seconds))

        return ':'.join(duration)

class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(title='Now playing',
                               description='```css\n{0.source.title}\n```'.format(self),
                               color=discord.Color.blurple())
                 .add_field(name='Duration', value=self.source.duration)
                 .add_field(name='Requested by', value=self.requester.mention)
                 .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                 .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail))

        return embed

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
    def __init__(self, ctx: commands.Context):
        self.guild = ctx.guild
        self.bot = ctx.bot
        self.skip_votes = set()

        self.queue = SongQueue()
        self.next = asyncio.Event()

        self.current = None
        self.voice = None
        self.skip_votes = set()

        self.bot.loop.create_task(self.player_loop(ctx))

    async def player_loop(self, ctx):
        while not self.bot.is_closed():
            print("Loop!")
            self.next.clear()
            try:
                async with timeout(300):
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                break

            print("Got a source from the queue.")
            self.guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            await ctx.send(f":headphones:**Now Playing:**`{source.title}`")
            await self.next.wait()

    def skip(self):
            self.skip_votes.clear()

            if self.is_playing:
                self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None



def get_player(ctx):
    try:
        player = players[ctx.guild.id]
        print("Loaded Existing Player.")
    except KeyError:
        player = Player(ctx)
        players[ctx.guild.id] = player
        print("Created a new player.")
    return player



class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    @commands.command(aliases=["connect"])
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        player = get_player(ctx)
        await channel.connect()

        await ctx.send(f":headphones:**Joined `{channel}` and bound to **`{ctx.message.channel}`")

    @commands.command()
    async def leave(self, ctx):

        await ctx.voice_client.disconnect()
        await ctx.send(":white_check_mark: **Succesfully disconnected**")

    @commands.command(aliases=["sing"])
    async def play(self, ctx, *, url):

        async with ctx.typing():
            source = await YTDLSource.from_url(url, loop=self.bot.loop)
            player = get_player(ctx)
            print("Inserting new source into queue.")
            await player.queue.put(source)

        embed = discord.Embed(

            title=source.title,
            url=source.url,
            color=0xffffff

        )

        embed.set_author(name="Added to queue", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=source.url)
        embed.add_field(name="Uploaded By", value=source.uploader)
        embed.add_field(name="Duration", value=source.duration)

        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    async def stream(self, ctx, *, url):

        async with ctx.typing():
            source = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            player = get_player(ctx)
            print("Inserting new source into queue.")
            await player.queue.put(source)

        embed = discord.Embed(

            title=source.title,
            url=source.url,
            color=0xffffff

        )

        embed.set_author(name="Added to queue", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=source.url)
        embed.add_field(name="Uploaded By", value=source.uploader)
        embed.add_field(name="Duration", value=source.duration)

        await ctx.send(embed=embed)
        await ctx.message.delete()

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")

    @commands.command(aliases=["stahp"])
    async def stop(self, ctx):

        player = get_player(ctx)

        player.queue.clear()
        ctx.voice_client.stop()

        await ctx.send("**Music has been stopped!**")
        await ctx.message.delete()

    @commands.command()
    async def skip(self, ctx):

        async with ctx.typing():
            ctx.voice_client.stop()

        await ctx.send(f"{ctx.author} force skipped the song!")
        await ctx.message.delete()

    @commands.command(aliases=["vol"])
    async def volume(self, ctx, volume: int):

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        if not 0 < volume <= 100:
            return await ctx.send('Please enter a value between 1 and 100.')
        else:

            ctx.voice_client.source.volume = volume / 100
            await ctx.send("Changed volume to {}%".format(volume))
            await ctx.message.delete()

    @commands.command()
    async def pause(self, ctx):

        async with ctx.typing():
            ctx.voice_client.pause()

        await ctx.send(':musical_note: **The music is paused** :musical_note:')
        await ctx.message.delete()

    @commands.command()
    async def resume(self, ctx):
        """Resumes music"""

        async with ctx.typing():
            ctx.voice_client.resume()

        await ctx.send(':musical_note: **The music is resumed** :musical_note:')
        await ctx.message.delete()

    @commands.command()
    async def playlocal(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(query))


    @commands.command(aliases=["q", "que"])
    async def queue(self, ctx, *, page: int =1):

        player = get_player(ctx)

        if len(Song.songs) == 0:
            return await ctx.send('Empty queue')

        items_per_page = 10
        pages = math.ceil(len(Song.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start +items_per_page

        queue = ''
        for i, song in enumerate(Song.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(Song.songs), queue))
                 .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Music(bot))