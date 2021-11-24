from discord.ext import commands
from youtube_dl import YoutubeDL
from discord import FFmpegPCMAudio
import asyncio

class music_player(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.voice_channel_connection = None
        self.currently_playing = False
        self.current_song = None
        self.skip = False
        self.music_queueue = []
        self.ydl_opts = {
            'format' : 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality' : '192',
                }],
            }
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
            'options': '-vn'
            }
        

    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        '''
            checks for when the bot disconnects, and sets its voice connected variable to None
        '''
        if not after.channel:
            if member == self.bot.user:
                print(self.bot.user)
                self.voice_channel_connection = None
                self.currently_playing = False

    @commands.command(name='play',help='plays video from youtube in voice channel')
    async def play_music(self,ctx,*args):
        if len(args) == 0:
            await ctx.send("usage: !play {name of song / direct youtube link to song}")
            return
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if not self.voice_channel_connection:
                self.voice_channel_connection = await channel.connect()
            with YoutubeDL(self.ydl_opts) as ydl:
                user_input = " ".join(args)
                if user_input.find("https://www.youtube.com") != -1:
                    search = ydl.extract_info(user_input,download=False)
                    source = search['formats'][0]['url']
                    title = search['title']
                    thumbnail = None
                else:
                    search = ydl.extract_info(f"ytsearch:{user_input}",download=False)
                    source = search['entries'][0]['formats'][0]['url']
                    title = search['entries'][0]['title']
                    thumbnail = search['entries'][0]['thumbnail']
                self.music_queueue.append({'source':source,'title':title,'thumbnail':thumbnail})
                await ctx.send(f"{title} added")
                if not self.currently_playing:
                    self.currently_playing = True
                    await self._play_until_done(ctx) 
        else:
            await ctx.send('Error: must be in voice channel')

    async def _play_until_done(self,channel):
        while self.music_queueue and self.voice_channel_connection:
            self.current_song = self.music_queueue.pop(0) # pop top of queue off
            if self.current_song['thumbnail']:
                await channel.send(self.current_song['thumbnail']) # post thumbnail
            await channel.send(f"now playing: {self.current_song['title']}") # post thumbnail
            self.voice_channel_connection.play(FFmpegPCMAudio(self.current_song['source'],**self.ffmpeg_options))
            while self.voice_channel_connection and (self.voice_channel_connection.is_playing() or not self.skip): # don't go to next song until we're done with the current song
                await asyncio.sleep(1)
            self.skip = False
            self.current_song = None
        self.currently_playing = False

    @commands.command(name='pause',help='pauses current stream of music')
    async def pause_music(self,ctx,*args):
        if ctx.author.voice: # check if invoking user is actually in channel
            if self.voice_channel_connection:
                if self.voice_channel_connection.is_playing():
                    self.voice_channel_connection.pause()
                else:
                    await ctx.send('player already paused')

        else:
            await ctx.send('Error: must be in voice channel')
        
    @commands.command(name='skip',help='skips current song')
    async def skip_current(self,ctx,*args):
        self.voice_channel_connection.stop()
        self.skip = True
        await ctx.send(f"{self.current_song['title']} skipped")

    @commands.command(name='queue',help='lists current song along with everything currently queued up')
    async def list_queue(self, ctx,*args):
        if self.voice_channel_connection and self.current_song:
            await ctx.send(f"now playing: {self.current_song['title']}\nQueued up:")
            queue_list = "".join([f"{i[0]+1}: {i[1]['title']}\n" for i in enumerate(self.music_queueue)])
            if len(queue_list) == 0:
                pass
            else:
                await ctx.send(queue_list)
        else:
            await ctx.send("queue empty")

    @commands.command(name='remove',help='remove song from queue at index, default is top of queue')
    async def remove_at_index(self, ctx, index:int = 1):
        removed = self.music_queueue.pop(index-1)
        await ctx.send(f"{removed['title']} removed")

    @commands.command(name='resume',help='resumes current music stream')
    async def resume_music(self, ctx,*args):
        if ctx.author.voice:
            if self.voice_channel_connection:
                if self.voice_channel_connection.is_paused():
                    self.voice_channel_connection.resume()
                else:
                    await ctx.send('player already playing')
        else:
            await ctx.send('Error: must be in voice channel')