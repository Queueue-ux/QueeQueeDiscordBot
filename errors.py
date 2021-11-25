from discord.ext import commands
import traceback

class ErrorHandling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(name='ReportError',help='allows user to report error, describe error the best you can')
    async def flip_coin(self, ctx, *args):
        if len(args) < 1:
            await ctx.send("please describe error as fully as you can")
        with open('err.log', 'a') as f:
            print(" ".join(args),file = f)
            print(f"\n\ncontext:\n{self._context_reader(ctx)}\n\n\n===========================================\n===========================================\n", file=f)
