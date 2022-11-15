"""
Copyright (c) 2019 Valentin B.
A simple music bot written in discord.py using youtube-dl.
Though it's a simple example, music bots are complex and require much time and knowledge until they work perfectly.
Use this as an example or a base for your own bot and extend it as you want. If there are any bugs, please let me know.
Requirements:
Python 3.5+
pip install -U discord.py pynacl youtube-dl
You also need FFmpeg in your PATH environment variable or the FFmpeg.exe binary in your bot's directory on Windows.
"""

import asyncio
from datetime import datetime, timedelta
import functools
import itertools
import math
from multiprocessing import context
from pickle import FALSE
import random
from sqlite3 import Timestamp
import requests
import secret
from discord_components import *
import time


import discord
import youtube_dl
from async_timeout import timeout
from discord.ext import commands

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.video_id = data.get('id')
        self.uploader = data.get('uploader')
        self.uploader_id = data.get('uploader_id')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = parse_duration(int(data.get('duration')))
        self.duration_int = int(data.get('duration'))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('找不到任何結果 -> `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('找不到任何結果 -> `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    


class Song:
    #__slots__ = ('source', 'requester','mode')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester
        self.mode = 'play'
        self.mode_changer = None

    def create_embed(self):
        mode=self.mode
        embed = (discord.Embed(
                            title='{0.source.title}'.format(self),
                            url='{0.source.url}'.format(self),
                            #description='[**{0.source.uploader}**]({0.source.uploader_url})\n'.format(self),
                            #description='\n**{0.source.title}**\n'.format(self),
                            color=discord.Color.green())
                .add_field(name='時長', value=self.source.duration,inline=True)
                .add_field(name='點播者', value=self.requester.name,inline=True)
                #.add_field(name='提供者', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self),inline=True)
                .set_thumbnail(url=self.source.thumbnail))
        
        embed.set_author(
            name=self.source.uploader,
            url=self.source.uploader_url,
            icon_url=id_to_icon(self.source.uploader_id)
            )
        foot_text=''
        
        if mode == 'play':
            embed.set_footer(text='🎵 現正播放 Now Playing 🎵')
        elif mode == 'pause':
            embed.set_footer(text=f'⏸️ 暫停中 Paused ⏸️  -  By {self.mode_changer}')
        elif mode == 'end':
            embed.set_footer(text='↪️ 播放結束 Play Ends ↪️')
        elif mode == 'skip':
            embed.set_footer(text=f'↪️ 已跳過 Skipped ↪️  -  By {self.mode_changer}')
        #embed.set_footer(text=f'{self.requester.name}', icon_url=self.requester.avatar_url)
        #print(id_to_icon(self.source.uploader_id))
        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None # Song
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()
        #self.mode = 'play'
        self.msg = None

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())
        self.member_task = bot.loop.create_task(self.channel_member_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def channel_member_task(self):
        while True:
            await asyncio.sleep(5)
            print('check member')

            try:
                if len(self.voice.channel.members) > 1:
                    continue

                await asyncio.sleep(180) #檢查過了 3分鐘後是不是還是沒人

                if len(self.voice.channel.members) > 1:
                    continue
                
                embed = discord.Embed(title='',description='**沒人要聽傑哥唱歌 傑哥直接睡覺了😭**',color=discord.Color.green())
                await self._ctx.send(embed=embed)
                self.bot.loop.create_task(self.stop())
                return
            except:
                pass
                 #每五秒check一次

    async def audio_player_task(self):
        while True:
            print('in task')
            self.next.clear()
            

            if not self.loop:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    embed = discord.Embed(title='',description='**沒人要聽傑哥唱歌 傑哥直接睡覺了😭**',color=discord.Color.green())
                    await self._ctx.send(embed=embed)
                    return

            
            self.current.source.volume = self._volume
            self.voice.play(self.current.source,after=self.play_next_song)
            
            self.msg = await self.current.source.channel.send('讀取中...')
            await self.msg.edit(
                content='',
                embed=self.current.create_embed(),
                components=[[
                    Button(label='pause', style=ButtonStyle.green),
                    Button(label='skip',style=ButtonStyle.blue)]]
            )

            await asyncio.gather(self.next.wait(), self.button_task())
            # await self.button_task(msg)
            # await self.next.wait()

    
    async def button_task(self):
        
        start = time.perf_counter
        button_label = 'pause'

        while self.current.mode not in 'end skip':

            if not self.voice.is_playing() and self.current.mode!='pause':
                print('loading or exit')#有可能在剛點歌還沒下載好的時候退出
                if time.perf_counter-start >= self.current.source.duration_int:
                    #下載或播放時間超過本身時長的歌自退出
                    self.current.mode='end'
                    break


            try:#若有觸發按鈕
                inter = await self.bot.wait_for('button_click',timeout=0.5)

                if inter.component.label == 'pause':
                    print('pause')
                    self.voice.pause()
                    self.current.mode = 'pause'
                    self.current.mode_changer=inter.author.name

                elif inter.component.label == 'resume':
                    print('resume')
                    self.voice.resume()
                    self.current.mode = 'play'
                elif inter.component.label == 'skip':
                    self.skip(inter.author.name)
                else:
                    continue#避免觸發其他按鈕
                
                try: await inter.respond()
                except: pass

            except:#沒觸發按鈕
                pass

            if button_label=='pause' and self.current.mode=='pause':
                button_label='resume'
                await self.msg.edit(
                    embed=self.current.create_embed(),
                    components=[[
                        Button(label='resume',style=ButtonStyle.green),
                        Button(label='skip',style=ButtonStyle.blue)]]
                )
            elif button_label=='resume' and self.current.mode=='play':
                button_label='pause'
                await self.msg.edit(
                    embed=self.current.create_embed(),
                    components=[[
                        Button(label='pause', style=ButtonStyle.green),
                        Button(label='skip',style=ButtonStyle.blue)]]
                )

        print('leave')#自然播放結束
        
        await self.msg.edit(
            embed=self.current.create_embed(),
            components=[]
        )
            

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))
        # if self._loop
        #     queue.puts=self.current.source

        self.next.set()

    def skip(self,name:str):
        #self.skip_votes.clear()

        self.current.mode='skip'
        self.current.mode_changer=name

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()
        self.current.mode='end'
        if self.voice:
            await self.voice.disconnect()
            self.voice = None

#傳入client
class Music(commands.Cog):
    def __init__(self, bot: commands.Bot): # bot = 我們的client
        self.bot = bot
        self.voice_states = {} #存放各伺服器的語音狀態

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        
        #找不到此伺服器狀態，則新增一個
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    # async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
    #     await ctx.send('***我看你完全是不懂哦: {}***'.format(str(error)))

    @commands.command(name='join', invoke_without_subcommand=True, aliases=['connect','加入','j','J','c'])
    async def _join(self, ctx: commands.Context):
        """Joins a voice channel."""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    # @commands.command(name='summon')
    # @commands.has_permissions(manage_guild=True)
    # async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
    #     """Summons the bot to a voice channel.
    #     If no channel was specified, it joins your channel.
    #     """
    #
    #     if not channel and not ctx.author.voice:
    #         raise VoiceError('You are neither connected to a voice channel nor specified a channel to join.')
    #
    #     destination = channel or ctx.author.voice.channel
    #     if ctx.voice_state.voice:
    #         await ctx.voice_state.voice.move_to(destination)
    #         return
    #
    #     ctx.voice_state.voice = await destination.connect()


    @commands.command(name='leave', aliases=['disconnect','l','L','離開'])
    #@commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx: commands.Context):
        """Clears the queue and leaves the voice channel."""

        if not ctx.voice_state.voice:
            #return await ctx.send('***不在任何語音頻道中***')
            embed = discord.Embed(title='',description='**傑哥不在任何語音頻道中**',color=discord.Color.green())
            return await ctx.send(embed=embed)

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    # @commands.command(name='volume')
    # async def _volume(self, ctx: commands.Context, *, volume: int):
    #     """Sets the volume of the player."""
    #
    #     if not ctx.voice_state.is_playing:
    #         return await ctx.send('Nothing being played at the moment.')
    #
    #     if 0 > volume > 100:
    #         return await ctx.send('Volume must be between 0 and 100')
    #
    #     ctx.voice_state.volume = volume / 100
    #     await ctx.send('Volume of the player set to {}%'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing'])
    async def _now(self, ctx: commands.Context):
        """Displays the currently playing song."""

        #await ctx.send(embed=ctx.voice_state.current.create_embed())
        await ctx.voice_state.msg.delete()
        ctx.voice_state.msg = await ctx.send('now playing...')
        await ctx.voice_state.msg.edit(
            content='',
            embed=ctx.voice_state.current.create_embed(),
            components=[[
                Button(label='pause', style=ButtonStyle.green),
                Button(label='skip',style=ButtonStyle.blue)]]
        )

    @commands.command(name='pause',aliases=['暫停','ps'])
    #@commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """Pauses the currently playing song."""

        #if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
        if ctx.voice_state.current.mode=='play':
            ctx.voice_state.voice.pause()
            ctx.voice_state.current.mode='pause'
            await ctx.message.add_reaction('⏸️')

    @commands.command(name='resume',aliases=['rs'])
    #@commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        """Resumes a currently paused song."""

        #if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
        if ctx.voice_state.current.mode=='pause':
            ctx.voice_state.voice.resume()
            ctx.voice_state.current.mode='play'
            await ctx.message.add_reaction('▶️')

    @commands.command(name='stop',aliases=['停止','st','ST'])
    #@commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx: commands.Context):
        """Stops playing song and clears the queue."""

        ctx.voice_state.songs.clear()
        
        #if ctx.voice_state.is_playing:
        if ctx.voice_state.current.mode!='end':
            ctx.voice_state.current.mode='end'
            ctx.voice_state.voice.stop()
        
        await ctx.message.add_reaction('⏹')

    @commands.command(name='skip',aliases=['跳過','sk','SK'])
    async def _skip(self, ctx: commands.Context):
        """Vote to skip a song. The requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        if ctx.voice_state.current.mode=='end':
            embed = discord.Embed(title='',description='**無歌曲播放中**',color=discord.Color.green())
            return await ctx.send(embed=embed)

        await ctx.message.add_reaction('⏭')
        #ctx.voice_state.current.mode='end'
        ctx.voice_state.skip(ctx.author.name)
        
        '''
        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
            else:
                await ctx.send('Skip vote added, currently at **{}/3**'.format(total_votes))

        else:
            await ctx.send('You have already voted to skip this song.')
        '''

    @commands.command(name='queue',aliases=['Q','q','清單','歌單'])
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """Shows the player's queue.
        You can optionally specify the page to show. Each page contains 10 elements.
        """

        #await ctx.send(embed=ctx.voice_state.current.create_embed())

        #if not ctx.voice_state.is_playing or not ctx.voice_state.voice.is_playing:
        if ctx.voice_state.current.mode=='end':
            embed = discord.Embed(title='',description='**無歌曲播放中**',color=discord.Color.green())
            return await ctx.send(embed=embed)

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''

        #剩餘所需時間
        sum=0
        for song in ctx.voice_state.songs:
            sum += song.source.duration_int

        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        if len(ctx.voice_state.songs) == 0:
            queue='`0.` [**無待播歌曲**]({})\n'.format('https://youtu.be/072tU1tamd0')

        if pages==0: page=0

        embed = (discord.Embed(
                #title='播放清單  -  {}'.format(ctx.guild.name),
                color=discord.Color.green())
                .add_field(name='現正播放：',value='[`▶️` **{0.source.title}**]({0.source.url})'.format(ctx.voice_state.current),inline=False)
                .add_field(name='待播清單：',value=queue)
                .set_footer(text='{0} / {1} 頁  -  {2} 首待播  -  共 {3}'.format(page, pages,len(ctx.voice_state.songs),parse_duration(sum))))
        embed.set_author(name='播放清單  -  {}'.format(ctx.guild.name),icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)
        

    @commands.command(name='shuffle',aliases=['打散','隨機','sf'])
    async def _shuffle(self, ctx: commands.Context):
        """Shuffles the queue."""

        if len(ctx.voice_state.songs) == 0:
            embed = discord.Embed(title='',description='**目前無待播歌曲**',color=discord.Color.green())
            return await ctx.send(embed=embed)

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('🔀')

    @commands.command(name='remove',aliases=['RM','rm','刪除','移除','DEL','del','delete','dl'])
    async def _remove(self, ctx: commands.Context, index: int):
        """Removes a song from the queue at a given index."""

        if len(ctx.voice_state.songs) == 0:
            embed = discord.Embed(title='',description='**目前無待播歌曲**',color=discord.Color.green())
            return await ctx.send(embed=embed)

        embed = discord.Embed(title='',
            description='**刪除成功** ✅ **{}**'.format(ctx.voice_state.songs[index-1].source.title),
            color=discord.Color.green())
        await ctx.send(embed=embed)
        ctx.voice_state.songs.remove(index - 1)
        #await ctx.message.add_reaction('✅')

    @commands.command(name='loop',aliases=['循環','lp','LP','LOOP'])
    async def _loop(self, ctx: commands.Context):
        """Loops the currently playing song.
        Invoke this command again to unloop the song.
        """

        #if not ctx.voice_state.is_playing:
        if ctx.voice_state.current.mode=='end':
            embed = discord.Embed(title='',description='**無歌曲播放中**',color=discord.Color.green())
            return await ctx.send(embed=embed)

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction('✅')

    @commands.command(name='play',aliases=['p','P','PLAY','ADD','播放','add'])
    async def _play(self, ctx: commands.Context, *, search: str):
        """Plays a song.
        If there are songs in the queue, this will be queued until the
        other songs finished playing.
        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """

        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
                
            else:
                song = Song(source)

                await ctx.voice_state.songs.put(song)
                #await ctx.send('**加入成功**✅ **{}**'.format(song.source.title))
                embed = discord.Embed(title='',
                    description='**加入成功** ✅ **{}**'.format(song.source.title),
                    color=discord.Color.green())
                return await ctx.send(embed=embed)



    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            #await ctx.send('***我家很大 歡迎你們來我家點歌***')
            embed = discord.Embed(title='',description='**我家很大 歡迎你們來我家點歌 😏**',
                    color=discord.Color.green())
            return await ctx.send(embed=embed)

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                embed = discord.Embed(title='',description='**傑哥正從便利商店趕過來 ☺️**',
                    color=discord.Color.green())
                return await ctx.send(embed=embed)



def parse_duration(duration: int):
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    duration = []
    if days > 0:
        duration.append('{0:02d}'.format(days))
    if hours > 0:
        duration.append('{0:02d}'.format(hours))
    if minutes >= 0:
        duration.append('{0:02d}'.format(minutes))
    if seconds >= 0:
        duration.append('{0:02d}'.format(seconds))

    return ':'.join(duration)

def id_to_icon(ID):
    """組合 URL 後 GET 網頁並轉換成 JSON"""
    api_url = f"https://youtube.googleapis.com/youtube/v3/channels?part=snippet&id={ID}&key={secret.YT_API_KEY}"
    response = requests.get(api_url)
    data=response.json()

    if data['pageInfo']['totalResults'] == 0:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=snippet&forUsername={ID}&key={secret.YT_API_KEY}"
        response = requests.get(url)
        data=response.json()
    
    return (data['items'][0]['snippet']['thumbnails']['default']['url'])


def setup(bot):
    # 使用 cogs.setup(client) 會發生的事
    bot.add_cog(Music(bot))
    DiscordComponents(bot)




    