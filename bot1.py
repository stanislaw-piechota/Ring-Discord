#https://discord.com/api/oauth2/authorize?client_id=773874155807834113&permissions=8&scope=bot

import asyncio
import discord
from time import sleep
import json
from secrets import token1, token2
from discord.ext import commands
from googletrans import Translator
import datetime

with open('perms.json') as f:
    data = json.loads(f.read())

trns = Translator().translate
dt = datetime.datetime.now

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f'{dt()} Bot joined new guild {guild.name} {guild.id}')
        if guild.me.guild_permissions.administrator:
            channel = await guild.create_text_channel('Ring-setup', overwrites={guild.default_role: discord.PermissionOverwrite(read_messages=False)})
            if guild.name in data.keys():
                await channel.send(':white_check_mark: Bot already configured for this server')
                return
            else:
                await channel.send('Hi. Well done. Bot is on the server. **Person with admin rights have to type in `activate` to activate bot**. You have 10 mins')
                def check(msg):
                    if isinstance(msg.author, discord.Member):
                        return (msg.author == guild.owner or msg.author.guild_permissions.administrator) and msg.author != guild.me and msg.channel == channel
                    return False
                while True:
                    try:
                        message = await self.bot.wait_for('message', timeout=600, check=check)
                    except asyncio.TimeoutError:
                        await guild.leave()
                        return

                    if message.content == 'activate':
                        dcp = {"perms":{"ring":{"ba":[message.author.nick[:2]],"bv":[]}, \
                        "volume":{"ba":[message.author.nick[:2]], "bv":[]}, \
                        "grant":{"ba":[message.author.nick[:2]], "bv":[]}}, "vol":100}
                        data[guild.name] = dcp

                        with open('perms.json', 'w') as file:
                            file.write(json.dumps(data, indent=2))

                        await channel.send(f':sunglasses: Congratulations. **Bot activated**. User {message.author.nick[:2]} have admin rights')
                        return

                    else:
                        await channel.send(':x: wrong message')

        else:
            print(f'Bot does not have admin rights {guild.name} ({guild.id})')
            try:
                await guild.text_channels[0].send(':x: **Bot needs admin rights. Add it once again, checking privileges**')
            except discord.Forbidden:
                pass
            await guild.leave()

    def _play(self, ctx, query):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

    @commands.command()
    async def ring(self, ctx):
        serv = ctx.guild.name
        print(f'{dt()} RING {serv} {ctx.author}')
        if ctx.author.nick[:2] in data[serv]['perms']['ring']['ba'] or ctx.author.nick[:2] in data[serv]['perms']['ring']['bv']:
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
            self.volume = data[serv]['vol']/100
            self._play(ctx, 'dzwonek.mp3')
            ctx.voice_client.source.volume = self.volume
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

    @commands.command(brief='grant [perm / help] [@ping ...] - grants permission')
    async def grant(self, ctx, perm : str):
        serv = ctx.guild.name
        print(f'{dt()} GRANT {serv} {ctx.author}')
        if ctx.author.nick[:2] in data[serv]['perms']['grant']['ba']:
            if perm == 'help':
                await ctx.send('You can grant following permissions:\n```\nall\ngrant\nring\nvolume```')
                return
            try:
                new = ctx.message.mentions[0].nick[:2]
            except:
                await ctx.send('You have to mention user')
                return
            if perm=='all':
                for k in data[serv]['perms'].keys():
                    if new not in data[serv]['perms'][k]['ba']:
                        data[serv]['perms'][k]['ba'].append(new)
            else:
                if new not in data[serv]['perms'][perm]['ba']:
                    data[serv]['perms'][perm]['ba'].append(new)
            with open('perms.json', 'w') as f:
                f.write(json.dumps(data, indent=2))
            text = '**__CHANGING PERMISSIONS__**\n' \
                   f'Permission **{perm}** granted for user **{new}**\n\n' \
                   f':white_check_mark: Done by: {ctx.author}'
            embed = discord.Embed(description=text, color=0xfffffe)
            embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
            await ctx.send(embed=embed)
        elif ctx.author.nick[:2] in data[serv]['perms']['grant']['bv']:
            if perm == 'help':
                await ctx.send('You can ungrant following permissions:\n```\ngrant\nring\nvolume\n```')
                return
            new = ctx.message.mentions[0].nick[:2]
            if not new in data[serv]['perms'][perm]['bv']:
                data[serv]['perms'][perm]['bv'].append(new)
            with open('perms.json', 'w') as f:
                f.write(json.dumps(data, indent=2))
            text = '**__CHANGING PERMISSIONS__**\n' \
                   f'Permission **{perm}** granted for user **{new}**\n\n' \
                   f':white_check_mark: Done by: {ctx.author}'
            embed = discord.Embed(description=text, color=0xfffffe)
            embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
            await ctx.send(embed=embed)
        else:
            new = ctx.message.mentions[0].nick[:2]; apprs = []
            admin_appr = False; admin_name = 'waiting for approve'; admin_state = ':arrows_counterclockwise:'
            text = '**__CHANGING PERMISSIONS__**\n' \
                   f'Granting permission **{perm}** for user **{new}**\n\n' \
                   f'{admin_state} Admin: {admin_name}\n' \
                   ':arrows_counterclockwise: Waiting for approve ({}/10)'
            embed = discord.Embed(description=text.format(len(apprs)), color=0xfffffe)
            embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
            message = await ctx.send(embed=embed)
            await message.add_reaction('✅')

            def check(reaction, user):
                return str(reaction.emoji)=='✅' and reaction.message==message and user!=ctx.guild.me

            while not (not len(apprs)<10 and admin_appr):
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                except asyncio.TimeoutError:
                    embed = discord.Embed(description=':alarm_clock: **Time to grant passed**')
                    await message.edit(embed=embed)
                    await message.remove_reaction('✅', ctx.guild.me)
                    return

                apprs = await reaction.users().flatten()
                apprs.remove(ctx.guild.me)

                if user.nick[:2] in data[serv]['perms']['grant']['ba']:
                    admin_appr = True
                    admin_name = user
                    admin_state = ':white_check_mark:'

                text = '**__CHANGING PERMISSIONS__**\n' \
                       f'Granting permission **{perm}** for user **{new}**\n\n' \
                       f':{admin_state} Admin: {admin_name}\n' \
                       ':arrows_counterclockwise: Waiting for approve ({}/10)'
                embed = discord.Embed(description=text.format(len(apprs)), color=0xfffffe)
                embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
                await message.edit(embed=embed)

            text = '**__CHANGING PERMISSIONS__**\n' \
                   f'Permission **{perm}** granted for user **{new}**\n\n' \
                   f':white_check_mark: Approved by: {admin_name}\n' \
                   ':white_check_mark: Granted in voting (10)'
            embed = discord.Embed(description=text, color=0xfffffe)
            embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
            if new not in data[serv]['perms'][perm]['bv']:
                data[serv]['perms'][perm]['bv'].append(new)
            with open('perms.json', 'w') as f:
                f.write(json.dumps(data, indent=2))
            await message.edit(embed=embed)

    @commands.command(brief='ungrant [perm / help] [@ping ...] - takes away permission')
    async def ungrant(self, ctx, perm : str):
        serv = ctx.guild.name
        print(f'{dt()} UNGRANT {serv} {ctx.author}')
        if ctx.author.nick[:2] in data[serv]['perms']['grant']['ba']:
            if perm == 'help':
                await ctx.send('You can ungrant following permissions:\n```\nall\ngrant\nring\nvolume\n```')
                return
            new = ctx.message.mentions[0].nick[:2]
            if perm=='all':
                for k in data[serv]['perms'].keys():
                    if new in data[serv]['perms'][k]['ba']:
                        data[serv]['perms'][k]['ba'].remove(new)
                    if new in data[serv]['perms'][k]['bv']:
                        data[serv]['perms'][k]['bv'].remove(new)
            else:
                if new in data[serv]['perms'][perm]['ba']:
                    data[serv]['perms'][perm]['ba'].remove(new)
                if new in data[serv]['perms'][perm]['bv']:
                    data[serv]['perms'][perm]['bv'].remove(new)
            with open('perms.json', 'w') as f:
                f.write(json.dumps(data, indent=2))
            text = '**__CHANGING PERMISSIONS__**\n' \
                   f'Permission **{perm}** taken away from user **{new}**\n\n' \
                   f':white_check_mark: Done by: {ctx.author}'
            embed = discord.Embed(description=text, color=0xfffffe)
            embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
            await ctx.send(embed=embed)
        elif ctx.author.nick[:2] in data[serv]['perms']['grant']['bv']:
            if perm == 'help':
                await ctx.send('You can ungrant following permissions:\n```\ngrant\nring\nvolume\n```')
                return
            new = ctx.message.mentions[0].nick[:2]
            if new in data[serv]['perms'][perm]['ba']:
                text = '**__CHANGING PERMISSIONS__**\n' \
                       f'You cannot take away this permission from user **{new}**\n\n' \
                       'Only admin feature :shrug: :sunglasses:'
                embed = discord.Embed(description=text, color=0xfffffe)
                embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
                message = await ctx.send(embed=embed)
                return
            if new in data[serv]['perms'][perm]['bv']:
                data[serv]['perms'][perm]['bv'].remove(new)
            with open('perms.json', 'w') as f:
                f.write(json.dumps(data, indent=2))
            text = '**__CHANGING PERMISSIONS__**\n' \
                   f'Permission **{perm}** taken away from user **{new}**\n\n' \
                   f':white_check_mark: Done by: {ctx.author}'
            embed = discord.Embed(description=text, color=0xfffffe)
            embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
            await ctx.send(embed=embed)
        else:
            new = ctx.message.mentions[0].nick[:2]
            if new in data[serv]['perms'][perm]['ba']:
                text = '**__CHANGING PERMISSIONS__**\n' \
                       f'You cannot take away this permission from user **{new}**\n\n' \
                       'Only admin feature :shrug: :sunglasses:'
                embed = discord.Embed(description=text, color=0xfffffe)
                embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
                message = await ctx.send(embed=embed)
                return
            apprs = []; admin_appr = False; admin_name = 'waiting for approve'; admin_state = ':arrows_counterclockwise:'
            text = '**__CHANGING PERMISSIONS__**\n' \
                   f'Taking away permission **{perm}** from user **{new}**\n\n' \
                   f':{admin_state} Admin: {admin_name}\n' \
                   ':arrows_counterclockwise: Waiting for approve ({}/10)'
            embed = discord.Embed(description=text.format(len(apprs)), color=0xfffffe)
            embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
            message = await ctx.send(embed=embed)
            await message.add_reaction('✅')

            def check(reaction, user):
                return str(reaction.emoji)=='✅' and reaction.message==message and user!=ctx.guild.me

            while not (not len(apprs)<10 and admin_appr):
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                except asyncio.TimeoutError:
                    embed = discord.Embed(description=':alarm_clock: **Time to ungrant passed**')
                    await message.edit(embed=embed)
                    await message.remove_reaction('✅', ctx.guild.me)
                    return

                apprs = await reaction.users().flatten()
                apprs.remove(ctx.guild.me)

                if user.nick[:2] in data[serv]['perms']['grant']['ba']:
                    admin_appr = True
                    admin_name = user
                    admin_state = ':white_check_mark:'

                text = '**__CHANGING PERMISSIONS__**\n' \
                       f'Taking away permission **{perm}** from user **{new}**\n\n' \
                       f'{admin_state} Admin: {admin_name}\n' \
                       ':arrows_counterclockwise: Waiting for approve ({}/10)'
                embed = discord.Embed(description=text.format(len(apprs)), color=0xfffffe)
                embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
                await message.edit(embed=embed)

            text = '**__CHANGING PERMISSIONS__**\n' \
                   f'Permission **{perm}** taken away from user **{new}**\n\n' \
                   f':white_check_mark: Approved by: {admin_name}\n' \
                   ':white_check_mark: Ungranted in voting (10)'
            embed = discord.Embed(description=text, color=0xfffffe)
            embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
            if new in data[serv]['perms'][perm]['bv']:
                data[serv]['perms'][perm]['bv'].remove(new)
            with open('perms.json', 'w') as f:
                f.write(json.dumps(data, indent=2))
            await message.edit(embed=embed)

    @commands.command(brief='Check permissions')
    async def perms(self, ctx):
        serv = ctx.guild.name
        print(f'{dt()} PERMS {serv} {ctx.author}')
        nick = ctx.author.nick[:2]
        mess = 'Your permissions:\n```\nBy admin:\n'
        admin = ''; voting = ''
        for k in data[serv]['perms'].keys():
            if nick in data[serv]['perms'][k]['ba']:
                admin = admin + f'{k}\n'
            if nick in data[serv]['perms'][k]['bv']:
                voting = voting + f'{k}\n'
        if admin:
            mess += admin
        else:
            mess += 'None\n'
        mess += '\nBy voting or by privileged user:\n'
        if voting:
            mess += voting
        else:
            mess += 'None\n'
        mess += '\n```'
        await ctx.send(mess)

    @commands.command(brief='volume <percent> - changes volume')
    async def volume(self, ctx, vol : int):
        serv = ctx.guild.name
        print(f'{dt()} VOLUME {serv} {ctx.author}')
        nick = ctx.author.nick[:2]
        if nick in data[serv]['perms']['volume']['ba'] or nick in data[serv]['perms']['volume']['bv']:
            data[serv]['vol'] = vol
            with open('perms.json', 'w') as f:
                f.write(json.dumps(data, indent=2))
            await ctx.send(f'Volume changed to {vol}%')
        else:
            await ctx.send('You don\'t have permissions to invoke this command')

    @commands.command(brief='trans [pl/en/es/ru] "text"')
    async def trans(self, ctx, lang: str, phrase: str):
        serv = ctx.guild.name
        print(f'{dt()} TRANS {serv} {ctx.author}')
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
        print(f'{dt()} RU {serv} {ctx.author}')
        try:
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
