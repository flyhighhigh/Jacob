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
TEST_GUILD_ID = os.getenv('TEST_GUILD_ID')


OWNER = [628421176351260722,858897462206267433,617692516871045121]

def is_owner() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is an owner of the bot.
    """
    async def predicate(context: commands.Context) -> bool:
        for owner in OWNER:
            if context.author.id == owner: return True
        
        return False

    return commands.check(predicate)


def is_test_server():
    async def predicate(context: commands.Context) -> bool:
        if str(context.guild.id) == TEST_GUILD_ID:
            return True
        return False

    return commands.check(predicate)