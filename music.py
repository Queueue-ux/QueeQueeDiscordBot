# pip install youtube_dl
# pip install -U discord
# pip install python-dotenv
# pip install youtube_dl
# pip install PyNaCl
# add ffmpeg install to path if on windows

import os
import random

import time

from discord.ext import commands
from discord import utils

from dotenv import load_dotenv
from FunnyCounter import FunnyCounter
from music_player import music_player

load_dotenv()


TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
bot = commands.Bot(command_prefix='!')



@bot.event
async def on_ready():
    guild = utils.get(bot.guilds,name=GUILD)

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

@bot.command(name='flip',help='flips a coin, either heads or tails')
async def flip_coin(ctx, flips:int = 1):
    choices = ['Heads','Tails'] # space for printing purposes
    result_print = ""
    if flips > 500000:
        await ctx.send('Error: Max flips is 500000')
        return

    results = [random.choice(choices) for i in range(flips)]

    if flips > 1:
        heads = results.count('Heads')
        tails = results.count('Tails')
        result_print += f"\ntotal heads = {heads} ({heads/len(results)})\ntotal tails = {tails} ({tails / len(results)})"
    else:
        result_print += results[0]

    await ctx.send(result_print)

bot.add_cog(FunnyCounter(bot))
bot.add_cog(music_player(bot))
bot.run(TOKEN)
