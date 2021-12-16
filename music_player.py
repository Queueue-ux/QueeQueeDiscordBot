from datetime import timedelta
from discord.ext import commands
from yt_dlp import YoutubeDL
from discord import FFmpegPCMAudio
import time
import copy
import asyncio
from os import getcwd

class music_player(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.voice_channel_connection = None
        self.currently_playing = False
        self.paused = False
        self.current_song = None
        self.seconds_playing = 0
        self.skip = False
        self.loop = False
        self.start_time = 0 # TESTING ONLY
        self.end_time = 0 # TESTING ONLY
        self.music_queueue = []
        test = getcwd() + '\\youtube.com_cookies.txt'
        print(test)
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality' : '192',
                }],
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'simulate' : True,
            'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
            'cookiefile:' : getcwd() + '\\youtube.com_cookies.txt',
            'prefer_ffmpeg' : True,
        }
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
            'options': '-vn',
            } # -ar 22050 for funny
        

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
            for x in before.channel.guild.channels:
                if x.name == "general-garbage":
                    await x.send("see ya!")
                    return
            

    @commands.command(name='play',help='plays video from youtube in voice channel')
    async def play_music(self,ctx,*args, rate="48000"):
        self.start_time = time.perf_counter() # TESTING ONLY
        if len(args) == 0:
            await ctx.send("usage: !play {name of song / direct youtube link to song}")
            return
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            loop = self.bot.loop
            #loop = asyncio.get_event_loop()
            if not self.voice_channel_connection:
                self.voice_channel_connection = await channel.connect()
            with YoutubeDL(self.ydl_opts) as ydl:
                user_input = " ".join(args)
                
                if user_input.find("https://www.youtube.com") != -1:
                    # run_in_executor basically allows ydl to use threading
                    search = await loop.run_in_executor(None, lambda: ydl.extract_info(user_input,download=False))
                    source = search['formats'][0]['url']
                    title = search['title']
                    duration = timedelta(seconds = search['duration'])
                    thumbnail = None
                    
                else:
                    # first find actual link- can't use youtube-dl because it will break on age-restrict
                    # run_in_executor basically allows ydl to use threading
                    search = await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch:{user_input}" ,download=False))
                    if not search['entries']:
                        await ctx.send("error retrieving video")
                        return
                    '''for x in search['entries'][0]['formats']: # find the first source with ASR of 48000 to match hz of ffmpeg
                        if x['asr'] == 48000:
                            source = x['url']
                            break'''
                    source = search['entries'][0]['formats'][0]['url']
                    title = search['entries'][0]['title']
                    thumbnail = search['entries'][0]['thumbnail']
                    duration = timedelta(seconds = search['entries'][0]['duration'])

                self.music_queueue.append({'source':source,'title':title,'thumbnail':thumbnail,'duration':duration,'hz':rate})
                total_time = timedelta(seconds = 0)
                for x in self.music_queueue:
                    total_time += x['duration']
                if self.current_song:
                    await ctx.send(f"{title} ({duration}) added (playing in {(self.current_song['duration'] - timedelta(seconds = self.seconds_playing)) + total_time})")
                else:
                    await ctx.send(f"{title} ({duration}) added")
                # testing timings

                self.dl_time = time.perf_counter()
                print(f"youtube_dl time: {self.dl_time - self.start_time}")

                if not self.currently_playing:
                    self.currently_playing = True
                    await self._play_until_done(ctx) 
        else:
            await ctx.send('Error: must be in voice channel')

    async def _play_until_done(self,channel,options=True):
        while (self.music_queueue and self.voice_channel_connection) or self.current_song:
            self.seconds_playing = 0
            if self.loop:
                if not self.current_song:
                    self.current_song = self.music_queueue.pop(0)
            else:
                self.current_song = self.music_queueue.pop(0) # pop top of queue off

            if self.current_song['thumbnail']:
                await channel.send(self.current_song['thumbnail']) # post thumbnail
            if not self.loop:
                await channel.send(f"**now playing**: {self.current_song['title']} ({self.current_song['duration']})") # post thumbnail
            modified_options = copy.deepcopy(self.ffmpeg_options)
            modified_options['options'] += f" -ar {self.current_song['hz']}"
            self.voice_channel_connection.play(FFmpegPCMAudio(self.current_song['source'], **modified_options))

            # testing performance
            self.end_time = time.perf_counter()
            print(f"ffmpeg_time: {self.end_time - self.dl_time}")
            print(f"TOTAL TIME: {self.end_time-self.start_time}\n")

            while self.voice_channel_connection and (self.voice_channel_connection.is_playing() and not self.skip) or self.paused: # don't go to next song until we're done with the current song
                await asyncio.sleep(1)
                self.seconds_playing += 1
            self.skip = False
            if not self.loop:
                self.current_song = None
        self.currently_playing = False
    
    async def _noSkip(self):
        if not self.skip:
            self.skip = True

    @commands.command(name='hp',help='plays video from youtube in voice channel')
    async def harry_potter_XD(self,ctx):
        await self.play_music(ctx,"harry potter distorted")

    @commands.command(name='nightcore',aliases=['nc'],help='takes a youtube search/link and makes it nightcore')
    async def nightcore(self,ctx,*args):
        await self.play_music(ctx,*args,rate="27000")

    @commands.command(name='nightcoretr',aliases=['nctr'],help='takes a youtube search/link and makes it nightcore')
    async def nightcore_trap_remix(self,ctx,*args):
        await self.play_music(ctx," ".join(args) + " trap remix",rate="27000")

    @commands.command(name='tr',help='makes youtube search a trap remix')
    async def trap_remix(self,ctx,*args):
        await self.play_music(ctx," ".join(args) + " trap remix")

    @commands.command(name='current',aliases=['np'],help='plays video from youtube in voice channel')
    async def display_current(self,ctx):
        total_time = timedelta(seconds = self.seconds_playing)
        await ctx.send(f"**currently playing**: {self.current_song['title']}\n{total_time}/{self.current_song['duration']}")

    @commands.command(name='pause',help='pauses current stream of music')
    async def pause_music(self,ctx,*args):
        if ctx.author.voice: # check if invoking user is actually in channel
            if self.voice_channel_connection:
                if self.voice_channel_connection.is_playing():
                    self.paused = True
                    self.voice_channel_connection.pause()
                else:
                    await ctx.send('player already paused')

        else:
            await ctx.send('Error: must be in voice channel')
        
    @commands.command(name='clearQueue',help='pauses current stream of music')
    async def clear(self,ctx,*args):
        self.music_queueue = []

    @commands.command(name='skip',help='skips current song')
    async def skip_current(self,ctx,*args):
        if self.currently_playing:
            self.voice_channel_connection.stop()
            self.skip = True
            self.paused = False
            self.loop = False
            #self.current_song = None
            await ctx.send(f"**skipped --** {self.current_song['title']}")

    @commands.command(name='love',help='people fall in love in mysterious ways')
    async def love_you(self, ctx, *args):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if not self.voice_channel_connection:
                self.voice_channel_connection = await channel.connect()
            self.music_queueue.append({'source':'love.mp3','title':'people fall in love','thumbnail':None,'duration':timedelta(seconds = 7)})
            if not self.currently_playing:
                self.currently_playing = True
                await self._play_until_done(ctx,options=False)

    @commands.command(name='queue',aliases = ["q","que"],help='lists current song along with everything currently queued up')
    async def list_queue(self, ctx,list_full = False,*args):
        if self.voice_channel_connection and self.current_song:
            await ctx.send(f"**now playing**: {self.current_song['title']}({self.current_song['duration']})\nQueue:")
            total_time = timedelta(seconds = 0)
            for x in self.music_queueue:
                total_time += x['duration']
            queue_list = f"total time: {total_time}\n"
            if list_full:
                queue_list += "".join([f"\t{i[0]+1}: {i[1]['title']}({i[1]['duration']})\n" for i in enumerate(self.music_queueue)])
            else:
                queue_list += "".join([f"\t{i[0]+1}: {i[1]['title']}({i[1]['duration']})\n" for i in enumerate(self.music_queueue) if i[0] + 1 < 6])
            
            if len(self.music_queueue) >= 6 and not list_full:
                queue_list += f"...\ntotal queue length: {len(self.music_queueue)}{len(self.music_queueue) - 5} more\n"

            if len(queue_list) == 0:
                pass
            else:
                await ctx.send(queue_list)
        else:
            await ctx.send("queue empty")

    @commands.command(name='queueListAll',help='lists full queue')
    async def list_queue_full(self, ctx,*args):
        await self.list_queue(ctx,list_full = True)

    @commands.command(name='remove',help='remove song from queue at index, default is top of queue')
    async def remove_at_index(self, ctx, index:int = 1):
        if len(self.music_queueue) >= index-1:
            removed = self.music_queueue.pop(index-1)
            await ctx.send(f"{removed['title']} removed")
        else:
            await ctx.send(f"index not in queue")
    
    @commands.command(name='join',help='bot leaves channel')
    async def join_channel(self, ctx,*args):
        channel = ctx.author.voice.channel
        self.voice_channel_connection = await channel.connect()
    
    @commands.command(name='loop',help='loop current song, call again to stop looping')
    async def loop_song(self, ctx):
        if not self.loop:
            if self.current_song:
                await ctx.send(f"{self.current_song['title']} now looping")
            else:
                await ctx.send(f"next song will loop")
            self.loop = True
        else:
            if self.current_song:
                await ctx.send(f"{self.current_song['title']} no longer loop")
            else:
                await ctx.send(f"next song will no longer loop")
            self.loop = False

    @commands.command(name='leave',help='bot leaves channel')
    async def leave_channel(self, ctx,*args):
        await self.voice_channel_connection.disconnect()
        self.voice_channel_connection = None

    @commands.command(name='resume',help='resumes current music stream')
    async def resume_music(self, ctx,*args):
        if ctx.author.voice:
            if self.voice_channel_connection:
                if self.voice_channel_connection.is_paused():
                    self.voice_channel_connection.resume()
                    self.paused = True
                else:
                    await ctx.send('player already playing')
        else:
            await ctx.send('Error: must be in voice channel')