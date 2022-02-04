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
import functools
import itertools
import math
import random
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

voice_states = {} #存放各伺服器的語音狀態
labels = {
    'pause':'resume',
    'play':'pause',
}

class embeds:
    def timeout_memberless():
        return discord.Embed(title='',description='**沒人要聽傑哥唱歌 傑哥直接睡覺了😭**',color=0xf93a2f)

    def timeout_songless():
        return discord.Embed(title='',description='**沒人要點歌 傑哥直接睡覺了 😭**',color=0xf93a2f)

    def player_init():
        return discord.Embed(title='',description='**播放器準備中**',color=0xf8c300)

    def no_song_playing():
        return discord.Embed(title='',description='**無歌曲播放中 🤐**',color=0xf93a2f)

    def no_song_queuing():
        return discord.Embed(title='',description='**目前無待播歌曲**',color=0xf93a2f)

    def bot_not_in_voice():
        return discord.Embed(title='',description='**傑哥不在任何語音頻道中**',color=0xf93a2f)

    def author_not_in_voice():
        return discord.Embed(title='',description='**我家很大 歡迎你們來我家點歌 😏**',color=0xf93a2f)
    
    def success_del(string:str):
        return discord.Embed(title='',
            description=f'**刪除成功** ✅ **{string}**',
            color=discord.Color.green())
    
    def success_add(ctx: commands.Context,title:str):
        return discord.Embed(title='',
            description=f'**加入成功 ✅ {title} ( By {ctx.author.name} )**',
            color=discord.Color.green())
    
    def success_connect(ctx: commands.Context):
        return discord.Embed(title='',
            description=f'**傑哥來 {ctx.author.voice.channel} 拜訪你們了**',
            color=0xf8c300)

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
        self.icon_url = id_to_icon(self.uploader_id)

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            print('找不到任何結果 -> `{}`'.format(search))
            return

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                print('找不到任何結果 -> `{}`'.format(search))
                return

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            print('Couldn\'t fetch `{}`'.format(webpage_url))
            return

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    print('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))
                    return

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)


class Song:
    #__slots__ = ('source', 'requester','mode')

    def __init__(self,ctx: commands.context,source: YTDLSource):
        self.source = source
        self.requester = source.requester
        self.mode = 'play'
        self.mode_changer = None
        self.ctx=ctx

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
            icon_url=self.source.icon_url
            )
        
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
        self.loop_cnt = 0

        self.looping = False
        self.volume = 0.5
        self.killed = False
        #self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())
        self.member_task = bot.loop.create_task(self.check_members())

    def __del__(self):
        self.audio_player.cancel()
        self.member_task.cancel()

    @property
    def loop(self):
        return self.looping

    @loop.setter
    def loop(self, value: bool):
        self.looping = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def check_members(self):
        while not self.killed:
            await asyncio.sleep(5)
            print('check member')

            try:
                if len(self.voice.channel.members) > 1:
                    print('=',len(self.voice.channel.members))
                    continue
                
                #在機器人上線之前上語音頻道的人不會被算進 member
                print('waiting member timeout')
                await asyncio.sleep(180) #檢查過了 3分鐘後是不是還是沒人 

                if len(self.voice.channel.members) > 1:
                    continue
                
                print('260 timeout')
                
                if not self.killed:
                    await self._ctx.send(embed=embeds.timeout_memberless())
                    self.bot.loop.create_task(self.kill())
                break
            except:
                pass
                 #每五秒check一次
        print('channel member task ends')

    async def audio_player_task(self):
        while not self.killed:
            print('in player task')
            #self.next.clear()

            if not self.loop:
                try:
                    async with timeout(180):  # 在三分鐘內嘗試get歌曲
                        self.current = await self.songs.get() #把current pop出來
                    print('get song success/pop out from queue')
                except:
                    print('288 timeouting')
                    
                    if not self.killed:
                        await self._ctx.send(embed=embeds.timeout_songless())
                        self.bot.loop.create_task(self.kill())
                    break
            
            if not self.msg:#若把if not這一行註解掉 則msg會每首歌發新的
                #目前這樣則是一直編輯同一個msg
                self.msg = await self.current.ctx.send(embed=embeds.player_init())

            print('qqq')
            self.current.source.volume = self.volume
            #self.voice.play(self.current.source,after=self.play_next_song)

            start_time=time.time()
            self.voice.play(self.current.source,after=self.play_next_song())

            print('330')

            await self.msg.edit(
                content='',
                embed=self.current.create_embed(),
                components=[[
                    Button(label='pause', style=ButtonStyle.green),
                    Button(label='skip',style=ButtonStyle.blue)]]
            )
            print('340')

            #await asyncio.gather(self.next.wait(), self.button_for_song())
            await self.button_for_song(start=start_time) #等到歌曲結束才會回來
            # await self.next.wait()
        print('audio player end')

    async def create_msg(self,ctx=None):
        pass
    
    async def button_for_song(self,start=time.time()):#每首歌開始會進來
        paused_time = 0
        while self.current.mode not in 'end skip':

            if not self.voice.is_playing() and self.current.mode!='pause':
                print('loading or exit')#有可能在剛點歌還沒下載好的時候退出
                through_time = time.time()-start
                print(through_time,'sec',self.current.source.title)

                if  through_time >= 5:
                    #下載或播放時間超過5秒，且現在沒手動停止卻不撥放的歌，自動退出
                    self.current.mode='end'
                    break
                else:
                    await asyncio.sleep(5)# 有可能下載太久 所以送他5秒鐘再試一次
                    continue

            try:#若有觸發按鈕
                inter = await self.bot.wait_for('button_click',timeout=1)

                if inter.component.label == 'pause':
                    print('pause')
                    self.voice.pause()
                    self.current.mode = 'pause'
                    self.current.mode_changer=inter.author.name
                    button_label='resume'
                    await self.msg.edit(
                        embed=self.current.create_embed(),
                        components=[[
                            Button(label='resume',style=ButtonStyle.green),
                            Button(label='skip',style=ButtonStyle.blue)]]
                    )

                elif inter.component.label == 'resume':
                    print('resume')
                    self.voice.resume()
                    self.current.mode = 'play'
                    button_label='pause'
                    await self.msg.edit(
                        embed=self.current.create_embed(),
                        components=[[
                            Button(label='pause', style=ButtonStyle.green),
                            Button(label='skip',style=ButtonStyle.blue)]]
                    )
                    
                elif inter.component.label == 'skip':
                    print('skip')
                    self.skip(inter.author.name)

                else:
                    continue#避免觸發其他按鈕
                
                try: await inter.respond()
                except: pass

            except:#沒觸發按鈕
                pass


        print('leave song')#自然播放結束
        
        await self.msg.edit(
            embed=self.current.create_embed(),
            components=[]
        )
            

    def play_next_song(self, error=None):
        if error:
            print('in play next song',str(error))
            return

        # if self.looping
        #     queue.puts self.current.source
        #     self.loop_cnt += 1

        #self.next.set()

    def skip(self,name:str):
        #self.skip_votes.clear()

        self.current.mode='skip'
        self.current.mode_changer=name

        if self.is_playing:
            self.voice.stop()

    async def kill(self):
        print('killing voice state')
        self.songs.clear()

        self.killed = True

        if self.current:
            self.current.mode = 'end'
        if self.msg:
            await self.msg.edit(
                embed=self.current.create_embed(), #函式
                components=[])
            self.msg = None
        if self.voice:
            await self.voice.disconnect()
            self.voice = None
        
        voice_states.pop(self._ctx.guild.id)
        self.__del__()
        print('voice state killed')


#傳入client
class Music(commands.Cog):
    global voice_states

    def __init__(self, bot: commands.Bot): # bot = 我們的client
        self.bot = bot

    def get_voice_state(self, ctx: commands.Context):
        # 若機器人在傳入之訊息(ctx)的所屬伺服器是有語音狀態的，就設定ctx.voice_state
        # 若沒有則宣告一個新的語音狀態給ctx
        state = voice_states.get(ctx.guild.id)
        
        #找不到此伺服器狀態，則新增一個
        if not state:
            state = VoiceState(self.bot, ctx)
            voice_states[ctx.guild.id] = state

        return state
    
    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    # def cog_unload(self):
    #     for state in voice_states.values():
    #         self.bot.loop.create_task(state.kill())

    # def cog_check(self, ctx: commands.Context):
    #     if not ctx.guild:
    #         raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

    #     return True

    # async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
    #     await ctx.send('***我看你完全是不懂哦: {}***'.format(str(error)))

    @commands.command(name='join',aliases=['connect','加入','j','J','cn'])
    async def _join(self, ctx: commands.Context):
        print('in join')

        # 訊息發送者不在任何語音頻道內，則直接退出
        if not ctx.author.voice or not ctx.author.voice.channel:
            #await ctx.send('***我家很大 歡迎你們來我家點歌***')
            await ctx.send(embed=embeds.author_not_in_voice())
            return False # 加入失敗

        destination = ctx.author.voice.channel
        
        if ctx.voice_state.voice:# 機器人原本有進語音
            # 若機器人在其他頻道，則呼叫過來 (todo 發送確認按鈕)
            if ctx.voice_state.voice.channel != ctx.author.voice.channel:
                await ctx.voice_state.voice.move_to(destination)
                await ctx.send(embed=embeds.success_connect(ctx))

        else:# 機器人原本沒進語音 叫他加入
            ctx.voice_state.voice = await destination.connect()
            await ctx.send(embed=embeds.success_connect(ctx))

        return True #加入成功
    

    @commands.command(name='play',aliases=['p','P','PLAY','ADD','播放','add'])
    async def _play(self, ctx: commands.Context, *, search: str):
        
        if await self._join(ctx) == False:
            return
        
        print('in play (correctly)')

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except:
                return await ctx.send(f'An error occurred while processing this request: {search}')
                
            
            song = Song(ctx,source)

            await ctx.voice_state.songs.put(song)
            await ctx.send(embed=embeds.success_add(ctx,song.source.title))

        # try:
        #     await ctx.message.delete()
        # except: pass


    @commands.command(name='queue',aliases=['Q','q','清單','歌單'])
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """Shows the player's queue.
        You can optionally specify the page to show. Each page contains 10 elements.
        """

        #await ctx.send(embed=ctx.voice_state.current.create_embed())

        #if not ctx.voice_state.is_playing or not ctx.voice_state.voice.is_playing:
        if ctx.voice_state.current.mode=='end':
            return await ctx.send(embed=embeds.no_song_playing())

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


    @commands.command(name='leave', aliases=['disconnect','l','L','離開'])
    #@commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx: commands.Context):
        """Clears the queue and leaves the voice channel."""

        if not ctx.voice_state.voice:
            return await ctx.send(embed=embeds.bot_not_in_voice())

        await ctx.voice_state.kill()

    @commands.command(name='refresh', aliases=['rf', 'player'])
    async def _refresh_player_msg(self, ctx: commands.Context):
        """Displays the currently playing song."""

        #await ctx.send(embed=ctx.voice_state.current.create_embed())
        #await ctx.voice_state.create_msg(ctx)
        
        if ctx.voice_state.msg:#有存在的msg
            await ctx.voice_state.msg.delete()
            if ctx.voice_state.current.mode in 'skip end':
                return await ctx.send(embed=embeds.no_song_playing())
        else:#沒有msg 也就是還沒有播放東西
            return await ctx.send(embed=embeds.no_song_playing())

        # ctx.voie_state.msg = await ctx.send(embed=embeds.player_init())
        # print('609')
        ctx.voice_state.msg = await ctx.send(
            content='',
            embed=ctx.voice_state.current.create_embed(),
            components=[[
                Button(label=labels[ctx.voice_state.current.mode], style=ButtonStyle.green),
                Button(label='skip',style=ButtonStyle.blue)]]
        )


    @commands.command(name='remove',aliases=['RM','rm','刪除','移除','DEL','del','delete','dl'])
    async def _remove(self, ctx: commands.Context, index: int):

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send(embed=embeds.no_song_queuing())

        embed = embeds.success_del(ctx.voice_state.songs[index-1].source.title)
        await ctx.send(embed=embed)
        ctx.voice_state.songs.remove(index - 1)
        #await ctx.message.add_reaction('✅')




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




    