import discord
from discord.ext import commands
import random
import json
from discord_slash import SlashCommand, SlashContext


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        channel = self.bot.get_channel(678232569988382720)
        await channel.send('hello')

    @commands.command()
    async def ping(self, ctx):
        """"Dit is een ping command"""
        await ctx.send(':ping_pong:Pong! ' + str(round(self.bot.latency, 1)) + 'ms')
        await ctx.message.delete()

    @commands.command()
    async def tekst(self, ctx, *, tekst):
        """Dit command verstuurt je eigen tekst!"""
        await ctx.send(tekst)
        await ctx.message.delete()

    @commands.command()
    async def about(self, ctx):
        embed = discord.Embed(title='Over deze bot', description='Deze bot is om te testen', color=0xff0000)
        embed.set_footer(text='Author fbruggeling#0001')
        embed.add_field(text='Gemaakt op', value=self.bot.createdAt())
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    async def serverinfo(self, ctx):
        """Dit is een serverinfo command :)"""
        embed = discord.Embed(
            title="Serverinfo",
            description="Dit is de info van deze server",
            color=discord.Color.blue()
        )

        embed.set_footer(text="Owner: " + str(ctx.guild.owner))
        embed.set_image(
            url="https://cdn.discordapp.com/avatars/575727588153098260/c2f7fd4b52afbdcbf1e50c379207d0ed.png?size=128")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_author(name=(ctx.author))
        embed.add_field(name='members', value=(ctx.guild.member_count))
        embed.add_field(name='Date created', value=(ctx.guild.created_at))
        embed.add_field(name='Language', value=(ctx.guild.preferred_locale))
        embed.add_field(name='Boosters', value=(ctx.guild.premium_subscription_count))
        await ctx.send(embed=embed)

    @commands.command()
    async def presence(self, ctx, name):
        await self.bot.change_presence(activity=discord.Game(name=name))
        await ctx.message.delete()

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, limit: int):
        """This is a clear command"""
        await ctx.channel.purge(limit=limit)
        await ctx.send('Clear by {}'.format(ctx.author.mention))
        await ctx.message.delete()

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, command.MissingPermissions):
            await ctx.send('You cant do that!')

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member:discord.Member, *, arg):
        author = ctx.author
        guild = ctx.message.guild
        channel = discord.utils.get(guild.text_channels, name='warn-logs')
        if channel is None:
            channel = await guild.create_text_channel('warn-logs')
        await channel.send(f'{member.mention} warned for: {arg} warned by: {author.mention}')
        await member.send(f'{author.mention} warned you for: {arg}')
        await ctx.message.delete()

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member:discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await member.send('{author.mention} has kicked you for {reason}')
        await ctx.guild.kick()
        await ctx.message.delete()

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member:discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await member.send('{author.mention} has banned you for {reason}')
        await ctx.guild.ban()
        await ctx.message.delete()

    @commands.command()
    async def embed(self, ctx, title: str, *, tekst: str):
        embed = discord.Embed(
            title=str(title),
            description=str(tekst),
            color=discord.Colour.red()
        )
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    async def announce(self, ctx,  *, announcement: str):
        await ctx.send(str(announcement))
        await ctx.message.delete()

    @commands.command()
    async def namepicker(self, ctx, names):
     name_list = names.split(';')
     await ctx.send(random.choice(name_list))
     print(name_list)

    @commands.command()
    async def gta(self, ctx):
        embed= discord.Embed(
            title="Wie doet er mee met gta",
            description=":white_check_mark: = Ja :negative_squared_cross_mark: = Nee",
            color= discord.Colour.green()
        )

        await ctx.send(embed=embed)
        await ctx.add_reaction('212e30e47232be03033a87dc58edaa95')
        await ctx.add_reaction('d17d69c79096244f30760ec441f76933')

    @commands.command(usage="<argument>")
    @commands.is_owner()
    async def tag(self, ctx, member: discord.Member, count: int):
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    for x in range(0, count):
                        await channel.send("<@{}>".format(member.id))
                except Exception as e:
                    print(e)

    @commands.command()
    async def number(self, ctx):
        cards = ['1', '2', '3', '4', '5', '6']
        await ctx.send("You chose number {}".format(random.choice(cards)))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, guild_prefix=None):
        """Get the current prefix for this guild or choose another one"""
        with open("prefixes.json") as prefix_read:
            prefix_json = json.load(prefix_read)
        if not guild_prefix:
            try:
                guild_prefix = prefix_json[str(self.bot.user.id)][str(ctx.guild.id)]
            except KeyError:
                guild_prefix = '*'
            description = ""
        else:
            prefix_json[str(self.bot.user.id)][str(ctx.guild.id)] = guild_prefix
            with open("prefixes.json", "w+") as prefix_write:
                prefix_write.write(json.dumps(prefix_json))
            description = "Prefix changed!"
        embed = discord.Embed(description="{} Use `{}` or <@{}> in this guild".format(description, guild_prefix,
                                                                                      self.bot.user.id))
        await ctx.send(embed=embed)




def setup(bot):
    bot.add_cog(Commands(bot))
