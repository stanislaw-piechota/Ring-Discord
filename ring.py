import asyncio
import discord
import json
from discord.ext import commands
from random import choice

class Ring(commands.Cog):
    def __init__(self, bot, data, dt):
        self.bot = bot; self.data = data
        self.dt = dt

    def _play(self, ctx, query):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

    async def log(self, message):
        await self.bot.get_channel(780912356573184020).send(message)

    @commands.command()
    async def ring(self, ctx):
        serv = str(ctx.guild.id)
        await self.log(f'{self.dt()} RING {ctx.guild.name} {ctx.author}')
        if ctx.author.id in self.data[serv]['perms']['ring']['ba'] or ctx.author.id in self.data[serv]['perms']['ring']['bv']:
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
            self._play(ctx, 'additional/dzwonek.mp3')
            ctx.voice_client.source.volume = self.data[serv]['vol']/100
            await asyncio.sleep(2)
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

    @commands.command(brief='volume <percent> - changes volume')
    async def volume(self, ctx, vol : int):
        serv = str(ctx.guild.id)
        await self.log(f'{self.dt()} VOLUME {ctx.guild.name} {ctx.author}')
        nick = ctx.author.id
        if nick in self.data[serv]['perms']['volume']['ba'] or nick in self.data[serv]['perms']['volume']['bv']:
            self.data[serv]['vol'] = vol
            with open('perms.json', 'w') as f:
                f.write(json.dumps(self.data, indent=2))
            await ctx.send(f'Volume changed to {vol}%')
        else:
            await ctx.send('You don\'t have permissions to invoke this command')

    @commands.command(brief='rm <"message"> <seconds> <starting_letter>')
    async def rm(self, ctx, mess:str, secs: int, start: str, ):
        serv = str(ctx.guild.id)
        await self.log(f'{self.dt()} RM {ctx.guild.name} {ctx.author.name}')
        channels = ctx.guild.channels
        for channel in channels.copy():
            if type(channel) != discord.TextChannel:
                channels.remove(channel)

        def check(msg):
                    return (msg.content.isdigit() or msg.content=='quit') and msg.author.name == ctx.author.name

        if mess == "random":
            if self.data[serv]["phrases"]:
                mess = choice(self.data[serv]["phrases"])
            else:
                await ctx.send("There are **no custom phrases** to choose on this server")
                return
        elif mess == "custom":
            custom = 'Following phrases found:\n```\n'
            if not self.data[serv]['phrases']:
                await ctx.send("There are **no custom phrases** to choose on this server")
                return
            for i, phr in enumerate(self.data[serv]["phrases"]):
                custom += f'{i+1}: "{phr}"\n'
            custom += '```\nType in number of phrase you want to send'
            main = await ctx.send(custom)
            try:
                msg = await self.bot.wait_for('message', timeout=30, check=check)
            except asyncio.TimeoutError:
                await main.edit(':alarm_clock: **Time to choose passed**')
                return
            mess = self.data[serv]['phrases'][int(msg.content)-1]

        if mess not in self.data[serv]["phrases"]:
            self.data[serv]["phrases"].append(mess)
            with open('perms.json', 'w') as file:
                file.write(json.dumps(self.data, indent=2))
        
        if not len(channels):
            await ctx.send(f'There are no text channels')
        else:
            for channel in channels.copy():
                if not channel.name.startswith(start):
                    channels.remove(channel)
            if not len(channels):
                await ctx.send(f'There is no channel that starts with **{start}**')
            elif len(channels) == 1:
                await asyncio.sleep(secs)
                await channels[0].send(mess)
            else:
                possible = 'Possible channels are:\n```\n'
                for i, c in enumerate(channels):
                    possible += f'{i+1}: {c.name}\n'
                possible += '```\nType in number of channel you want to choose'
                main = await ctx.send(possible)

                try:
                    msg = await self.bot.wait_for('message', timeout=30, check=check)
                except asyncio.TimeoutError:
                    await main.edit(':alarm_clock: **Time to choose passed**')
                    return

                await asyncio.sleep(secs)
                await channels[int(msg.content)-1].send(mess)

    @commands.command()
    async def phrase(self, ctx, opt: str, phrase = None):
        serv = str(ctx.guild.id)
        if opt == 'add':
            self.data[serv]['phrases'].append(phrase)
            with open('perms.json', 'w') as file:
                file.write(json.dumps(self.data, indent=2))
            await ctx.send(f'Phrase **{phrase}** added to catalogue')
        elif opt == 'show':
            msg = 'Saved phrases:\n```\n'
            for i, e in enumerate(self.data[serv]['phrases']):
                msg += f'{i+1}: {e}\n'
            msg += '```'
            await ctx.send(msg)
        elif opt == 'remove':
            try:
                self.data[serv]['phrases'].pop(int(phrase)-1)
                with open('perms.json', 'w') as file:
                   file.write(json.dumps(self.data, indent=2))
                await ctx.send(f'Phrase with index {int(phrase)} removed')
            except Exception as e:
                print(e)
                await ctx.send(f'Phrase with index {int(phrase)} does not exist')