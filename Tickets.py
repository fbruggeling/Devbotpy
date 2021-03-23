import discord
from discord.ext import commands

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def new(self, ctx, *, arg):
        support_role = ctx.guild.get_role(678244431047950356)

        guild = ctx.message.guild

        ticket = discord.utils.get(guild.text_channels, name="{}s ticket".format(ctx.author))

        if ticket is None:
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                support_role: discord.PermissionOverwrite(read_messages=True),
                ctx.author: discord.PermissionOverwrite(read_messages=True),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
                }

            name = "tickets"

            category = discord.utils.get(ctx.guild.categories, name=name)

            channel = await ctx.guild.create_text_channel('{}s Ticket'.format(ctx.author), overwrites=overwrites, category=category)

            ticket1 = discord.Embed(
                title="ticket",
                description="{}".format(arg)
            )

            embed = discord.Embed(

            name = "Ticket",
            description = "U word zo snel mogelijk geholpen door ons staff team!"

            )

            await channel.send(embed=ticket1)
            await channel.send(embed=embed)


    @commands.command()
    @commands.has_role("Support)
    async def remove(self, ctx, member: discord.member):
        guild = ctx.message.guild
        ticket = discord.utils.get(guild.text_channels, name="{}s ticket".format(ctx.author))
        

def setup(bot):
    bot.add_cog(Tickets(bot))
