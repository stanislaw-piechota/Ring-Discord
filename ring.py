import asyncio
import discord
import json
from discord.ext import commands

class Ring(commands.Cog):
    def __init__(self, bot, data, dt):
        self.bot = bot; self.data = data
        self.dt = dt

    def _play(self, ctx, query):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

    @commands.command()
    async def ring(self, ctx):
        serv = ctx.guild.name
        print(f'{self.dt()} RING {serv} {ctx.author}')
        if ctx.author.nick[:2] in self.data[serv]['perms']['ring']['ba'] or ctx.author.nick[:2] in self.data[serv]['perms']['ring']['bv']:
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
        serv = ctx.guild.name
        print(f'{self.dt()} VOLUME {serv} {ctx.author}')
        nick = ctx.author.nick[:2]
        if nick in self.data[serv]['perms']['volume']['ba'] or nick in self.data[serv]['perms']['volume']['bv']:
            self.data[serv]['vol'] = vol
            with open('perms.json', 'w') as f:
                f.write(json.dumps(self.data, indent=2))
            await ctx.send(f'Volume changed to {vol}%')
        else:
            await ctx.send('You don\'t have permissions to invoke this command')
