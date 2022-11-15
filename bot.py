import json
import os
import platform
import random

import discord
from discord.ext import tasks, commands
from discord.ext.commands import Bot
from discord.ext.commands import Context
from dotenv import load_dotenv

from helpers import checks

load_dotenv()
PREFIX = os.getenv('PREFIX')
# APPID = os.getenv('APPID')
TOKEN = os.getenv('TOKEN')
OWNER = os.getenv('OWNER')

if len(PREFIX) > 3:
    with open('prefix.json','r',encoding='utf-8') as file:
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


@bot.command()
@checks.is_owner()
# @commands.check(flyhighhigh)
async def unload(ctx: Context, ext: str = None):
    """
    下線Cogs
    """
    if ext:
        try:
            await bot.unload_extension(f"cogs.{ext}")
            print(f"Unloaded extension '{ext}'")
        except Exception as e:
            exception = f"{type(e).__name__}: {e}"
            print(f"Failed to unload extension {extension}\n{exception}")
    else:
        for file in os.listdir(f"./cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await bot.unload_extension(f"cogs.{extension}")
                    print(f"Unloaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(
                        f"Failed to unload extension {extension}\n{exception}")


@bot.command()
@checks.is_owner()
# @commands.check(flyhighhigh)
async def load(ctx: Context, ext: str = None):
    """
    載入Cogs
    """
    if ext:
        try:
            await bot.load_extension(f"cogs.{ext}")
            print(f"Loaded extension '{ext}'")
        except Exception as e:
            exception = f"{type(e).__name__}: {e}"
            print(f"Failed to load extension {extension}\n{exception}")
    else:
        for file in os.listdir(f"./cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await bot.load_extension(f"cogs.{extension}")
                    print(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(f"Failed to load extension {extension}\n{exception}")


@bot.command()
@checks.is_owner()
# @commands.check(flyhighhigh)
async def reload(ctx: Context, ext: str = None):
    """
    重新載入Cogs
    """
    if ext:
        try:
            await bot.reload_extension(f"cogs.{ext}")
            print(f"Reloaded extension '{ext}'")
        except Exception as e:
            exception = f"{type(e).__name__}: {e}"
            print(f"Failed to reload extension {extension}\n{exception}")
    else:
        for file in os.listdir(f"./cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await bot.reload_extension(f"cogs.{extension}")
                    print(f"Reloaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(
                        f"Failed to reload extension {extension}\n{exception}")


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