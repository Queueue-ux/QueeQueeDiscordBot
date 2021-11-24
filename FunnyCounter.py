from discord.ext import commands

class FunnyCounter(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.funny_name = ""
        self.funny_phrase = ""
        self.funny_count = 0
    
    @commands.command(name='funnyCounterInit',help='initializes the funny count')
    async def funny_init(self, ctx, individual:str, *args):
        self.funny_name = individual
        self.funny_phrase = " ".join(args)
        self.funny_count = 0

    @commands.command(name='plusOne',help='add one to funny count')
    async def plus_one(self, ctx, num:int = 1):
        self.funny_count += num
        await ctx.message.delete()

    @commands.command(name='displayFunny',help='display funny count')
    async def display(self, ctx,num:int = 1):
        global funny_name
        await ctx.send(f"{self.funny_name} has said: {self.funny_phrase} {self.funny_count} times")