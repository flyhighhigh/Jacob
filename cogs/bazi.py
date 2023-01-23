""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 4.1.1
"""

import typing
import discord
from discord import Interaction
from discord.ext import commands
from helpers import checks
from zhdate import ZhDate
from datetime import datetime
import sxtwl

roles = {
    '金':1000800640760565821,
    '木':1000800679771766784,
    '水':1000800736004800632,
    '火':1000800757915848826,
    '土':1000800799292670023
}
colors = {
    '金':discord.Color.gold(),
    '木':discord.Color.green(),
    '水':discord.Color.blue(),
    '火':discord.Color.red(),
    '土':discord.Color.dark_gold()
}

Gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
Zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
gan5 = {"甲":"木", "乙":"木", "丙":"火", "丁":"火", "戊":"土", "己":"土", 
    "庚":"金", "辛":"金", "壬":"水", "癸":"水"}



class Bazi(commands.Cog, name="bazi-commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="bazi",
        description="輸入西元生日計算五行"
    )
    async def bazirole(self, ctx: commands.Context,year:int,month:int,day:int,hour:typing.Optional[int]) -> None:
        """
        輸入西元生日計算五行
        """
        ### 機器人身分組要是幾乎最高才可以，在他以上的他管不到
        sended = await ctx.send(embed=discord.Embed(description=f'{year}/{month}/{day}/{hour}，正在處理中...'),ephemeral=True)
        date = None
        try:
            if not hour: date = datetime(year,month,day)
            else: date = datetime(year,month,day,hour)
            await ctx.send(embed=discord.Embed(description=f'{date}'),ephemeral=True)
            lunar_date = sxtwl.fromSolar(date.year,date.month,date.day) # 換算農曆
            yGZ = lunar_date.getYearGZ()
            mGZ = lunar_date.getMonthGZ()
            dGZ = lunar_date.getDayGZ()
            
            st = "八字 【 "+ Gan[yGZ.tg]+Zhi[yGZ.dz]+" "
            st += Gan[mGZ.tg]+Zhi[mGZ.dz]+" "
            st += Gan[dGZ.tg]+Zhi[dGZ.dz]+' '

            ast = f'農曆 {lunar_date.getLunarYear()}年' 
            ast += f'{lunar_date.getLunarMonth()}月{lunar_date.getLunarDay()}日'

            if not hour: st += '－－'
            else:
                hGZ = day.getHourGZ(hour)
                st += Gan[hGZ.tg]+Zhi[hGZ.dz]
                ast += f'{hour}時'
            
            st += ' 】'
            dst = f"您的日主天干為【{gan5[Gan[dGZ.tg]]}】"

            embed = discord.Embed(
                title=dst,
                description=st+'\n'+ast,
                color=colors[gan5[Gan[dGZ.tg]]]
            )
            embed.set_author(name='五行查詢結果',icon_url=self.bot.user.avatar)
            embed.set_footer(
                text=f"已為 {ctx.author.display_name} 分發【{gan5[Gan[dGZ.tg]]}】身分組！"
            )
            await ctx.send(embed=embed,ephemeral=True)
        except Exception as e:
            return await ctx.send(embed=discord.Embed(description=f'輸入數值不正確：{e}'),ephemeral=True)
        
        #分發身分組
        try:
            for role_id in roles.values():
                if role_id != roles[gan5[Gan[dGZ.tg]]]:
                    await ctx.author.remove_roles(ctx.guild.get_role(role_id))
                else:
                    await ctx.author.add_roles(ctx.guild.get_role(role_id))
        except:
            pass

        


async def setup(bot):
    await bot.add_cog(Bazi(bot))
