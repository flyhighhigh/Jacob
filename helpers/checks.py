""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 4.1.1
"""

import os
from typing import TypeVar, Callable
from dotenv import load_dotenv
from discord.ext import commands

T = TypeVar("T")
load_dotenv()

flyhighhigh = 617692516871045121
OWU = 698431872157352003
G5 = 985817891268087818

def is_owner() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is an owner of the bot.
    """
    async def predicate(context: commands.Context) -> bool:
        if context.author.id == flyhighhigh: return True
        
        return False

    return commands.check(predicate)

def is_OWU(): #鬥大專屬
    async def predicate(context: commands.Context) -> bool:
        try:
            if context.guild.id == OWU: return True
            return False
        except:
            return False

    return commands.check(predicate)

def is_G5SH_guild(): #g5專屬
    async def predicate(context: commands.Context) -> bool:
        try:
            if context.guild.id == G5: return True
            return False
        except:
            return False

    return commands.check(predicate)