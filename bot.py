import json
import os
import platform
import random
import subprocess
import sys
from time import sleep

import discord
from discord.ext import tasks, commands
from discord.ext.commands import Bot
from discord.ext.commands import Context
from dotenv import load_dotenv
import git
import datetime

from helpers import checks

load_dotenv()
PREFIX = os.getenv('PREFIX')
# APPID = os.getenv('APPID')
TOKEN = os.getenv('TOKEN')
OWNER = os.getenv('OWNER')

if len(PREFIX) > 3:
    with open('config.json','r',encoding='utf-8') as file:
        PREFIX = json.load(file)['prefix']

class MyBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix=PREFIX,
                         intents=intents,
                         description='這件事是我們兩個之間的秘密，你最好不要給我告訴任何人，\n\
        如果你要說出去，就給我小心一點，我知道你學校在哪裡，也知道你讀哪一班，\n\
        你最好給我好好記住，懂嗎？')

    async def on_ready(self) -> None:
        """
        The code in this even is executed when the bot is ready
        """
        print(f"Logged in as {bot.user.name}")
        print(f"discord API version: {discord.__version__}")
        print(f"Python version: {platform.python_version()}")
        print(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        print("-------------------")
        status_task.start()
        await from_restart()

    async def setup_hook(self) -> None:
        for file in os.listdir(f"./cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await bot.load_extension(f"cogs.{extension}")
                    print(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(f"Failed to load extension {extension}\n{exception}")
        print(PREFIX,TOKEN)
        await bot.tree.sync()


    async def on_command_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title='',
                                  description='**輸入參數錯誤或不足，我看你完全是不懂哦**',
                                  color=0xf93a2f)
            await ctx.send(embed=embed)
            #await ctx.send('***輸入參數錯誤或不足，我看你完全是不懂哦***')
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(title='',
                                  description='**無效指令，我看你是完全不懂哦**',
                                  color=0xf93a2f)
            await ctx.send(embed=embed)
            #await ctx.send('***無效指令，我看你是完全不懂哦***')


intents = discord.Intents.all()
intents.message_content = True
bot = MyBot()

async def from_restart():
    print('')
    print('--- parsing start arguments ---')
    try:
        with open("temp.json", "r+",encoding='utf-8') as file:
            data = json.load(file)
            channel_id = int(data["channel_id"])
            message_id = int(data["message_id"])
            data["channel_id"] = ''
            data["message_id"] = ''
            file.seek(0)  # rewind
            json.dump(data, file,indent=4)
            file.truncate()
        
        channel = await bot.fetch_channel(channel_id)
        msg = await channel.fetch_message(message_id)
        cont = msg.content + '\nPull and restart finished. Hello World!'
        print('--- restart finished! ---')
        await msg.edit(content=cont)
    except:
        print('--- no arguments ---')

# def flyhighhigh(ctx: commands.Context):
#     if ctx.author.id == 617692516871045121:
#         return True
#     else:
#         embed = discord.Embed(title='', description='**權限不足**', color=0xf93a2f)
#         bot.loop.create_task(ctx.send(embed=embed))
#         return False


@tasks.loop(seconds=10.0)
async def status_task() -> None:
    """
    Setup the game status task of the bot
    """
    statuses = ["阿偉", "淑惠阿姨", "阿嬤", "彬彬"]
    act = discord.Activity(name=random.choice(statuses),
                           type=discord.ActivityType.playing)
    await bot.change_presence(activity=act)

@tasks.loop(seconds=60.0)
async def birthday_task() -> None:
    """
    Setup the OWU birthday task of the bot
    """
    try:
        channel = await bot.fetch_channel(698431872673251330) # 鬥陣大學 聊天系
        date = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        # if date.month == 4 and date.day == 11 and date.hour == 0 and date.minute <= 10:
        if date.month == 3 and date.day == 9 and date.hour == 3 and 29 <= date.minute < 30:
            year = date.year - 2020
            embed = discord.Embed(title='',
                                  description=f'**恭喜 鬥陣大學 邁入{year}週年！！**',
                                  color=0xf93a2f)
            await channel.send(embed=embed)
    except Exception as e:
        with open("log.txt", "r+",encoding='utf-8') as file:
            file.write(str(e))


@bot.command()
@checks.is_owner()
async def pull(ctx: Context, ext: str = None):
    """
    自動從github拉，然後reload
    """
    result = ''
    print('')
    print('--- pulling ---')
    try:
        g = git.cmd.Git()
        result:str = g.pull() + '\n'
    except Exception as e:
        result = str(e) + '\n'
    print(result)
    
    print('--- reloading ---')
    if result.startswith("Already up to date."):
        pass
    elif ext:
        try:
            await bot.reload_extension(f"cogs.{ext}")
            print(f"Reloaded extension '{ext}'")
            result += f"Reloaded extension '{ext}'" + '\n'
        except Exception as e:
            exception = f"{type(e).__name__}: {e}"
            print(f"Failed to reload extension {extension}\n{exception}")
            result += f"Failed to reload extension {extension}\n{exception}" + '\n'
    else:
        for file in os.listdir(f"./cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await bot.reload_extension(f"cogs.{extension}")
                    print(f"Reloaded extension '{extension}'")
                    result += f"Reloaded extension '{extension}'" + '\n'
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(f"Failed to reload extension {extension}\n{exception}")
                    result += f"Failed to reload extension {extension}\n{exception}" + '\n'

    print('--- pull and reload finished ---')
    print('')
    await ctx.send(result)

@bot.command()
@checks.is_owner()
async def restart(ctx: Context, ext: str = None):
    """
    自動從github pull，然後重啟
    """
    result = ''
    print('')
    print('--- pulling ---')
    try:
        g = git.cmd.Git()
        result:str = g.pull()
    except Exception as e:
        result = str(e)
    print(result)
    print('--- pull and finished ---')
    print('')

    sended = await ctx.send(result + '\nrestarting bot...')
    channel_id = str(ctx.channel.id)
    message_id = str(sended.id)

    with open("temp.json", "w",encoding='utf-8') as file:
        # data = json.load(file)
        data = {}
        data["channel_id"] = channel_id
        data["message_id"] = message_id
        # file.seek(0)  # rewind
        json.dump(data, file,indent=4)
        # file.truncate()
    
    os.execv(sys.executable, ['python'] + sys.argv)
    

@bot.command()
@checks.is_owner()
# @commands.check(flyhighhigh)
async def unload(ctx: Context, ext: str = None):
    """
    下線Cogs
    """
    result = ''
    if ext:
        try:
            await bot.unload_extension(f"cogs.{ext}")
            print(f"Unloaded extension '{ext}'")
            result += f"Unloaded extension '{ext}'" + '\n'
        except Exception as e:
            exception = f"{type(e).__name__}: {e}"
            print(f"Failed to unload extension {extension}\n{exception}")
            result += f"Failed to unload extension {extension}\n{exception}" + '\n'
    else:
        for file in os.listdir(f"./cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await bot.unload_extension(f"cogs.{extension}")
                    print(f"Unloaded extension '{extension}'")
                    result += f"Unloaded extension '{extension}'" + '\n'
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(f"Failed to unload extension {extension}\n{exception}")
                    result += f"Failed to unload extension {extension}\n{exception}" + '\n'
    await ctx.send(result)

@bot.command()
@checks.is_owner()
# @commands.check(flyhighhigh)
async def load(ctx: Context, ext: str = None):
    """
    載入Cogs
    """
    result = ''
    if ext:
        try:
            await bot.load_extension(f"cogs.{ext}")
            print(f"Loaded extension '{ext}'")
            result += f"Loaded extension '{ext}'" + '\n'
        except Exception as e:
            exception = f"{type(e).__name__}: {e}"
            print(f"Failed to load extension {extension}\n{exception}")
            result += f"Failed to load extension {extension}\n{exception}" + '\n'
    else:
        for file in os.listdir(f"./cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await bot.load_extension(f"cogs.{extension}")
                    print(f"Loaded extension '{extension}'")
                    result += f"Loaded extension '{extension}'" + '\n'
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(f"Failed to load extension {extension}\n{exception}")
                    result += f"Failed to load extension {extension}\n{exception}" + '\n'
    await ctx.send(result)

@bot.command()
@checks.is_owner()
# @commands.check(flyhighhigh)
async def reload(ctx: Context, ext: str = None):
    """
    重新載入Cogs
    """
    result = ''
    if ext:
        try:
            await bot.reload_extension(f"cogs.{ext}")
            print(f"Reloaded extension '{ext}'")
            result += f"Reloaded extension '{ext}'" + '\n'
        except Exception as e:
            exception = f"{type(e).__name__}: {e}"
            print(f"Failed to reload extension {extension}\n{exception}")
            result += f"Failed to reload extension {extension}\n{exception}" + '\n'
    else:
        for file in os.listdir(f"./cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await bot.reload_extension(f"cogs.{extension}")
                    print(f"Reloaded extension '{extension}'")
                    result += f"Reloaded extension '{extension}'" + '\n'
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(f"Failed to reload extension {extension}\n{exception}")
                    result += f"Failed to reload extension {extension}\n{exception}" + '\n'
    await ctx.send(result)

@bot.command()
@checks.is_owner()
# @commands.check(flyhighhigh)
async def sync(ctx: Context, spec: str = None):
    """
    將Command同步，使slash command正常顯示
    """
    if spec == '~':
        await ctx.bot.tree.sync(guild=discord.Object(id=ctx.guild.id))
        embed = discord.Embed(description="synced to current guild",
                              color=discord.Color.green())
        await ctx.send(embed=embed)
    else:
        await ctx.bot.tree.sync()
        embed = discord.Embed(description="synced globally",
                              color=discord.Color.green())
        await ctx.send(embed=embed)


@bot.command()
@checks.is_owner()
# @commands.check(flyhighhigh)
async def shutdown(ctx: Context):
    """
    關機的啦
    """
    embed = discord.Embed(description="再會啦 心愛的人! :wave:", color=0x9C84EF)
    await ctx.send(embed=embed)
    await bot.close()


# Run the bot with the token
bot.run(TOKEN)