import discord
from discord.ext import commands
from discord.ext.commands import Context

import pandas as pd

import yfinance as yf 

class Finance(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

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