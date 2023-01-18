import discord
from discord import ButtonStyle, Embed
from discord.ui import Select,View,Button
from discord.ext import commands
import random
import typing
import json
from helpers import checks
from datetime import datetime,timedelta,timezone,date
import pip
import pkg_resources


class Pipp(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot    
    
    @commands.hybrid_command(name='pip',description="安裝或查看遠端pip module")
    @checks.is_owner()
    async def pip(self,ctx:commands.Context,mod:str=''):
        """安裝或查看遠端pip module"""
        
        def install(package):
            if hasattr(pip, 'main'):
                pip.main(['install', package])
            else:
                pip._internal.main(['install', package])

        sended = await ctx.send('正在處理中...')
        try:
            if len(mod)!=0: install(mod)
            a = '\n'.join([f'{p.project_name} = {p.version}' for p in pkg_resources.working_set])
            await sended.edit(content=a)
        except Exception as e:
            a = '\n'.join([p.project_name for p in pkg_resources.working_set])+'\n'
            await sended.edit(content=a+f'error:{e}')
        
        
    #哪時候加入
    # @commands.hybrid_command(name='joined_加入時間',description="查看加入時間")
    # async def joined(self,ctx,members: commands.Greedy[discord.Member]):
    #     """何時加入伺服器"""
    #     if not members:
    #         members=[ctx.author]
    
    #     for member in members:
    #         print(member.nick)
    #         await ctx.send('{0.mention} joined on {0.joined_at}'.format(member))

async def setup(bot):
    await bot.add_cog(Pipp(bot))