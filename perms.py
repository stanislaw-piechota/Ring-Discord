import asyncio
import discord
from discord.ext import commands
import json

class Perms(commands.Cog):
    def __init__(self, bot, data, dt):
        self.bot, self.data, self.dt = bot, data, dt

    def saveData(self):
        with open('perms.json', 'w') as file:
            file.write(json.dumps(self.data, indent=2))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f'{self.dt()} Bot joined new guild {guild.name} {guild.id}')
        if guild.me.guild_permissions.administrator:
            channel = await guild.create_text_channel('Ring-setup', overwrites={guild.default_role: discord.PermissionOverwrite(read_messages=False)})
            if guild.name in self.data.keys():
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
                        self.data[guild.name] = dcp

                        self.saveData()

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

    @commands.command(brief='grant [perm / help] [@ping ...] - grants permission')
    async def grant(self, ctx, perm : str):
        serv = ctx.guild.name
        print(f'{self.dt()} GRANT {serv} {ctx.author}')
        if ctx.author.nick[:2] in self.data[serv]['perms']['grant']['ba']:
            if perm == 'help':
                await ctx.send('You can grant following permissions:\n```\nall\ngrant\nring\nvolume```')
                return
            try:
                new = ctx.message.mentions[0].nick[:2]
            except:
                await ctx.send('You have to mention user')
                return
            if perm=='all':
                for k in self.data[serv]['perms'].keys():
                    if new not in self.data[serv]['perms'][k]['ba']:
                        self.data[serv]['perms'][k]['ba'].append(new)
            else:
                if new not in self.data[serv]['perms'][perm]['ba']:
                    self.data[serv]['perms'][perm]['ba'].append(new)
            self.saveData()
            text = '**__CHANGING PERMISSIONS__**\n' \
                   f'Permission **{perm}** granted for user **{new}**\n\n' \
                   f':white_check_mark: Done by: {ctx.author}'
            embed = discord.Embed(description=text, color=0xfffffe)
            embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
            await ctx.send(embed=embed)
        elif ctx.author.nick[:2] in self.data[serv]['perms']['grant']['bv']:
            if perm == 'help':
                await ctx.send('You can ungrant following permissions:\n```\ngrant\nring\nvolume\n```')
                return
            new = ctx.message.mentions[0].nick[:2]
            if not new in self.data[serv]['perms'][perm]['bv']:
                self.data[serv]['perms'][perm]['bv'].append(new)
            self.saveData()
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
                   ':arrows_counterclockwise: Waiting for approve ({}/{})'
            embed = discord.Embed(description=text.format(len(apprs), self.data[serv]['votes']), color=0xfffffe)
            embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
            message = await ctx.send(embed=embed)
            await message.add_reaction('✅')

            def check(reaction, user):
                return str(reaction.emoji)=='✅' and reaction.message==message and user!=ctx.guild.me

            while not (not len(apprs)<self.data[serv]['votes'] and admin_appr):
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                except asyncio.TimeoutError:
                    embed = discord.Embed(description=':alarm_clock: **Time to grant passed**')
                    await message.edit(embed=embed)
                    await message.remove_reaction('✅', ctx.guild.me)
                    return

                apprs = await reaction.users().flatten()
                try:
                    apprs.remove(ctx.guild.me)
                except Exception as e:
                    print(e)

                if user.nick[:2] in self.data[serv]['perms']['grant']['ba']:
                    admin_appr = True
                    admin_name = user
                    admin_state = ':white_check_mark:'

                text = '**__CHANGING PERMISSIONS__**\n' \
                       f'Granting permission **{perm}** for user **{new}**\n\n' \
                       f'{admin_state} Admin: {admin_name}\n' \
                       ':arrows_counterclockwise: Waiting for approve ({}/{})'
                embed = discord.Embed(description=text.format(len(apprs), self.data[serv]['votes']), color=0xfffffe)
                embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
                await message.edit(embed=embed)

            text = '**__CHANGING PERMISSIONS__**\n' \
                   f'Permission **{perm}** granted for user **{new}**\n\n' \
                   f':white_check_mark: Approved by: {admin_name}\n' \
                   ':white_check_mark: Granted in voting (10)'
            embed = discord.Embed(description=text, color=0xfffffe)
            embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
            if new not in self.data[serv]['perms'][perm]['bv']:
                self.data[serv]['perms'][perm]['bv'].append(new)
            self.saveData()
            await message.edit(embed=embed)

    @commands.command(brief='ungrant [perm / help] [@ping ...] - takes away permission')
    async def ungrant(self, ctx, perm : str):
        serv = ctx.guild.name
        print(f'{self.dt()} UNGRANT {serv} {ctx.author}')
        if ctx.author.nick[:2] in self.data[serv]['perms']['grant']['ba']:
            if perm == 'help':
                await ctx.send('You can ungrant following permissions:\n```\nall\ngrant\nring\nvolume\n```')
                return
            new = ctx.message.mentions[0].nick[:2]
            if perm=='all':
                for k in self.data[serv]['perms'].keys():
                    if new in self.data[serv]['perms'][k]['ba']:
                        self.data[serv]['perms'][k]['ba'].remove(new)
                    if new in self.data[serv]['perms'][k]['bv']:
                        self.data[serv]['perms'][k]['bv'].remove(new)
            else:
                if new in self.data[serv]['perms'][perm]['ba']:
                    self.data[serv]['perms'][perm]['ba'].remove(new)
                if new in self.data[serv]['perms'][perm]['bv']:
                    self.data[serv]['perms'][perm]['bv'].remove(new)
            self.saveData()
            text = '**__CHANGING PERMISSIONS__**\n' \
                   f'Permission **{perm}** taken away from user **{new}**\n\n' \
                   f':white_check_mark: Done by: {ctx.author}'
            embed = discord.Embed(description=text, color=0xfffffe)
            embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
            await ctx.send(embed=embed)
        elif ctx.author.nick[:2] in self.data[serv]['perms']['grant']['bv']:
            if perm == 'help':
                await ctx.send('You can ungrant following permissions:\n```\ngrant\nring\nvolume\n```')
                return
            new = ctx.message.mentions[0].nick[:2]
            if new in self.data[serv]['perms'][perm]['ba']:
                text = '**__CHANGING PERMISSIONS__**\n' \
                       f'You cannot take away this permission from user **{new}**\n\n' \
                       'Only admin feature :shrug: :sunglasses:'
                embed = discord.Embed(description=text, color=0xfffffe)
                embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
                message = await ctx.send(embed=embed)
                return
            if new in self.data[serv]['perms'][perm]['bv']:
                self.data[serv]['perms'][perm]['bv'].remove(new)
            self.saveData()
            text = '**__CHANGING PERMISSIONS__**\n' \
                   f'Permission **{perm}** taken away from user **{new}**\n\n' \
                   f':white_check_mark: Done by: {ctx.author}'
            embed = discord.Embed(description=text, color=0xfffffe)
            embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
            await ctx.send(embed=embed)
        else:
            new = ctx.message.mentions[0].nick[:2]
            if new in self.data[serv]['perms'][perm]['ba']:
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
                   f'{admin_state} Admin: {admin_name}\n' \
                   ':arrows_counterclockwise: Waiting for approve ({}/10)'
            embed = discord.Embed(description=text.format(len(apprs)), color=0xfffffe)
            embed.set_thumbnail(url=ctx.message.mentions[0].avatar_url)
            message = await ctx.send(embed=embed)
            await message.add_reaction('✅')

            def check(reaction, user):
                return str(reaction.emoji)=='✅' and reaction.message==message and user!=ctx.guild.me

            while not (not len(apprs)<self.data[serv]['votes'] and admin_appr):
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                except asyncio.TimeoutError:
                    embed = discord.Embed(description=':alarm_clock: **Time to ungrant passed**')
                    await message.edit(embed=embed)
                    await message.remove_reaction('✅', ctx.guild.me)
                    return

                apprs = await reaction.users().flatten()
                try:
                    apprs.remove(ctx.guild.me)
                except Exception as e:
                    print(e)

                if user.nick[:2] in self.data[serv]['perms']['grant']['ba']:
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
            if new in self.data[serv]['perms'][perm]['bv']:
                self.data[serv]['perms'][perm]['bv'].remove(new)
            self.saveData()
            await message.edit(embed=embed)

    @commands.command(brief='Check permissions')
    async def perms(self, ctx):
        serv = ctx.guild.name
        print(f'{self.dt()} PERMS {serv} {ctx.author}')
        nick = ctx.author.nick[:2]
        mess = 'Your permissions:\n```\nBy admin:\n'
        admin = ''; voting = ''
        for k in self.data[serv]['perms'].keys():
            if nick in self.data[serv]['perms'][k]['ba']:
                admin = admin + f'{k}\n'
            if nick in self.data[serv]['perms'][k]['bv']:
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

    @commands.command()
    async def votes(self, ctx, votes: int):
        serv = ctx.guild.name
        print(f'{self.dt()} VOTES {serv} {ctx.author}')
        if ctx.author.nick[:2] in self.data[serv]['perms']['grant']['ba']:
            self.data[serv]['votes'] = votes
            self.saveData()
            await ctx.send(f'Votes limit changed to **{votes}**')
        elif ctx.author.nick[:2] in self.data[serv]['perms']['grant']['bv']:
            await ctx.send('You can not invoke this command. Only admin feature :shrug: :sunglasses:')
        else:
            await ctx.send('You do not have permission to invoke this command')
