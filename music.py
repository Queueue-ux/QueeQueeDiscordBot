# bot.py
# pip install youtube_dl
# pip install -U discord
# pip install python-dotenv
# pip install youtube_dl
import os
import random
import asyncio
import time
from youtube_dl import YoutubeDL
from discord.ext import commands
from discord import utils
from discord import FFmpegPCMAudio
from dotenv import load_dotenv

load_dotenv()
ydl_opts = {
    'format' : 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality' : '192',
    }],
}

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
bot = commands.Bot(command_prefix='!')
voice_channel_connection = None # global voice channel, used by all music commands
currently_playing = False
current_song = None
skip = False
music_queueue = []

funny_name = ""
funny_phrase = ""
funny_count = 0

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
@bot.event
async def on_ready():
    guild = utils.get(bot.guilds,name=GUILD)

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

@bot.event
async def on_voice_state_update(member,before,after):
    '''
        checks for when the bot disconnects, and sets its voice connected variable to None
    '''
    if not after.channel:
        if member == bot.user:
            print(bot.user)
            global voice_channel_connection
            voice_channel_connection = None
            currently_playing = False

@bot.command(name='play',help='plays video from youtube in voice channel, takes either a video to search or a direct youtube link')
async def play_music(ctx,*args):
    if len(args) == 0:
        await ctx.send("usage: !play {name of song / direct youtube link to song}")
        return
    if ctx.author.voice:
        global voice_channel_connection
        global music_queueue
        global currently_playing
        channel = ctx.author.voice.channel
        if not voice_channel_connection:
            voice_channel_connection = await channel.connect()
        with YoutubeDL(ydl_opts) as ydl:
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
            music_queueue.append({'source':source,'title':title,'thumbnail':thumbnail})
            await ctx.send(f"{title} added")
            if not currently_playing:
                currently_playing = True
                await _play_until_done(ctx)
            #source = info['formats'][0]['url']
            #music_player = FFmpegPCMAudio('In_the_Mirror.mp4')        
    else:
        await ctx.send('Error: must be in voice channel')

async def _play_until_done(channel):
    global currently_playing
    global music_queueue
    global voice_channel_connection
    global current_song
    global skip
    while music_queueue and voice_channel_connection:
        current_song = music_queueue.pop(0) # pop top of queue off
        if current_song['thumbnail']:
            await channel.send(current_song['thumbnail']) # post thumbnail
        await channel.send(f"now playing: {current_song['title']}") # post thumbnail
        voice_channel_connection.play(FFmpegPCMAudio(current_song['source'],**ffmpeg_options))
        while voice_channel_connection and (voice_channel_connection.is_playing() or not skip): # don't go to next song until we're done with the current song
            await asyncio.sleep(1)
        skip = False
        current_song = None
    currently_playing = False

@bot.command(name='pause',help='pauses current stream of music')
async def pause_music(ctx,*args):
    if ctx.author.voice: # check if invoking user is actually in channel
        global voice_channel_connection
        if voice_channel_connection:
            if voice_channel_connection.is_playing():
                voice_channel_connection.pause()
            else:
                await ctx.send('player already paused')

    else:
        await ctx.send('Error: must be in voice channel')
        
@bot.command(name='skip',help='skips current song')
async def skip_current(ctx,*args):
    global skip
    global voice_channel_connection
    global current_song
    voice_channel_connection.stop()
    skip = True
    await ctx.send(f"{current_song['title']} skipped")

@bot.command(name='queue',help='lists current song along with everything currently queued up')
async def list_queue(ctx,*args):
    global music_queueue
    global voice_channel_connection
    if voice_channel_connection and current_song:
        await ctx.send(f"now playing: {current_song['title']}\nQueued up:")
        queue_list = "".join([f"{i[0]+1}: {i[1]['title']}\n" for i in enumerate(music_queueue)])
        if len(queue_list) == 0:
            pass
        else:
            await ctx.send(queue_list)
    else:
        await ctx.send("queue empty")

@bot.command(name='remove',help='remove song from queue at index, default is top of queue')
async def remove_at_index(ctx, index:int = 1):
    global music_queueue
    removed = music_queueue.pop(index-1)
    await ctx.send(f"{removed['title']} removed")

@bot.command(name='resume',help='resumes current music stream')
async def pause_music(ctx,*args):
    if ctx.author.voice:
        global voice_channel_connection
        if voice_channel_connection:
            if voice_channel_connection.is_paused():
                voice_channel_connection.resume()
            else:
                await ctx.send('player already playing')
    else:
        await ctx.send('Error: must be in voice channel')

@bot.command(name='flip',help='flips a coin, either heads or tails')
async def flip_coin(ctx, flips:int = 1):
    choices = ['Heads','Tails'] # space for printing purposes
    result_print = ""
    if flips > 500000:
        await ctx.send('Error: Max flips is 500000')
        return

    results = [random.choice(choices) for i in range(flips)]

    if flips > 1:
        heads = results.count('Heads')
        tails = results.count('Tails')
        result_print += f"\ntotal heads = {heads} ({heads/len(results)})\ntotal tails = {tails} ({tails / len(results)})"
    else:
        result_print += results[0]

    await ctx.send(result_print)

'''
counter functions for tom funny tings
'''
@bot.command(name='funnyCounterInit',help='initializes the funny count to keep track of a funny thing')
async def funny_init(ctx, individual:str, *args):
    global funny_name
    global funny_phrase
    global funny_count
    funny_name = individual
    funny_phrase = " ".join(args)
    funny_count = 0

@bot.command(name='plusOne',help='add one to funny count')
async def add_to_counter(ctx,num:int = 1):
    global funny_count
    funny_count += num
    await ctx.message.delete()

@bot.command(name='displayFunny',help='display funny count')
async def add_to_counter(ctx,num:int = 1):
    global funny_name
    await ctx.send(f"{funny_name} has said: {funny_phrase} {funny_count} times")

bot.run(TOKEN)
