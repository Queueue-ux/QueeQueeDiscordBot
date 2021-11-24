from discord.ext import commands
from discord import utils

class listeners(commands.Cog):
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild

    @commands.Cog.listener()    
    async def on_ready(self):
        guild = utils.get(self.bot.guilds,name=self.guild)

        print(
            f'{self.bot.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )

    @commands.cog.listener()
    async def on_error(self, event, *args, **kwargs):
        with open('err.log', 'a') as f:
            if event == 'on_message':
                f.write(f'Unhandled message: {args[0]}\n')
            else:
                raise