import os

import discord
from discord import client
from discord.ext import commands
from discord.ext.commands.core import command
import emoji

import random
import pandas as pd

# Mover para modulo externo depois
import yfinance as yf 

from modules import Music

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn'
}

class PPBot(commands.Cog):
    def __init__(self, bot):
        self.base_prefix = "$"
        self.bot = bot
        self._ddd = "069"
        self._ytb_music = Music.MusicYTB()

    # Bot commands
    @commands.command()
    async def rolldice(self, ctx):
        """Rolls a dice in NdN format."""
        result = ', '.join(str(random.randint(1, 7)))
        await ctx.send(result)

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"pong! {round(self.bot.latency * 1000)}ms")

    @commands.command()
    async def ddd(self, ctx):
        """
        Retorna o DDD do bot
        """
        await ctx.send(f"📞 DDD ({self._ddd})")

    @commands.command()
    async def stock(self, ctx, ticker, e=None, cf=None):
        stock = yf.Ticker(ticker+".SA")
        start_date = pd.to_datetime("today") - pd.Timedelta(7, "D")

        stock_hist = stock.history(start=start_date, end=pd.to_datetime("today"))
        stock_hist.drop(columns=["Dividends", "Stock Splits"], inplace=True)
        
        # Add price variation to table
        stock_hist["Var (%)"] = 100*(stock_hist['Close'] - stock_hist['Open'])/stock_hist['Open']

        #todays_price = stock_hist.iloc[0]
        # await ctx.send(f"{ticker} Stock price @{pd.to_datetime('today')} ~ Open = R${todays_price.Open} // Hi/Lo = R${todays_price.High}/R${todays_price.Low} // Close = R${todays_price.Close}")

        await ctx.send(f"```{stock_hist.to_markdown()}```")

        if (ticker in ['cogn3', 'cogn', 'conga']):
            await ctx.send("CONGA É 30!! 🙈")

        if (e):
            await ctx.send(f"```{stock.quarterly_earnings.to_markdown()}```")

        if (cf):
            # Limit length of message is 2000, so split Q_cashflow in two
            await ctx.send(f"```{stock.quarterly_cashflow.iloc[:8, :].to_markdown()}```")
            await ctx.send(f"```{stock.quarterly_cashflow.iloc[8:, :].to_markdown()}```")

    ## MUSIC MODULE
    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not in a voice channel ! Please join a voice channel.")

        voice_channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)
    
    @commands.command()
    async def dc_voice(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command()
    async def play(self, ctx, url):
        ctx.voice_client.stop()
        source = await discord.FFmpegOpusAudio.from_probe(self._ytb_music.get_ffmpeg_url(url), **FFMPEG_OPTIONS)
        ctx.voice_client.play(source)

    @commands.command()
    async def search_play(self, ctx, query):
        ctx.voice_client.stop()
        url = self._ytb_music.search_url(query)
        source = await discord.FFmpegOpusAudio.from_probe(self._ytb_music.get_ffmpeg_url(url), **FFMPEG_OPTIONS)
        ctx.voice_client.play(source)
        await ctx.send(f"Now playing 😎 >> {url}")

    @commands.command()
    async def pause(self, ctx):
        await ctx.voice_client.pause()
        await ctx.send("Paused ⏸️")

    @commands.command()
    async def resume(self, ctx):
        await ctx.voice_client.resume()
        await ctx.send("Resuming ▶️")

    ## Bot event functions
    @commands.Cog.listener()
    async def on_ready(self):
        startup_text = emoji.emojize("Patife Bot is online 😎")
        print (startup_text)

# Create bot, cog and run
bot = commands.Bot(command_prefix = "!")
bot.add_cog(PPBot(bot))
bot.run(os.environ.get('PPBOT_TOKEN'))