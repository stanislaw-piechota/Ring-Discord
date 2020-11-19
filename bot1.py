import asyncio
import discord
from time import sleep
import json
from secrets import token1, token2
from discord.ext import commands
from googletrans import Translator

with open('perms.json') as f:
    data = json.loads(f.read())

trns = Translator().translate

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.volume = data['vol']/100

    def _play(self, ctx, query):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

    @commands.command()
    async def ring(self, ctx):
        if ctx.author.nick[:2] in data['perms']['ring']:
            if ctx.author.voice:
                try:
                    ctx.voice_client.disconnect()
                except:
                    pass
                finally:
                    try:
                        await ctx.author.voice.channel.connect()
                    except:
                        await ctx.send('Bot already joined channel. Please wait')
            else:
                await ctx.send("You are not connected to a voice channel.")
                return
            self._play(ctx, 'dzwonek.mp3')
            ctx.voice_client.source.volume = self.volume
            await asyncio.sleep(3)
            await ctx.voice_client.disconnect()
        else:
            await ctx.send('You don\'t have permissions to invoke this command')

    '''@commands.command()
    async def stop(self, ctx):
        if ctx.author.nick[:2] in data['stop']:
            if ctx.voice_client:
                await ctx.voice_client.disconnect()
        else:
            await ctx.send('You don\'t have permissions to invoke this command')'''

    @commands.command(brief='grant [perm / help] [@ping ...] - grants permission')
    async def grant(self, ctx, perm : str):
        if ctx.author.nick[:2] in data['perms']['grant']:
            if perm == 'help':
                await ctx.send('You can grant following permissions:\n```\nall\ngrant\nring\nvolume```')
                return
            try:
                new = ctx.message.mentions[0].nick[:2]
            except:
                await ctx.send('You have to mention user')
                return
            if perm=='all':
                for k in data['perms'].keys():
                    if new not in data['perms'][k]:
                        data['perms'][k].append(new)
            else:
                if new not in data['perms'][perm]:
                    data['perms'][perm].append(new)
            with open('perms.json', 'w') as f:
                f.write(json.dumps(data))
            await ctx.send(f'Permission **{perm}** granted for user **{new}**')
        else:
            await ctx.send('You don\'t have permissions to invoke this command')

    @commands.command(brief='ungrant [perm / help] [@ping ...] - takes away permission')
    async def ungrant(self, ctx, perm : str):
        if ctx.author.nick[:2] in data['perms']['grant']:
            if perm == 'help':
                await ctx.send('You can ungrant following permissions:\n```\nall\ngrant\nring\nvolume\n```')
                return
            new = ctx.message.mentions[0].nick[:2]
            if perm=='all':
                for k in data['perms'].keys():
                    if new in data['perms'][k]:
                        data['perms'][k].remove(new)
            else:
                if new in data['perms'][perm]:
                    data['perms'][perm].remove(new)
            with open('perms.json', 'w') as f:
                f.write(json.dumps(data))
            await ctx.send(f'Permission **{perm}** taken away from user **{new}**')
        else:
            await ctx.send('You don\'t have permissions to invoke this command')

    @commands.command(brief='Check permissions')
    async def perms(self, ctx):
        nick = ctx.author.nick[:2]
        mess = 'Your permissions:\n```\n'
        for k in data['perms'].keys():
            if nick in data['perms'][k]:
                mess = mess + f'{k}\n'
        mess += '\n```'
        if mess == 'Your permissions:\n```\n\n```':
            mess = 'Your permissions:\n```\nNone\n```'
        await ctx.send(mess)

    @commands.command(brief='volume <percent> - changes volume')
    async def volume(self, ctx, vol : int):
        nick = ctx.author.nick[:2]
        if nick in data['perms']['volume']:
            self.volume = vol / 100
            data['vol'] = vol
            with open('perms.json', 'w') as f:
                f.write(json.dumps(data))
            await ctx.send(f'Volume changed to {vol}%')
        else:
            await ctx.send('You don\'t have permissions to invoke this command')

    @commands.command(brief='trans [pl/en/es/ru] "text"')
    async def trans(self, ctx, lang: str, phrase: str):
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
        try:
            print(' '.join(args))
            trnsd = trns(' '.join(args), dest='ru')
            mess = trnsd.text + '\nPronunciation: '+trnsd.pronunciation
            await ctx.send(f'Translated text:\n```\n{mess}\n```')
        except Exception as e:
            print(e)
            await ctx.send('This command is temporary unavaliable, because of Google API error')

bot = commands.Bot(command_prefix="//", description='End of lesson is here')

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

bot.add_cog(Music(bot))
bot.run(token1, reconnect=True)
