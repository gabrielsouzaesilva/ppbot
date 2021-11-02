import discord
from discord.ext import commands
from discord.ext.commands.core import after_invoke, command

import youtube_dl
import requests
import validators

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn'
}

class Song():
    def __init__(self, title, url) -> None:
        self.title = title
        self.url = url

    def get_title(self):
        return self.title
    
    def get_url(self):
        return self.url

class MusicYTB(commands.Cog):
    '''
    Class dedicated to the management of music functions that use Youtube
    as source of content.
    '''
    def __init__(self, bot) -> None:
        self.bot = bot
        self.music_queue = {}
        self.current_song = None

    @commands.command()
    async def join(self, ctx:commands.Context) -> None:
        '''
        Make bot join voice channel

        Parameters
        ----------
        ctx:commands.Context
            Discord Context
        
        Returns
        -------
        '''
        if ctx.author.voice is None:
            await ctx.send("You are not in a voice channel ! Please join a voice channel.")

        voice_channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)
    
    @commands.command()
    async def bye(self, ctx:commands.Context) -> None:
        await ctx.voice_client.disconnect()
        await ctx.send("Bye ! PPBot left voice channel. 👋")

    @commands.command()
    async def np(self, ctx:commands.Context) -> None:
        if ctx.voice_client.is_playing():
            await ctx.send(f"Now playing >> {self.current_song} <<")
        else:
            await ctx.send("Nothing playing")

    @commands.command()
    async def stop(self, ctx:commands.Context) -> None:
        ctx.voice_client.stop()

    @commands.command()
    async def play(self, ctx:commands.Context, *params) -> None:
        '''
        Makes bot join a voice channel and play audio

        Parameters
        ----------
        ctx : commands.Context
            Discord Context
        
        *params : dict
            A url or a query to search

        Returns
        -------
        None
        '''
        # Check if params is a url
        if validators.url(params[0]):
            url = params[0]
        else:
            # Append query elements
            query = ' '.join(params)
            url = self.search_url(query)

        # Check if user is in voice channel
        if ctx.author.voice is None:
            return await ctx.send("You are not in a voice channel ! Please join a voice channel.")
        else:
            await self.join(ctx)

        # Get ytb video info
        video_info = self.get_video_info(url)
        song_title = video_info['title']
        ffmpeg_url = video_info['formats'][0]['url']

        if (ctx.voice_client.is_playing()):
            # If player is playing add song to music queue
            if (ctx.guild.id not in self.music_queue):
                self.create_guild_queue(ctx.guild.id)

            self.music_queue[ctx.guild.id].append(Song(song_title, url))
            await ctx.send(f"Song >> {song_title} << added to queue")
            return None
            
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ffmpeg_url, **FFMPEG_OPTIONS))
        ctx.voice_client.play(
            source, 
            after=lambda error: self.queue_after_func(ctx)
        )
        self.current_song = song_title
        await ctx.send(f"Now playing 😎 >> {url}")

    @commands.command()
    async def pause(self, ctx:commands.Context):
        ctx.voice_client.pause()
        await ctx.send("Paused ⏸️")

    @commands.command()
    async def resume(self, ctx:commands.Context):
        ctx.voice_client.resume()
        await ctx.send("Resuming ▶️")

    @commands.command()
    async def volume(self, ctx:commands.Context, vol:int=None):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        if (vol is None):
            return await ctx.send(f"No value for volume was passed")
        
        if (vol >= 100):
            vol = 100.0
            await ctx.send(f"Setting vol as 100%. I'm not a 'Saveiro Paredão' 😆")

        ctx.voice_client.source.volume = vol / 100.0
        await ctx.send(f"Volume set to {vol}% 🔊")

    # Music queue
    @commands.group()
    async def queue(self, ctx:commands.Context) -> None:
        # Check if guild has queue
        if (ctx.guild.id not in self.music_queue):
            self.create_guild_queue(ctx.guild.id)

        if ctx.invoked_subcommand is None:
            print (self.music_queue)

            # Playlist message title
            queue_msg = ">>> 🎶 Playlist Queue 🎶 \n"

            # Check if music queue is empty and return if so
            if len(self.music_queue[ctx.guild.id]) == 0:
                return await ctx.send(queue_msg + "Empty queue")

            # Creates playlist message. One music per line
            for i, song in enumerate(self.music_queue[ctx.guild.id]):
                queue_line = f"**{i}** - {song.title} \n"
                queue_msg += queue_line
            
            await ctx.send(queue_msg[:1999]) # Manage big queues >>2000chars

    @queue.command()
    async def add(self, ctx:commands.Context, *params) -> None:
        # Check if params is a url
        if validators.url(params[0]):
            url = params[0]
        else:
            # Append query elements
            query = ' '.join(params)
            url = self.search_url(query)

        # Get ytb video info
        video_info = self.get_video_info(url)
        ffmpeg_url = video_info['formats'][0]['url']
        title = video_info['title']
        
        # Append song to queue
        self.music_queue[ctx.guild.id].append(Song(title, url))

        await ctx.send(f">> {title} << Added to queue !")

    @queue.command()
    async def remove(self, ctx:commands.Context, idx:int) -> None:
        '''
        Remove song from music queue

        Parameters
        ----------
        ctx:commands.Context
            Discord Context
        idx:int
            Index of song in queue
        '''
        if (0 <= idx < len(self.music_queue[ctx.guild.id])):
            self.music_queue[ctx.guild.id].pop(idx)
            return None
        else:
            return await ctx.send(f"Music id {idx} is out of range")

    @queue.command()
    async def clear(self, ctx:commands.Context) -> None:
        '''
        Queue sub-command to clear music queue

        Parameters
        ----------
        ctx:commands.Context
            Discord context

        Returns
        -------
        None
        '''
        self.music_queue[ctx.guild.id] = []
        await ctx.send("Queue is clear.")

    @queue.command()
    async def next(self, ctx:commands.Context) -> None:
        # Remove current track
        self.music_queue[ctx.guild.id].pop(0)

        if len(self.music_queue[ctx.guild.id]) > 0:
            # Grab next song
            self.current_song = self.music_queue[ctx.guild.id][0]
            await self.play(ctx, self.current_song.get_url(), )
        else:
            ctx.voice_client.stop()
            return None

    def queue_after_func(self, ctx:commands.Context) -> None:
        # Remove current track
        self.music_queue[ctx.guild.id].pop(0)

        if len(self.music_queue[ctx.guild.id]) > 0:
            # Grab next song
            self.current_song = self.music_queue[ctx.guild.id][0]
            self.play(ctx, self.current_song.get_url())
        else:
            ctx.voice_client.stop()
            return None

    def create_guild_queue(self, guild_id:int) -> None:
        self.music_queue[guild_id] = []
        return None

    def get_video_info(self, url:str) -> str:
        '''
        Get FFMPEG URL link from youtube. Uses the video URL to download 
        the information.

        ** To be used when URL is known.

        Parameters
        ----------
        URL : str
            The URL of the video to extract the audio
        
        Returns
        -------
        str
            The FFMPEG audio URL from youtube
        '''
        ydl = youtube_dl.YoutubeDL(YDL_OPTIONS)
        info = ydl.extract_info(url, download=False)
        #url2 = info['formats'][0]['url']
        del ydl
        return (info)

    def search_url(self, query:str) -> str:
        '''
        Searches a video based on the query passed by the user.
        Returns the URL of the first video that appears on the youtube search.

        Parameters
        ----------
        query : str
            The query to search on youtube
        
        Returns
        -------
        str
            The video URL found
        '''
        search_url = f"https://www.youtube.com/results?search_query={query}"
        req = requests.get(search_url)
        http_text = req.text

        # Find video url in http
        idx = http_text.find('watch?v')
        video_url = ""

        while True:
            char = http_text[idx]
            if (char == '"'):
                break
            video_url += char
            idx += 1

        video_url = f"https://www.youtube.com/{video_url}"
        return (video_url)