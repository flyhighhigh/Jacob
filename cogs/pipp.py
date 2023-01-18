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


class Others(commands.Cog):
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

don = (['開墮！！！'],
       ['墮胎屬叔 AAAAA'],
       ['還敢下來啊冰鳥', '還敢下來啊**{0}**'],
       ['為什麼那個冰鳥還敢下來', '為什麼那個**{0}**還敢下來'],
       ['AAAA 嬰兒！', 'AAAA **{0}**！'],
       ['給庫！痾痾痾痾痾痾'],
       ['為什麼不幫我發大絕 極靈', '為什麼不幫我發大絕 **{0}**'],
       ['搭波kill！'],
       ['巨槌瑞斯 誇爪！哈哈哈'],
       ['哈撒ki 吹起來！聊天室滑起來！', '哈撒ki 吹起來！**{0}** 滑起來！'],
       ['DEATH IS LIKE THE WIND ALWAYS BY MY 賽'],
       ['嘿嘿嘿 又要死囉', '嘿嘿嘿 **{0}** 又要死囉'],
       ['瑞斯一打三！！！', '**{0}** 一打三！！！'],
       ['瑞斯一打五！', '**{0}** 一打五！'],
       ['這什麼...這到底什麼閃現 齁齁齁齁齁'],
       ['滑起來！通通給我滑起來！'],
       ['哈哈 又CARRY了一場 媽的'],
       ['逮到你囉！', '逮到你囉！**{0}**'],
       ['死好啊 媽的'],
       ['你看到我 媽的 巨...你看到我大槌達瑞斯 都不會怕的欸\n還在他媽 還在前面那邊洗兵耶',
        '**{0}** 看到我 媽的 巨...你看到我大槌達瑞斯 都不會怕的欸\n還在他媽 還在前面那邊洗兵耶'],
       ['喔沒有關係阿 沒有關係阿 還是讓我表演了一把阿'],
       ['鬼步開啟！！老爸墮起來！', '鬼步開啟！！**{0}** 墮起來！'],
       ['達瑞斯斷頭台！！！嬰兒通通死去', '**{0}** 斷頭台！！！嬰兒通通死去'],
       ['犽鎖開滑 嘻嘻嘻 爽哦', '**{0}** 開滑 嘻嘻嘻 爽哦'],
       ['老子瘋狗的外號他媽的10歲就有了 他媽咬死你啊糙',
        '**{0}** 瘋狗的外號他媽的10歲就有了 他媽咬死你啊糙'],
       ['媽的不讓你 不讓你見識一下 你是不知道誰是他媽的吃肉的啊'],
       ['抓進勞改營 準備好要被勞改了嗎'],
       ['家暴神拳 童家拳 開扁'],
       ['幹你不要再看了好不好 會不會來幫忙啊 糙'],
       ['你誰都可以得罪就是他媽不要得罪瘋子啊'],
       ['幹你老師的勒 媽的我給你嚇大的啊'],
       ['還想髒阿底迪', '還想髒阿 **{0}**'],
       ['我沒投在...'],
       ['拉進垃圾車！！'],
       ['狠狠的 把他甩到旁邊去', '狠狠的 把 **{0}** 甩到旁邊去'],
       ['從現在開始 瘋 狂 送 頭！'],
       ['幸福好運到 主委加碼', '幸福好運到 **{0}** 主委加碼'],
       ['乞丐大劍 轟'],
       ['你到底在幹嘛啊 天啊', '**{0}** 你到底在幹嘛啊 天啊'],
       ['還想閃現阿 HEHEHE', '**{0}** 還想閃現阿 HEHEHE'],
       ['一定打你 一定把你鼻樑打歪', '**{0}** 一定打你 一定把你鼻樑打歪'],
       ['太舒服拉'],
       ['下去囉！'],
       ['爽嗎兄弟', '爽嗎 **{0}** 兄弟'],
       ['下面一位'],
       ['整場上來零次！']
       )

async def setup(bot):
    await bot.add_cog(Others(bot))