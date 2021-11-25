from discord.ext import commands
import random

class Miscellaneous(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command(name='flip',help='flips a coin, either heads or tails')
    async def flip_coin(self, ctx, flips:int = 1):
        choices = ['Heads','Tails'] # space for printing purposes
        result_print = ""
        if flips > 500000:
            await ctx.send('Error: Max flips is 500000')
            return
        if flips <= 0:
            await ctx.send('```fix\nidiot```')
            return

        results = [random.choice(choices) for i in range(flips)]

        if flips > 1:
            heads = results.count('Heads')
            tails = results.count('Tails')
            result_print += f"\ntotal heads = {heads} ({heads/len(results)})\ntotal tails = {tails} ({tails / len(results)})"
        else:
            result_print += results[0]

        await ctx.send(result_print)