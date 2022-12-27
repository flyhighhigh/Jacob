import discord
from discord import ButtonStyle, Embed
from discord.ui import Select,View,Button
from discord.ext import commands
import random
import typing
import json
import asyncio
from datetime import datetime,timedelta,timezone,date

class Others(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener('on_message')
    async def _jacob(self,message:discord.message.Message):
        #避免讀到自己的訊息
        if message.author == self.bot.user:
            return
        
        cont = message.content
        while True:# 去除<id>
            cont += ' '
            start = cont.find("<")
            end = cont.find(">",start+1)
            if start == -1 or end == -1:
                break
            cont = cont.replace(cont[start:end+1],'')
            
        while True:# 去除http
            start = cont.find("https")
            end = start+1
            while end < len(cont):
                if cont[end].isspace():break
                end += 1
            if start == -1 or end == len(cont):
                break
            cont = cont.replace(cont[start:end+1],'')

        if '69' in cont:
            await message.add_reaction('<:5569:988866562423410718>')
            return
        if '呱' in message.content or '<:Gua:976653931302240366>' in message.content:
            await message.add_reaction('<:Gua:976653931302240366>')
            return
        if '保健室' in message.content or '安妮雅' in message.content:
            await message.add_reaction('<:newanyaexcited:970148976592556092>')
            return
        if '冰冰' in message.content or '今天限定' in message.content or '泡湯' in message.content:
            await message.add_reaction('<:today_only:981863974515666994>')
            return
        if '傑哥' in message.content or '杰哥' in message.content:
            await message.add_reaction('<:JieGu:899329657369940020>')
            return
        if '冰淇淋' in message.content:
            await message.add_reaction('<:BingChiLing:966019859844567080>')
            return
        if '地震' in message.content:
            await message.reply("https://tenor.com/view/%E5%B7%A8%E6%90%A5%E7%91%9E%E6%96%AF-%E5%9C%8B%E5%8B%95-%E7%98%8B%E7%8B%97-league-of-legends-%E6%89%93%E8%83%8E%E5%8F%94%E5%8F%94-gif-13255794")
            # await message.add_reaction('<:wayne2:976652232227422228>')
            return

        
        keys = [
            ['聽話','你幹嘛','哥不要'],  # 0
            ["就是遜", "超勇的", "超會喝"],  # 1
            ["聽你這麼說", "你很勇"],  # 2
            ["看看", "康康"],  # 3
            ["懂什麼", "懂甚麼",'好康','不懂',],  # 4
            ["新遊戲"], #5
            ['玩累',"累了", "睡覺", "晚安", "下線", '睡了','開睡'],  # 6
            ["結實",'發育'], #7
            ['好蒿', '爽爽'],  # 8
            ['好爽','超爽','爽不爽','爽嗎'], # 9
            ['吃飯','晚餐','午餐','早餐','肚子餓','麵包'], # 10
            ['刷牙','倒垃圾'], # 11
            ['加碼','主委','送幸福','下面一位','下一位'], #12
            ['現在開始'], #13
            ['可憐'], #14
            ['早安'], #15
            ['阿姨','不想努力'], #16
            ['鼻樑打歪','打他','揍扁','操飛'], #17
            ['休息', "先下"], #18
            ['很煩','煩躁','好煩','煩欸'], #19
            ['阿阿阿','啊啊啊','開直播'], #20
            ['洗澡','洗個澡']
        ]
        replys = [
            ['聽話 讓我看看 <:LetMeSeeSee:900381954636140574>',"我看你...完全是不懂哦<:RealmOpen:900381919395594301>",f'**{message.author.mention}** 哥 你幹嘛'],  # 0
            ["聽你這麼說...你很勇哦<:RealmOpen:900381919395594301>"],  # 1
            ["開玩笑 我超勇的好不好 超會喝的啦"],  # 2
            ["不要！<:AWeiGanMa:900381934272798740>"],  # 3
            ["你想懂 我房裡有些好康的", "來啦 來看就知道了"],  # 4
            ["什麼新遊戲 比遊戲還刺激"], #5
            ["玩累了...就直接睡覺 沒問題的","我家還滿大的 歡迎你們來我家睡覺",'好啊 沒問題啊 那走啊','都幾歲了 還那麼早睡'],  # 6
            [f'**{message.author.mention}** 哥 你幹嘛'],#7
            [f'**{message.author.mention}** 和我，我們倆要...好蒿爽爽！'],  # 8
            [f'**{message.author.mention}** 爽嗎兄弟<:mr_han_obscene:981863097969016832>'], # 9
            ['我這裡剛好有個麵包 我還不餓 來 請你們吃','我跟 OTING 可以帶你們去costco買些好吃的喔'], #10
            ['好啊 沒問題啊 那走啊'], #11
            ['來 呱哥送幸福 主委加碼','來 幸福好運到 主委加碼'], #12
            ['瘋 狂 送 頭！'], #13
            ['可憐哪～～','https://tenor.com/view/kelian-%E5%8F%AF%E6%86%90-%E5%8F%AF%E6%86%90%E5%93%AA-gif-19126619'], #14
            ['欸...你們好 我叫阿杰 我也常來這裡玩'], #15
            ['阿姨 阿姨洗鐵路～～','阿姨 我不想努力了～～'], #16
            ['一定打你 一定把你鼻樑打歪 <:wayne3:976652202758246440>'], #17
            [f'**{message.author.mention}** 休息一下吧 去看個書好不好'], #18
            ['我才講你兩句你就說我煩 我只希望你好好用功讀書'], #19
            ['啊啊啊 我中了兩槍...','啊啊啊 你們一定要傳承我的精神...','幫我開直播 拿著 照我'], #20
            ['水很重要 量大 浴缸要很大<:mr_han_obscene:981863097969016832>','我談的是大海 你跟我談浴缸？']
        ]
        for i in range(len(keys)):
            for keyword in keys[i]:
                if keyword in message.content:
                    reply = random.choice(replys[i])
                    await message.reply(reply)
                    return

        #將訊息當成command再辨識一遍，不然其他的指令就沒用
        # await self.bot.process_commands(message)

    # @commands.command(name='clear',aliases=['clr'])
    # async def _clear(self,ctx,amount=1):
    #     """清除伺服器訊息"""
    #     await ctx.channel.purge(limit=amount+1)

            
    
    @commands.hybrid_command(name='guodon_模仿國動',description="老子瘋狗的外號他媽的十歲就有阿")
    async def _guodon(self,ctx:commands.Context,amount:typing.Optional[int],member: typing.Optional[discord.Member]):
        """模擬國動"""
        sended = await ctx.send('正在處理中...')

        if not amount:
            amount=1
        if amount>len(don):
            amount=len(don)

        temp = ''
        index = [i for i in range(0,len(don))]

        for i in range(0,amount): 
            new=random.choice(index) #任選一個國動語錄
            if member:
                try: temp += don[new][1].format(member.mention)+'\n'
                except: temp += don[new][0] + '\n'
            else:
                temp += don[new][0] +'\n'

            index.remove(new)

        await sended.edit(content=temp)
    
    @commands.hybrid_command(name='ping_目前延遲',description="查看機器人延遲")
    async def ping(self,ctx:commands.Context):
        """機器人延遲"""
        sended = await ctx.send('正在處理中...')
        await sended.edit(content=f'Current Ping = {round(self.bot.latency*1000)}ms')

    # @commands.hybrid_command(name='get_user_icon',description="使用使用者ID取得頭貼連結")
    # async def get_icon(self,ctx:commands.Context,id:str=''):
    #     """取得頭貼"""
    #     sended = await ctx.send('正在處理中...')
    #     user = 0

    #     if len(id)==0: user = ctx.author
    #     else: user = await self.bot.fetch_user(int(id))

    #     await sended.edit(content=f"使用者頭貼: {user.avatar}\n伺服器頭貼: {user.guild_avatar}")

    #哪時候加入
    # @commands.hybrid_command(name='joined_加入時間',description="查看加入時間")
    # async def joined(self,ctx,members: commands.Greedy[discord.Member]):
    #     """何時加入伺服器"""
    #     if not members:
    #         members=[ctx.author]
    
    #     for member in members:
    #         print(member.nick)
    #         await ctx.send('{0.mention} joined on {0.joined_at}'.format(member))

don = (['開墮！！！'],
       ['墮胎屬叔 AAAAA'],
       ['還敢下來啊冰鳥', '還敢下來啊**{0}**'],
       ['為什麼那個冰鳥還敢下來', '為什麼那個**{0}**還敢下來'],
       ['AAAA 嬰兒！', 'AAAA **{0}**！'],
       ['給庫！痾痾痾痾痾痾'],
       ['為什麼不幫我發大絕 極靈', '為什麼不幫我發大絕 **{0}**'],
       ['搭波kill！'],
       ['巨槌瑞斯 誇爪！哈哈哈'],
       ['哈撒ki 吹起來！聊天室滑起來！', '哈撒ki 吹起來！**{0}** 滑起來！'],
       ['DEATH IS LIKE THE WIND ALWAYS BY MY 賽'],
       ['嘿嘿嘿 又要死囉', '嘿嘿嘿 **{0}** 又要死囉'],
       ['瑞斯一打三！！！', '**{0}** 一打三！！！'],
       ['瑞斯一打五！', '**{0}** 一打五！'],
       ['這什麼...這到底什麼閃現 齁齁齁齁齁'],
       ['滑起來！通通給我滑起來！'],
       ['哈哈 又CARRY了一場 媽的'],
       ['逮到你囉！', '逮到你囉！**{0}**'],
       ['死好啊 媽的'],
       ['你看到我 媽的 巨...你看到我大槌達瑞斯 都不會怕的欸\n還在他媽 還在前面那邊洗兵耶',
        '**{0}** 看到我 媽的 巨...你看到我大槌達瑞斯 都不會怕的欸\n還在他媽 還在前面那邊洗兵耶'],
       ['喔沒有關係阿 沒有關係阿 還是讓我表演了一把阿'],
       ['鬼步開啟！！老爸墮起來！', '鬼步開啟！！**{0}** 墮起來！'],
       ['達瑞斯斷頭台！！！嬰兒通通死去', '**{0}** 斷頭台！！！嬰兒通通死去'],
       ['犽鎖開滑 嘻嘻嘻 爽哦', '**{0}** 開滑 嘻嘻嘻 爽哦'],
       ['老子瘋狗的外號他媽的10歲就有了 他媽咬死你啊糙',
        '**{0}** 瘋狗的外號他媽的10歲就有了 他媽咬死你啊糙'],
       ['媽的不讓你 不讓你見識一下 你是不知道誰是他媽的吃肉的啊'],
       ['抓進勞改營 準備好要被勞改了嗎'],
       ['家暴神拳 童家拳 開扁'],
       ['幹你不要再看了好不好 會不會來幫忙啊 糙'],
       ['你誰都可以得罪就是他媽不要得罪瘋子啊'],
       ['幹你老師的勒 媽的我給你嚇大的啊'],
       ['還想髒阿底迪', '還想髒阿 **{0}**'],
       ['我沒投在...'],
       ['拉進垃圾車！！'],
       ['狠狠的 把他甩到旁邊去', '狠狠的 把 **{0}** 甩到旁邊去'],
       ['從現在開始 瘋 狂 送 頭！'],
       ['幸福好運到 主委加碼', '幸福好運到 **{0}** 主委加碼'],
       ['乞丐大劍 轟'],
       ['你到底在幹嘛啊 天啊', '**{0}** 你到底在幹嘛啊 天啊'],
       ['還想閃現阿 HEHEHE', '**{0}** 還想閃現阿 HEHEHE'],
       ['一定打你 一定把你鼻樑打歪', '**{0}** 一定打你 一定把你鼻樑打歪'],
       ['太舒服拉'],
       ['下去囉！'],
       ['爽嗎兄弟', '爽嗎 **{0}** 兄弟'],
       ['下面一位'],
       ['整場上來零次！']
       )

async def setup(bot):
    await bot.add_cog(Others(bot))