from discord.ext import commands
from discord import utils
import traceback

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

    def _context_reader(self,context):
        readable_context = ""
        readable_context += f"author: {context.author.display_name}#{context.author.discriminator}\n"
        readable_context += f"channel: {context.channel.name}\n"
        readable_context += f"command: {context.command}"
        readable_context += f"message: {context.message.content}"
        return readable_context

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error, *args, **kwargs):
        # dont need to worry about commandNotFound, shouldn't print for that
        ignored = (commands.CommandNotFound, )
        if isinstance(error, ignored):
            return
        with open('err.log', 'a') as f:
            traceback.print_exception(type(error),error,error.__traceback__,file=f)
            print(f"\n\ncontext:\n{self._context_reader(ctx)}\n\n\n===========================================\n===========================================\n", file=f)