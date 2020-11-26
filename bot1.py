#https://discord.com/api/oauth2/authorize?client_id=773874155807834113&permissions=8&scope=bot

import asyncio
import discord
import json
from secrets import token1, token2
from discord.ext import commands
from ring import Ring
from trans import Trans
from perms import Perms
import datetime
import aiohttp

with open('perms.json') as f:
    data = json.loads(f.read())
dt = datetime.datetime.now

bot = commands.Bot(command_prefix="//", description='End of lesson is here')

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

@bot.command(brief='Displays changelog')
async def changelog(ctx):
    file = discord.File("changelog.txt")
    await ctx.send("Changelog **v2.2.0**", file=file)

@bot.command()
async def covid(ctx):
    async with ctx.typing():
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://koronawirus.abczdrowie.pl/#koronawirus-w-polsce') as r:
                resp = await r.text()

        last = resp.find(' dziś')
        new_infections = resp[last-10:last].split('+')[1]

        last -= 13
        infections = resp[last-10:last].split('>')[1]

        embed = discord.Embed(title='COVID statistics', color=0xef3f2d)
        embed.add_field(name="New infections", value=new_infections, inline=True)
        embed.add_field(name="Infections", value=infections, inline=True)
        await ctx.send(embed=embed)

bot.add_cog(Ring(bot, data, dt))
bot.add_cog(Trans(bot, dt))
bot.add_cog(Perms(bot, data, dt))
bot.run(token1, reconnect=True)
