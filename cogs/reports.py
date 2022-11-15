from datetime import datetime, timedelta,date
import json
import os
from time import time
import discord
from discord import ButtonStyle, Embed
from discord.ui import Select,View,Button
from discord.ext import commands
from requests import options
from helpers import checks

class Report(commands.Cog, name="Report"):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.reports: list = self.prev_reports()

    def prev_reports(self):
        with open('reports.json','r',encoding='utf-8') as file:
            reports = json.load(file)['reports']
        return reports
    
    @commands.hybrid_command(
        name="report_拉清單",
        description="別看今日鬧的歡，小心今後拉清單"
    )
    async def report(self, ctx: commands.Context,idiot:str,reason:str=None):
        """
        拉清單
        """
        print(ctx.author.id)
        # print(value=f"作者:<@{votes[i]['author_id']}> | ")
        sended = await ctx.send(embed=Embed(
            description='正在處理中...',
            color=discord.Color.dark_blue()
        ))
        self.reports.append({'name':idiot,'reason':reason,"author":ctx.author.id})
        embed = Embed(
            title=f'{idiot} | {reason}',
            color=discord.Colour.green()
        )
        embed.set_author(name='✅ | 舉報成功')
        embed.set_footer(text='鬥大感謝你的舉報',icon_url='https://cdn-longterm.mee6.xyz/plugins/welcome/images/698431872157352003/aa9f42d312a0ae398257f0377d151f175d5a6e600981f74bbc51ecd0f8e4f696.gif')
        await sended.edit(embed=embed)
        
        # store to reports.json
        with open('reports.json','w',encoding='utf-8') as file:
            temp = {'reports':self.reports}
            json.dump(temp,file,indent=4)
    

    @commands.hybrid_command(
        name="delete_report_解除清單",
        description="解除被誤拉的清單"
    )
    async def _delete_report(self, ctx: commands.Context,idiot:str):
        """
        解除清單
        """
        print(ctx.author.id)
        sended = await ctx.send(embed=Embed(
            description='正在處理中...',
            color=discord.Color.dark_blue()
        ))
        finded = [i for i in self.reports if i["name"] == idiot and i["author"] == ctx.author.id]
        
        result_str = ''
        if len(finded) == 0: # 沒有找到
            result_str = f'找不到有關 {idiot} 的回報，或你沒有權限刪除該資料'
            
        else:
            for i in finded:
                self.reports.remove(i)
            result_str = f'已刪除{len(finded)}筆有關 {idiot} 的回報'
        
        embed = Embed(
            title=result_str,
            color=discord.Colour.green()
        )
        embed.set_author(name='✅ | 解除清單')
        embed.set_footer(text='鬥大感謝你的回報',icon_url='https://cdn-longterm.mee6.xyz/plugins/welcome/images/698431872157352003/aa9f42d312a0ae398257f0377d151f175d5a6e600981f74bbc51ecd0f8e4f696.gif')
        
        await sended.edit(embed=embed)
        
        # store to reports.json
        with open('reports.json','w',encoding='utf-8') as file:
            temp = {'reports':self.reports}
            json.dump(temp,file,indent=4)

    @commands.hybrid_command(
        name="show_reports_查看目前清單",
        description="別看今日鬧的歡，小心今後拉清單"
    )
    async def _show_reports(self, ctx: commands.Context):
        """
        秀出目前清單
        """
        sended = await ctx.send(embed=Embed(
            description='正在處理中...',
            color=discord.Color.dark_blue()
        ))

        msg = ''
        for rpt in self.reports:
            name = rpt['name']
            reason = rpt['reason']
            author = rpt['author']
            msg += f"`{name}` {reason} (by:<@{votes[i]['author_id']}>)\n"
        embed = Embed(
            description=msg,
            color=discord.Color.green()
        )
        
        embed.set_author(name='✅ | 目前舉報清單')
        embed.set_footer(text='鬥大感謝你的舉報',icon_url='https://cdn-longterm.mee6.xyz/plugins/welcome/images/698431872157352003/aa9f42d312a0ae398257f0377d151f175d5a6e600981f74bbc51ecd0f8e4f696.gif')
        await sended.edit(embed=embed)
        


async def setup(bot):
    await bot.add_cog(Report(bot))
