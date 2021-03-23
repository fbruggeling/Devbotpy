import discord
from discord.ext import commands
from icalendar import Calendar
import urllib.request


class Rooster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dingetjeslijst = []

    def download(self):
        print('Beginning file download with urllib2...')
        url = 'https://calendar.google.com/calendar/ical/fbruggeling%40gmail.com/private-e07f26c46b7d739d9f3345d38d54c926/basic.ics'
        urllib.request.urlretrieve(url, 'basic.ics')

    def read(self):
        self.dingetjeslijst = []
        with open('basic.ics', 'rb') as g:
            gcal = Calendar.from_ical(g.read())
            for component in gcal.walk():
                if component.name == 'VEVENT':
                    dingetje = component.get('SUMMARY').to_ical().decode("utf-8")
                    dingetje = str(dingetje)
                    self.dingetjeslijst.append(dingetje)

    @commands.command()
    async def rooster(self, ctx):
        self.download()
        self.read()
        rooster_embed = ""
        for item in self.dingetjeslijst:
            rooster_embed += item + '\n'
        embed = discord.Embed(
            title="Rooster",
            description=rooster_embed,
            color=discord.Color.blue()
        )
        embed.set_author(name=(ctx.author))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Rooster(bot))