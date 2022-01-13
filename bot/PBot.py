import discord
from discord.ext import commands
import os
import sqlite3
import string
import json

bot = commands.Bot(command_prefix='$$', intents=discord.Intents.all())


@bot.event  # Проверка запуска
async def on_ready():
    print('PBot ready now!')

    global base, cur
    base = sqlite3.connect('PBot.db')
    cur = base.cursor()
    if base:
        print('Database connected')


@bot.event  # Приветствие
async def on_member_join(member):
    await member.send('Hello! Type $$info on server channel to open command list')

    for ch in bot.get_guild(member.guild.id).channels:
        if ch.name == 'основной':
            await bot.get_channel(ch.id).send(f'{member} welcome!')


@bot.event  # Прощание
async def on_member_remove(member):
    for ch in bot.get_guild(member.guild.id).channels:
        if ch.name == 'основной':
            await bot.get_channel(ch.id).send(f'{member}, goodbye. Hope to see you soon!')


@bot.command()  # Статус работоспособности бота
async def test(ctx):
    await ctx.send('Bot already online!')


@bot.command()  # Вызов справки
async def info(ctx, arg=None):
    author = ctx.message.author
    if arg == None:
        await ctx.send(
            f'{author.mention} \n $$info - list of avalbale commands \n $$test - check if bot currently online\n $$status - check count of warnings')
    else:
        await ctx.send(f'{author.mention} this is not actual command, type $$info for command list')


@bot.command()  # Проверка кол-ва предупреждений
async def status(ctx):
    base.execute('CREATE TABLE IF NOT EXISTS {}(userid INT, count INT)'.format(ctx.message.guild.name))
    base.commit()
    warning = cur.execute('SELECT * FROM {} WHERE userid == ?'.format(ctx.message.guild.name),(ctx.message.author.id,)).fetchone()
    if warning == None:
        await ctx.send(f'{ctx.message.author.mention}, zero warnings, good job!')
    else:
        await ctx.send(f'{ctx.message.author.mention}, You have {warning[1]} warnings')


@bot.event  # Модерация чата
async def on_message(message):
    if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.content.split(' ')}.intersection(set(json.load(open('cenz.json')))) != set():
        await message.channel.send(f'{message.author.mention}, obscene language detected')
        await message.delete()

        name = message.guild.name

        base.execute('CREATE TABLE IF NOT EXISTS {}(userid INT, count, INT)'.format(name))
        base.commit()

        warning = cur.execute('SELECT * FROM {} WHERE userid == ?'.format(name),(message.author.id,)).fetchone()

        if warning == None:
            cur.execute('INSERT INTO {} VALUES (?, ?)'.format(name),(message.author.id,1))
            base.commit()
            await message.channel.send(f'{message.author.mention}, first warning! Third warning = BAN!')

        elif warning[1] == 1:
            cur.execute('UPDATE {} SET count == ? WHERE userid == ?'.format(name),(2,message.author.id))
            base.commit()
            await message.channel.send(f'{message.author.mention}, Second warning!')

        elif warning[1] == 2:
            cur.execute('UPDATE {} SET count == ? WHERE userid == ?'.format(name), (3, message.author.id))
            base.commit()
            await message.channel.send(f'{message.author.mention}, Banned for obscene language')
            await message.author.ban(reason='obscene language')

    await bot.process_commands(message)


bot.run(os.getenv('TOKEN'))
