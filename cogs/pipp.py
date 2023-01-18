import discord
from discord import ButtonStyle, Embed
from discord.ui import Select,View,Button
from discord.ext import commands
import random
import typing
import json
import asyncio
from datetime import datetime,timedelta,timezone,date
import pip


class Pipp(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot    
    
    @commands.hybrid_command(name='pip',description="查看機器人延遲")
    async def pip(self,ctx:commands.Context):
        """機器人延遲"""
        
        def install(package):
            if hasattr(pip, 'main'):
                pip.main(['install', package])
            else:
                pip._internal.main(['install', package])

        sended = await ctx.send('正在處理中...')
        try:
            install('sxtwl')
            install('zhdate')
            await sended.edit(content=f'Current Ping = {round(self.bot.latency*1000)}ms')
        except Exception as e:
            await sended.edit(content=f'error:{e}')
        
        
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