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
    @checks.is_owner()
    async def bazirole(self, ctx: commands.Context,yyyy:int,mm:int,dd:int,hh:typing.Optional[int]=-1) -> None:
        """
        輸入西元生日計算五行
        """
        ### 機器人身分組要是幾乎最高才可以，在他以上的他管不到
        sended = await ctx.send(embed=discord.Embed(description='正在處理中...'),ephemeral=True)

        if yyyy < 1900 or 1 > mm or mm > 12 or 1 > dd or dd > 31:
            return await sended.edit(embed=discord.Embed(description='輸入數值不正確！'),ephemeral=True)
            

        day = sxtwl.fromSolar(yyyy, mm, dd)
        yGZ = day.getYearGZ()
        mGZ = day.getMonthGZ()
        dGZ = day.getDayGZ()

        st = "八字 【 "+ Gan[yGZ.tg]+Zhi[yGZ.dz]+" "
        st += Gan[mGZ.tg]+Zhi[mGZ.dz]+" "
        st += Gan[dGZ.tg]+Zhi[dGZ.dz]+' '
        if hh != -1:
            hGZ = day.getHourGZ(hh)
            st += Gan[hGZ.tg]+Zhi[hGZ.dz]
        else:
            st += '- -'
        st += ' 】'

        ast = f'農曆 {day.getLunarYear()}年{day.getLunarMonth()}月{day.getLunarDay()}日'
        if hh != -1:
            ast += f'{hh}時'

        dst = "對照的五行為"+gan5[Gan[dGZ.tg]]+"\n"

        embed = discord.Embed(
            title=st,
            description=dst,
            color=colors[gan5[Gan[dGZ.tg]]]
        )
        embed.set_author(name=ast)
        embed.set_footer(
            text=f"已為 {ctx.author} 分發【{gan5[Gan[dGZ.tg]]}】身分組！"
        )
        await sended.edit(embed=embed,ephemeral=True)

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
