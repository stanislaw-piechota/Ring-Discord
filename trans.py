import asyncio
import discord
from discord.ext import commands
from googletrans import Translator

trns = Translator().translate

class Trans(commands.Cog):
    def __init__(self, bot, dt):
        self.bot = bot; self.dt = dt

    async def log(self, message):
        await self.bot.get_channel(780912356573184020).send(message)

    @commands.command(brief='trans [pl/en/es/ru] "text"')
    async def trans(self, ctx, lang: str, phrase: str):
        serv = ctx.guild.name
        await self.log(f'{self.dt()} TRANS {serv} {ctx.author}')
        try:
            avlb = ['pl', 'en', 'ru', 'es']
            if lang in avlb:
                mess = ''
                trnsd = trns(phrase, dest=lang)
                mess += trnsd.text
                if lang == 'ru':
                    mess += '\nPronunciation: '+trnsd.pronunciation
                await ctx.send(f'Translated text:\n```\n{mess}\n```')
            else:
                await ctx.send('This language is not allowed')
        except Exception as e:
            print(e)
            await ctx.send('This command is temporary unavaliable, because of Google API error')

    @commands.command(brief='ru text')
    async def ru(self, ctx, *args):
        serv = ctx.guild.name
        await self.log(f'{self.dt()} RU {serv} {ctx.author}')
        try:
            trnsd = trns(' '.join(args), dest='ru')
            mess = trnsd.text + '\nPronunciation: '+trnsd.pronunciation
            await ctx.send(f'Translated text:\n```\n{mess}\n```')
        except Exception as e:
            print(e)
            await ctx.send('This command is temporary unavaliable, because of Google API error')
