from datetime import datetime, timedelta,date
import os
from time import time
from neuralintents import GenericAssistant
import typing
import discord
from discord import ButtonStyle, Embed
from discord.ui import Select,View,Button
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()


class AI(commands.Cog, name="ai-commands"):
    def __init__(self, bot):
        self.bot = bot
        # 用我自己fork的 pip install git+https://github.com/flyhighhigh/neuralintents
        self.chatbot = GenericAssistant("intents.json")
        self.chatbot.train_model()
        self.chatbot.save_model(model_name='jacobbeta')

    #@commands.command(name="ai")
    @commands.Cog.listener('on_message')
    async def ai(self,message:discord.Message):
        if message.author == self.bot.user: return
        if message.channel.id != 1004422612891471912: return

        response = self.chatbot.request(message.content)
        if "{}" in response:
            response = response.format(message.author.mention)
        await message.reply(response)



async def setup(bot):
    await bot.add_cog(AI(bot))