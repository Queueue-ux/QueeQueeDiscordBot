from discord.channel import DMChannel
from discord.ext import commands

class straw_poll(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.is_poll_active = False
        self.author = None
        self.already_voted = [] # list of everyone who has voted
        self.poll_name = None
        self.edit_message = None
        self.options = []
        self.auto_end = False
    
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
                            change_index = self.edit_message.content.index(user_vote) + len(user_vote) + 1
                            number = str(int(self.edit_message.content[change_index]) + 1)
                            new_message = self.edit_message.content[:change_index] + number + self.edit_message.content[change_index + 1:]
                            await self.edit_message.edit(content = new_message)
                            return
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
        self.author = ctx.author
        self.options = " ".join(args).strip().split(',')
        self.options = [i.strip() for i in self.options]
        self.options = {i:0 for i in self.options}
        
        self.edit_message = await ctx.send(f"NEW POLL\n{self.poll_name}\n\ncast your vote by DMing QueeQUeeJr:\n !vote " "{option you want}" + "\n\nOPTIONS\n" + "".join([i + " 0\n" for i in self.options]))
    
    @commands.command(name='endPoll',help='create straw poll')
    async def end_poll(self, ctx, *args):
        #make sure the person ending the poll is the one that started it
        if ctx.author == self.author or self.auto_end:
            split_message = self.edit_message.content.split()
            highest = ['option',-100000]
            for k,v in self.options.items():
                option_index = split_message.index(k) + 1
                if int(split_message[option_index]) > highest[1]:
                    highest[0] = k
                    highest[1] = int(split_message[option_index])
            print("hello")
            final_message = self.edit_message.content[:] + f'\n```JSON\n\n"{highest[0]} WON WITH {highest[1]} VOTES"```'
            await self.edit_message.edit(content = final_message)
            self.is_poll_active = False
            self.author = None
            self.already_voted = [] # list of everyone who has voted
            self.poll_name = None
            self.edit_message = None
            self.options = []
        else:
            await ctx.send("only creater of poll can end it")
