# pip install youtube_dl
# pip install -U discord
# pip install python-dotenv
#python3 -m pip install -U yt-dlp
# pip install PyNaCl
# add ffmpeg install to path if on windows

import os

from discord.ext import commands
from dotenv import load_dotenv
from FunnyCounter import FunnyCounter
from music_player import music_player
from misc import Miscellaneous
from listeners import listeners
from errors import ErrorHandling
from straw_poll import straw_poll

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')
bot.add_cog(FunnyCounter(bot))
bot.add_cog(music_player(bot))
bot.add_cog(Miscellaneous(bot))
bot.add_cog(listeners(bot,GUILD))
bot.add_cog(ErrorHandling(bot))
bot.add_cog(straw_poll(bot))

bot.run(TOKEN)
