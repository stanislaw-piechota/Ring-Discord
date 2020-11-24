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

with open('perms.json') as f:
    data = json.loads(f.read())
dt = datetime.datetime.now

bot = commands.Bot(command_prefix="//", description='End of lesson is here')

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

bot.add_cog(Ring(bot, data, dt))
bot.add_cog(Trans(bot, dt))
bot.add_cog(Perms(bot, data, dt))
bot.run(token1, reconnect=True)
