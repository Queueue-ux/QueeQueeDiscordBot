from discord.channel import DMChannel
from discord.ext import commands

class straw_poll(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.is_poll_active = False
        self.author = None
        self.already_voted = [] # list of everyone who has voted
        self.poll_name = None
        self.options = []
    
    @commands.Cog.listener()
    async def on_message(self,message):
        if isinstance(message.channel,DMChannel):
            if self.is_poll_active:
                message_content = message.content.strip().split(" ")
                if message_content[0] == "!vote":
                    if message.author in self.already_voted:
                        await message.channel.send("can only vote once")
                    else:
                        user_vote = " ".join(message_content[1:]).strip()
                        if user_vote in self.options:
                            self.options[user_vote] += 1
                            self.already_voted.append(message.author)

                            # next update the poll to show the new vote

                            #first find message in the cache
                            messages = self.bot.cached_messages._SequenceProxy__proxied
                            for i in range(len(messages) - 1, -1, -1):
                                message_content = messages[i].content
                                strip_message = message_content.split('\n')
                                if strip_message[0] == "NEW POLL":#found the message we want to edit!
                                    print(strip_message)
                        else:
                            await message.channel.send("invalid option")

    @commands.command(name='createPoll',help='create straw poll')
    async def create_poll(self, ctx, pollName:str="",*args):
        if self.is_poll_active:
            await ctx.send("poll already in progress, please end previous poll to start a new one")
            return

        if pollName == "" or len(args) < 1:
            await ctx.send("usage: createPoll {poll name} {all options for poll separated by commas}")
            return
        self.is_poll_active = True
        self.poll_name = pollName
        self.options = " ".join(args).strip().split(',')
        self.options = [i.strip() for i in self.options]
        self.options = {i:0 for i in self.options}
        
        await ctx.send(f"NEW POLL\n{self.poll_name}\n\ncast your vote by DMing QueeQUeeJr:\n !vote " "{option you want}" + "\n\nOPTIONS\n" + "".join([i + " 0\n" for i in self.options]))



        
    @commands.command(name='endPoll',help='create straw poll')
    async def end_poll(self, ctx, *args):
        pass
