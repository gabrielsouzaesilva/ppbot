import discord
from discord.ext import commands

import random

class Misc(commands.Cog):
    '''
    Class responsible for the management of miscellaneous functions of PPBot
    '''
    def __init__(self, bot):
        self.bot = bot
        self._ddd = "069"

    @commands.command()
    async def ping(self, ctx:commands.Context) -> None:
        await ctx.send(f"pong! {round(self.bot.latency * 1000)}ms")

    @commands.command()
    async def ddd(self, ctx:commands.Context) -> None:
        """
        Retorna o DDD do bot
        """
        await ctx.send(f"📞 DDD ({self._ddd})")

    @commands.command()
    async def rolldice(self, ctx:commands.Context) -> None:
        """Rolls a dice in NdN format."""
        result = ', '.join(str(random.randint(1, 6)))
        await ctx.send(result)

    @commands.command()
    async def slap(self, ctx:commands.Context, victim:str) -> None:
        print (victim)
        print (type(victim))
        await ctx.send(f"{ctx.author} slaps {victim}")
        '''
        if ctx.message.author.mention:
            await ctx.send(f"{ctx.author} slapped {ctx.message.author.mention}")
        else:
            await ctx.send(f"Use {ctx.prefix}slap @mention_username to slap someone 👋")
        '''