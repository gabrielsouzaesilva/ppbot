import discord
from discord.ext import commands

import os

from modules import MusicYTB, Finance, Misc

class PPBot(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        startup_text = "Patife Bot is online !!"
        print (startup_text)

    @commands.command()
    async def help(self, ctx:commands.Context, parameter=None):
        if (parameter):
            if (parameter in self.bot.cogs.keys()):
                cog = self.bot.get_cog(parameter)
                await ctx.send(f"Cog request sucesso !")
            else:
                await ctx.send(f"{parameter} is not a PP module !")
                await ctx.send(f"Available modules are: {list(self.bot.cogs.keys())}")
        else:
            for cog_name, cog in self.bot.cogs.items():
                cmd_list = []
                for cog_cmd in cog.get_commands():
                    cmd_list.append(cog_cmd.name)

                await ctx.send(f"Module {cog_name}")
                await ctx.send(f"Commands >> {cmd_list}")

# Create bot, add cogs and run
bot = commands.Bot(command_prefix = "$", help_command=None)
bot.add_cog(PPBot(bot))
bot.add_cog(MusicYTB(bot))
bot.add_cog(Finance(bot))
bot.add_cog(Misc(bot))
bot.run(os.environ.get('PPBOT_TOKEN'))