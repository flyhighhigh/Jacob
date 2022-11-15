"""
@flyhighhigh_vc 2022
"""

import asyncio
import functools
import itertools
import math
import random
from tabnanny import check
import requests
import secret
from discord_components import *
import time
import json
import urllib3

import discord
import youtube_dl
from async_timeout import timeout
from discord.ext import commands
from googlesearch import search
from bs4 import BeautifulSoup

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''

headers = {'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

voice_states = {} #存放各伺服器的語音狀態

labels = {# 輸入英文 回傳中文
    'pause' :'⏸️pause',
    'resume':'▶️resume',
    'skip'  :'⏭️skip',
    'stop'  :'⏹️stop',
    'kill_lyrics':'⛔關閉歌詞'
}

class embeds:
    def timeout_memberless():
        return discord.Embed(title='',description='**沒人要聽傑哥唱歌 傑哥直接睡覺了😭**',color=0xf93a2f)

    def timeout_songless():
        return discord.Embed(title='',description='**沒人要點歌 傑哥直接睡覺了 😭**',color=0xf93a2f)

    def player_init():
        return discord.Embed(title='',description='**播放器準備中**',color=0xf8c300)
    
    def cant_find_lyrics():
        return discord.Embed(title='',description='**傑哥沒有這首歌的歌詞  😢**',color=0xf8c300)
    
    def finding_lyrics():
        return discord.Embed(title='',description='**歌詞搜尋中**',color=0xf8c300)

    def no_song_playing():
        return discord.Embed(title='',description='**無歌曲播放中 🤐**',color=0xf93a2f)

    def no_song_queuing():
        return discord.Embed(title='',description='**目前無待播歌曲**',color=0xf93a2f)
    
    def del_index_error():
        return discord.Embed(title='',description='**選項超過待播清單範圍**',color=0xf93a2f)

    def bot_not_in_voice():
        return discord.Embed(title='',description='**傑哥不在任何語音頻道中**',color=0xf93a2f)

    def author_not_in_voice():
        return discord.Embed(title='',description='**我家很大 歡迎你們來我家點歌 😏**',color=0xf93a2f)
    
    def loading_error():
        return discord.Embed(title='',description='**歌曲載入失敗 重試中 幫我撐10秒 ⚔️ (可能自動跳過) **',color=0xf93a2f)
    
    def success_del(string:str):
        return discord.Embed(title='',
            description=f'**刪除成功** ✅ **{string}**',
            color=discord.Color.green())
    
    def success_add(ctx: commands.Context,title:str):
        return discord.Embed(title='',
            description=f'**加入成功 ✅ {title} ( By {ctx.author.display_name} )**',
            color=discord.Color.green())
    
    def success_connect(ctx: commands.Context):
        return discord.Embed(title='',
            description=f'**傑哥來 {ctx.author.voice.channel} 拜訪你們了**',
            color=0xf8c300)
    
    def disconnected(ctx: commands.Context):
        return discord.Embed(title='',
            description=f'**那個 {ctx.author.display_name} 就是遜啦 才聽幾首就不聽了**',
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
        'before_options': '-reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 10',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self,ctx:commands.Context,source:discord.FFmpegPCMAudio,*,data:dict,original_query:str):
        super().__init__(source,volume=0.5)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.mode = 'play'
        self.mode_changer = None
        self.ctx=ctx
        self.data = data

        self.video_id = data.get('id')
        self.uploader = data.get('uploader')
        self.uploader_id = data.get('uploader_id')
        self.uploader_url = data.get('uploader_url')
        self.channel_id = data.get('channel_id') # 用這個不會有自訂義id的問題
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = parse_duration(int(data.get('duration')))
        self.duration_int = int(data.get('duration'))
        self.url = data.get('webpage_url') # youtube頁面的url
        self.stream_url = data.get('url') # 擷取音訊的url
        
        self.icon_url = id_to_icon(self.channel_id)
        self.original_query = original_query

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            print(f'guild = {ctx.guild} | 找不到任何結果 -> `{search}`')
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
                print(f'guild = {ctx.guild} | 找不到任何結果 -> `{search}`')
                return

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)
        # with open("output.json", "w") as f:
        #      json.dump(processed_info, f, indent = 4)

        if processed_info is None:
            print(f'guild = {ctx.guild} | Couldn\'t fetch `{webpage_url}`')
            return

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    print(f'guild = {ctx.guild} | Couldn\'t retrieve any matches for `{webpage_url}`')
                    return

        #return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)
        return cls(ctx, discord.FFmpegPCMAudio(info['url']), data=info,original_query=search)

    

    # #自己改的
    # @classmethod
    # async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
    #     loop = loop or asyncio.get_event_loop()

    #     if search.startswith('https'):
    #         webpage_url=search
    #     else:
    #         results = YoutubeSearch(search_terms=search, max_results=10).to_dict()
    #         print(results[0]['url_suffix'])
    #         print(len(results))
    #         with open("search10.json", "w") as f:
    #             json.dump(results, f, indent = 4)
        
    #         webpage_url = """https://www.youtube.com/""" + results[0]['url_suffix']
        
    
    #     partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
    #     processed_info = await loop.run_in_executor(None, partial)

    #     if processed_info is None:
    #         print('Couldn\'t fetch `{}`'.format(webpage_url))
    #         return

    #     if 'entries' not in processed_info:
    #         info = processed_info
    #     else:
    #         info = None
    #         while info is None:
    #             try:
    #                 info = processed_info['entries'].pop(0)
    #             except IndexError:
    #                 print('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))
    #                 return

    #     return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

        #return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)
        #return cls(ctx, discord.FFmpegPCMAudio(info['url']), data=info)


    


# class SongQueue(asyncio.Queue):
#     def __getitem__(self, item):
#         if isinstance(item, slice):
#             return list(itertools.islice(self._queue, item.start, item.stop, item.step))
#         else:
#             return self._queue[item]

#     def __iter__(self):
#         return self._queue.__iter__()

#     def __len__(self):
#         return self.qsize()

#     def clear(self):
#         self._queue.clear()

#     def shuffle(self):
#         random.shuffle(self._queue)

#     def remove(self, index: int):
#         del self._queue[index]

#-------------------------------------------------------------------------------------

class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    def __init__(self, ctx):
        print(f'guild = {ctx.guild} | init new player')
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog
        self.vc = ctx.voice_client

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.msg = None  # Now playing message
        #self.volume = 0.5
        self.current = None # now playing source (YTDLsource)
        self.killed = False

        self.audio_player = self.bot.loop.create_task(self.player_loop())
        self.player_id = random.randint(0,10000)

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed() and self.killed==False:
            print(f'guild = {self._guild} | in task id:{self.player_id}')
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                if self.killed: break
                print(f'guild = {self._guild} | timeout id:{self.player_id}')
                await self._channel.send(embed=embeds.timeout_songless())
                self.destroy()
                return

            # if not isinstance(source, YTDLSource):
            #     # Source was probably a stream (not downloaded)
            #     # So we should regather to prevent stream expiration
            #     try:
            #         source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
            #     except Exception as e:
            #         await self._channel.send(f'There was an error processing your song.\n'
            #                                  f'```css\n[{e}]\n```')
            #         continue

            #source.volume = self.volume
            self.current = source

            self.vc.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            print(f'guild = {self._guild} | start play {source.title}')

            self.msg = await self.current.channel.send(embed=embeds.player_init())
            await self.msg.edit(
                content='',
                embed=self.create_embed(),
                components=[[
                    Button(label=labels['pause'], style=ButtonStyle.green),
                    Button(label=labels['skip'],style=ButtonStyle.blue)]]
            )
            start_time = time.time()
            await self.bot.loop.create_task(self.button_for_song(start=start_time))
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            #self.current = None

        print(f'guild = {self._guild} | out task id:{self.player_id}')

    async def button_for_song(self,start=time.time()):#每首歌開始會進來

        while self.current.mode not in 'end skip' and self.killed==False:

            if not self.vc.is_playing() and self.current.mode!='pause':
                print(f'guild = {self._guild} | loading or exit')#有可能在剛點歌還沒下載好的時候退出
                through_time = time.time()-start
                print(through_time,'sec',self.current.title)

                if not self.vc.is_connected():#not in voicechannel
                    self.current.mode='end'
                    self.destroy()
                    break

                if self.killed or through_time >= 10:
                    # 下載或播放時間超過10秒(或自身長度)
                    # 且現在沒手動停止卻停止撥放的歌，自動退出
                    try:
                        self.current.mode='end'
                    except: pass
                    break
                else:
                    await self.current.channel.send(embed=embeds.loading_error())
                    print(f'guild = {self._guild} | retrying')
                    self.current=await YTDLSource.create_source(self.current.ctx,self.current.url,loop=self.bot.loop)
                    self.vc.play(self.current, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
                    await asyncio.sleep(5)# 有可能下載太久 所以送他5秒鐘再試一次
                    continue

            try:#若有觸發按鈕
                inter = await self.bot.wait_for('button_click',timeout=1)

                if inter.component.label == labels['pause']:
                    print(f'guild = {self._guild} | pause')
                    self.vc.pause()
                    self.current.mode = 'pause'
                    self.current.mode_changer = inter.author.display_name

                    await self.msg.edit(
                        embed=self.create_embed(),
                        components=[[
                            Button(label=labels['resume'],style=ButtonStyle.green),
                            Button(label=labels['skip'],style=ButtonStyle.blue)]]
                    )

                elif inter.component.label == labels['resume']:
                    print(f'guild = {self._guild} | resume')
                    self.vc.resume()
                    self.current.mode = 'play'

                    await self.msg.edit(
                        embed=self.create_embed(),
                        components=[[
                            Button(label=labels['pause'], style=ButtonStyle.green),
                            Button(label=labels['skip'],style=ButtonStyle.blue)]]
                    )
                    
                elif inter.component.label == labels['skip']:
                    print(f'guild = {self._guild} | skip')
                    self.vc.stop()
                    self.current.mode = 'skip'
                    self.current.mode_changer = inter.author.display_name

                else:
                    continue#避免觸發其他按鈕
                
                try: await inter.respond()
                except: pass

            except:#沒觸發按鈕
                pass


        print(f'guild = {self._guild} | leave song (button ends)')#自然播放結束
        try:
            if self.current.mode!='skip': self.current.mode='end'
        except:
            pass

        await self.msg.edit(
            embed=self.create_embed(self.current),
            components=[]
        )
        self.current=None
    
    def create_embed(self,source=None):
        if source==None:
            source=self.current

        mode=source.mode
        embed = (discord.Embed(
                    title=f'{source.title}',
                    url=f'{source.url}',
                    color=discord.Color.green())
                .add_field(name='時長', value=source.duration,inline=True)
                .add_field(name='點播者', value=source.requester.display_name,inline=True)
                .set_thumbnail(url=source.thumbnail))
        
        embed.set_author(
            name=source.uploader,
            url=source.uploader_url,
            icon_url=source.icon_url
            )
        
        if mode == 'play':
            embed.set_footer(text='🎵 現正播放 Now Playing 🎵')
        elif mode == 'pause':
            embed.set_footer(text=f'⏸️ 暫停中 Paused ⏸️  -  By {source.mode_changer}')
        elif mode == 'end':
            embed.set_footer(text='↪️ 播放結束 Play Ends ↪️')
        elif mode == 'skip':
            embed.set_footer(text=f'↪️ 已跳過 Skipped ↪️  -  By {source.mode_changer}')
        #embed.set_footer(text=f'{self.requester.name}', icon_url=self.requester.avatar_url)
        #print(id_to_icon(self.source.uploader_id))
        return embed

    def destroy(self):
        """Disconnect and cleanup the player."""
        print(f'guild = {self._guild} | destroying player')
        return self.bot.loop.create_task(self._cog.cleanup(self._guild.id))


#傳入client
class Music(commands.Cog):
    global voice_states

    def __init__(self, bot: commands.Bot): # bot = 我們的client
        self.bot = bot
        self.players = {}
    
    async def cleanup(self, guild_id):
        # try:
        #     await guild.voice_client.disconnect()
        # except AttributeError:
        #     print('467')

        try:
            player = self.get_player(add=False,guildid=guild_id)
            player.killed = True
            guild = player._guild
            await player.vc.disconnect()
        except:
            print('486')

        try:
            del self.players[guild_id]
        except KeyError:
            print('491')
        
        print(f'guild = {guild} | finish clean')
    
    def get_player(self, ctx=None ,add=True, guildid=None):# add=是否要產生一個
        """Retrieve the guild player, or generate one."""
        if not guildid:
            guildid=ctx.guild.id

        try:# find guild player
            player = self.players[guildid]
        except:# generate
            if add:
                player = MusicPlayer(ctx)
                self.players[guildid] = player
            else:
                return None

        return player
    
    def cog_unload(self):
        for guildid in self.players.keys():
            self.bot.loop.create_task(self.cleanup(guildid))

    @commands.command(name='join',aliases=['connect','加入','j','J','cn'])
    async def _join(self, ctx: commands.Context):
        """加入使用者所在語音頻道"""

        # 訊息發送者不在任何語音頻道內，則直接退出
        try:
            destination = ctx.author.voice.channel
        except:
            await ctx.send(embed=embeds.author_not_in_voice())
            return False # 加入失敗
        
        vc = ctx.voice_client
        
        if vc:# 機器人原本有進語音
            if vc.channel == ctx.author.voice.channel:
                return True
            # 若機器人在其他頻道，則呼叫過來 (todo 發送確認按鈕)
            else:
                await vc.move_to(destination)
                await ctx.send(embed=embeds.success_connect(ctx))
                
        else:# 機器人原本沒進語音 叫他加入
            await destination.connect()
            await ctx.send(embed=embeds.success_connect(ctx))
            
        return True #加入成功
    

    @commands.command(name='play',aliases=['p','P','PLAY','ADD','播放','add'])
    async def _play(self, ctx: commands.Context, *, search: str):
        """播放歌曲"""

        if await self._join(ctx) == False:
            return
        
        vc = ctx.voice_client

        async with ctx.typing():
            try:
                player = self.get_player(ctx,add=True) #尋找此伺服器是否有player 若沒有則新增
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)

                await player.queue.put(source)
                try: title = source.title # 不用regather的方式
                except: title = source['title'] # 等等撥放時還要regather 此時只回傳一個dict

                await ctx.send(embed=embeds.success_add(ctx,title))
            except:
                return await ctx.send(f'An error occurred while processing this request: {search}')

        # 刪除指令
        # try:
        #     await ctx.message.delete()
        # except: pass

    @commands.command(name='leave', aliases=['disconnect','l','L','離開','dc','lv'])
    async def _leave(self, ctx: commands.Context):
        """離開語音頻道"""

        vc = ctx.voice_client

        if vc:
            await ctx.send(embed=embeds.disconnected(ctx))
            await self.cleanup(ctx.guild.id)
        else:
            await ctx.send(embed=embeds.bot_not_in_voice())
    
    @commands.command(name='refresh', aliases=['rf', 'player','now','RF','np','刷新'])
    async def _refresh_player_msg(self, ctx: commands.Context):
        '''顯示目前播放的歌曲'''
        player = self.get_player(ctx,add=False)

        if not player:# 沒有player 
            return await ctx.send(embed=embeds.no_song_playing())
        if not player.current:# 有player 但最後一首歌已經結束或跳過
            return await ctx.send(embed=embeds.no_song_playing())
        
        # 有player 且正在播放或暫停
        if player.msg:
            await player.msg.delete()
        
        player.msg = await ctx.send(
            content='',
            embed=player.create_embed(),
            components=[[
                Button(label=labelmodes(player.current.mode), style=ButtonStyle.green),
                Button(label=labels['skip'],style=ButtonStyle.blue)]]
        )
    
    @commands.command(name='lyrics', aliases=['ly','lr','歌詞'])
    async def _lyrics(self,ctx:commands.Context, *, query: str =''):
        '''到魔鏡歌詞網尋找歌詞'''
        await ctx.trigger_typing()

        if not query:
            keyin=False
            player = self.get_player(ctx,add=False)
            if not player:# 沒有player 
                return await ctx.send(embed=embeds.no_song_playing())
            if not player.current:# 有player 但最後一首歌已經結束或跳過
                return await ctx.send(embed=embeds.no_song_playing())
            query = player.current.title
            newqry = player.current.original_query+' mojim.com'
        else:
            keyin=True

        query +=' mojim.com'
        
        lyric_msg = await ctx.send(embed=embeds.finding_lyrics())

        def mojim(query):
            for url in search(query, stop=5, pause=2.0):
                if url.startswith('https://mojim.com/twy'):
                    return url
            return None
        
        result = mojim(query)# 用影片標題找
        print(f'guild = {ctx.guild} | 1',result)
        if not result:# 沒找到網址
            if not keyin:# 用使用者play指令輸入的找 若搜尋是由使用者輸入 就不找了
                result = mojim(newqry)
            print(f'guild = {ctx.guild} | 2',result)
            if not result:
                return await lyric_msg.edit(embed=embeds.cant_find_lyrics())

        try:
            # 找到魔鏡歌詞網的編輯功能
            url = result.replace('https://mojim.com/twy','https://mojim.com/twthx')
            url = url.replace('.htm','x1.htm')
            # print('url',url)

            html = requests.get(url,headers=headers)
            soup = BeautifulSoup(html.text, 'html.parser')
            text = str(soup.find('textarea',id='aaa_d'))
            
            # 若搜尋是使用現在播放的歌曲 並沒有增加準確度...
            # if not keyin:
            #     songstart=text.find('【')
            #     songstart=text.find('【',songstart+1)
            #     songend=text.find('】',songstart+1)
            #     song_title=text[songstart+1:songend]
            #     if song_title not in query:# 且歌名不在影片標題中 則視為出錯
            #         print(f'{song_title} not in {query}')
            #         raise
                
            start=text.find('>')
            end=text.find('\n',start+1)

            title=text[start:end].replace('>修改 ','')
            lyrics=text[end:].replace('</textarea>','')

            while True:# 刪除動態歌詞
                start = lyrics.find("[")
                end = lyrics.find("\n",start+1)
                if start==-1 or end==-1:
                    break
                lyrics=lyrics.replace(lyrics[start:end+1],'')

            while True:# 刪除前後換行
                if lyrics.startswith('\n'):
                    lyrics=lyrics[1:]
                elif lyrics.endswith('\n'):
                    lyrics=lyrics[:-1]
                else:
                    break

            embed=discord.Embed(title='',description=lyrics,color=discord.Color.blue())
            embed.set_author(name=title,url=result)
            button_id=str(random.randint(0,10000))
            print(f'guild = {ctx.guild} | send lyrics id:{button_id}')
            await lyric_msg.edit(embed=embed,components=[[
                Button(label=labels['kill_lyrics'],style=ButtonStyle.gray,custom_id=button_id)]])
            
            while True:
                try:# 有收到kill按鈕訊號
                    inter = await self.bot.wait_for('button_click',
                        timeout=120,
                        check=lambda i:i.component.label==labels['kill_lyrics']\
                            and i.component.custom_id==button_id)

                    #if inter.component.label == labels['kill_lyrics']:
                    print(f'guild = {ctx.guild} | kill lyrics id:{button_id}')
                    await lyric_msg.delete()
                    try: await inter.respond()
                    except: pass
                    break
                except:# timeout
                    await lyric_msg.edit(embed=embed,components=[])
        except:
            return await lyric_msg.edit(embed=embeds.cant_find_lyrics())


    @commands.command(name='pause',aliases=['ps','PS','暫停','Pause'])
    async def _pause(self, ctx: commands.Context):
        '''暫停播放歌曲'''
        vc = ctx.voice_client
        player = self.get_player(ctx,add=False)

        if not player:# 沒有player 
            return await ctx.send(embed=embeds.no_song_playing())
        if not player.current:# 有player 但最後一首歌已經結束或跳過
            return await ctx.send(embed=embeds.no_song_playing())

        #有player且播放中或暫停中
        if player.current.mode=='pause':return
        print(f'guild = {ctx.guild} | pause')
        vc.pause()
        player.current.mode = 'pause'
        player.current.mode_changer = ctx.author.display_name

        await player.msg.edit(
            embed=player.create_embed(),
            components=[[
                Button(label=labels['resume'],style=ButtonStyle.green),
                Button(label=labels['skip'],style=ButtonStyle.blue)]]
        )
        #await ctx.send("Paused ⏸️")
        await ctx.message.add_reaction('✅')
    
    @commands.command(name='resume',aliases=['rs','RS','繼續','Resume','re'])
    async def _resume(self, ctx: commands.Context):
        '''繼續播放歌曲'''
        
        vc = ctx.voice_client
        player = self.get_player(ctx,add=False)

        if not player:# 沒有player 
            return await ctx.send(embed=embeds.no_song_playing())
        if not player.current:# 有player 但最後一首歌已經結束或跳過
            return await ctx.send(embed=embeds.no_song_playing())

        #有player且播放中或暫停中
        if player.current.mode=='play':return
        print(f'guild = {ctx.guild} | resume')
        vc.resume()
        player.current.mode = 'play'

        await player.msg.edit(
            embed=player.create_embed(),
            components=[[
                Button(label=labels['pause'], style=ButtonStyle.green),
                Button(label=labels['skip'],style=ButtonStyle.blue)]]
        )
        await ctx.message.add_reaction('✅')
    

    @commands.command(name='skip',aliases=['sk','SK','Skip','跳過'])
    async def _skip(self, ctx:commands.Context):
        '''跳過這首歌曲'''
        
        vc = ctx.voice_client
        player = self.get_player(ctx,add=False)

        if not player:# 沒有player 
            return await ctx.send(embed=embeds.no_song_playing())
        if not player.current:# 有player 但最後一首歌已經結束或跳過
            return await ctx.send(embed=embeds.no_song_playing())

        print(f'guild = {ctx.guild} | skip')

        vc.stop()
        player.current.mode = 'skip'
        player.current.mode_changer = ctx.author.display_name
        await ctx.message.add_reaction('✅')


    @commands.command(name='queue',aliases=['Q','q','清單','歌單','Queue'])
    async def _queue(self, ctx: commands.Context):
        '''顯示待播清單'''

        #if not ctx.voice_state.is_playing or not ctx.voice_state.voice.is_playing:
        page = 1
        player = self.get_player(ctx,add=False)

        if not player:# 沒有player 
            return await ctx.send(embed=embeds.no_song_queuing())
        if not player.current:# 有player 但最後一首歌已經結束或跳過
            return await ctx.send(embed=embeds.no_song_queuing())

        items_per_page = 10
        pages = math.ceil(player.queue.qsize() / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page
        if end > player.queue.qsize(): end = player.queue.qsize()

        queue = ''

        #剩餘所需時間
        sum=0
        for song in player.queue._queue:# asyncio.queue要用 ._queue才能當作List
            sum += song.duration_int
            
        for i in range(start,end):
            queue += '`{0}.` [**{1.title}**]({1.url})\n'.format(i+1,player.queue._queue[i])

        if player.queue.qsize() == 0:
            queue='`0.` [**無待播歌曲**]({})\n'.format('https://youtu.be/dQw4w9WgXcQ')

        if pages==0: page=0 # 避免page=1 pages=0 的情況，看起來很怪

        embed = (discord.Embed(
                #title='播放清單  -  {}'.format(ctx.guild.name),
                color=discord.Color.green())
                .add_field(name='現正播放：',value='[`▶️` **{0.title}**]({0.url})'.format(player.current),inline=False)
                .add_field(name='待播清單：',value=queue))
        embed.set_author(name='播放清單  -  {}'.format(ctx.guild.name),icon_url=ctx.guild.icon_url)
        embed.set_footer(text='{0} / {1} 頁  -  {2} 首待播  -  共 {3}'.format(page,pages,player.queue.qsize(),parse_duration(sum)))
        await ctx.send(embed=embed)


    @commands.command(name='remove',aliases=['RM','rm','刪除','移除','DEL','del','delete','dl'])
    async def _remove(self, ctx: commands.Context, index: int):
        '''刪除待播歌曲'''

        player = self.get_player(ctx,add=False)

        if not player:# 沒有player 
            return await ctx.send(embed=embeds.no_song_queuing())
        if index == 0:# rm 0 自動轉譯成 skip，至於現在有沒有歌曲可以跳過就交給skip去確認
            return await self._skip(ctx)
        if player.queue.qsize()==0:# 有player 但沒有任何待播
            return await ctx.send(embed=embeds.no_song_queuing())
        if index > player.queue.qsize():
            await ctx.send(embed=embeds.del_index_error())

        await ctx.send(embed=embeds.success_del(player.queue._queue[index-1].title))
        del player.queue._queue[index-1]
        #await ctx.message.add_reaction('✅')

    @commands.command(name='shuffle',aliases=['打散','隨機','sf','sh'])
    async def _shuffle(self, ctx: commands.Context):
        '''打散待播清單'''
        
        player = self.get_player(ctx,add=False)

        if not player:# 沒有player 
            return await ctx.send(embed=embeds.no_song_queuing())
        if player.queue.qsize()==0:# 有player 但沒有任何待播
            return await ctx.send(embed=embeds.no_song_queuing())

        random.shuffle(player.queue._queue)
        await ctx.message.add_reaction('🔀')

#-------------------------------------------------------------------------------

def labelmodes(mode):
    if mode=='pause':
        return labels['resume']
    if mode=='play':
        return labels['pause']

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
        return 'https://www.freeiconspng.com/thumbs/error-icon/error-icon-4.png'
        # 若找不到則用username再找一次
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=snippet&forUsername={ID}&key={secret.YT_API_KEY}"
        response = requests.get(url)
        data=response.json()
    
    return (data['items'][0]['snippet']['thumbnails']['default']['url'])


def check_url(url):
    try:
        urllib3.urlopen(url)
        return True
    except:
        return False

def setup(bot):
    # 使用 cogs.setup(client) 會發生的事
    bot.add_cog(Music(bot))
    DiscordComponents(bot)





    