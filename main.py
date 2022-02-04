import discord
from discord.ext import commands
import music2
import music
import random
import typing
import secret

client = commands.Bot(command_prefix='--',description='你們好 我叫阿傑 大家都叫我傑哥')

@client.event
async def on_ready():
    print('大家好 我叫阿傑')
    await client.change_presence(status=discord.Status.online, activity=discord.Game(name="阿偉"))

@client.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='',description='**輸入參數錯誤或不足，我看你完全是不懂哦**',color=0xf93a2f)
        await ctx.send(embed=embed)
        #await ctx.send('***輸入參數錯誤或不足，我看你完全是不懂哦***')
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title='',description='**無效指令，我看你是完全不懂哦**',color=0xf93a2f)
        await ctx.send(embed=embed)
        #await ctx.send('***無效指令，我看你是完全不懂哦***')




@client.command()
async def ping(ctx):
    await ctx.send(f'current ping = {round(client.latency*1000)}ms')
    
@client.command(name='guodon',aliases=['國棟','國動','動主播','瘋狗'])
async def _guodon(ctx,amount:typing.Optional[int],member: typing.Optional[discord.Member],second:typing.Optional[int]):
    if not amount:
        if second: amount=second
        else: amount=1
    
    don = ( ['開墮！！！'],
            ['墮胎屬叔 AAAAA'],
            ['還敢下來啊冰鳥','還敢下來啊**{0}**'],
            ['為什麼那個冰鳥還敢下來','為什麼那個**{0}**還敢下來'],
            ['AAAA 嬰兒！','AAAA **{0}**！'],
            ['給庫！痾痾痾痾痾痾'],
            ['為什麼不幫我發大絕 極靈','為什麼不幫我發大絕 **{0}**'],
            ['搭波kill！'],
            ['巨槌瑞斯 誇爪！哈哈哈'],
            ['哈撒ki 吹起來！聊天室滑起來！','哈撒ki 吹起來！**{0}** 滑起來！'],
            ['DEATH IS LIKE THE WIND ALWAYS BY MY 賽'],
            ['嘿嘿嘿 又要死囉','嘿嘿嘿 **{0}** 又要死囉'],
            ['瑞斯一打三！！！','**{0}** 一打三！！！'],
            ['瑞斯一打五！','**{0}** 一打五！'],
            ['這什麼...這到底什麼閃現 齁齁齁齁齁'],
            ['滑起來！通通給我滑起來！'],
            ['哈哈 又CARRY了一場 媽的'],
            ['逮到你囉！','逮到你囉！**{0}**'],
            ['死好啊 媽的'],
            ['你看到我 媽的 巨...你看到我大槌達瑞斯 都不會怕的欸\n還在他媽 還在前面那邊洗兵耶',
            '**{0}** 看到我 媽的 巨...你看到我大槌達瑞斯 都不會怕的欸\n還在他媽 還在前面那邊洗兵耶'],
            ['喔沒有關係阿 沒有關係阿 還是讓我表演了一把阿'],
            ['鬼步開啟！！老爸墮起來！','鬼步開啟！！**{0}** 墮起來！'],
            ['達瑞斯斷頭台！！！嬰兒通通死去','**{0}** 斷頭台！！！嬰兒通通死去'],
            ['犽鎖開滑 嘻嘻嘻 爽哦','**{0}** 開滑 嘻嘻嘻 爽哦'],
            ['老子瘋狗的外號他媽的10歲就有了 他媽咬死你啊糙',
            '**{0}** 瘋狗的外號他媽的10歲就有了 他媽咬死你啊糙'],
            ['媽的不讓你 不讓你見識一下 你是不知道誰是他媽的吃肉的啊'],
            ['抓進勞改營 準備好要被勞改了嗎'],
            ['家暴神拳 童家拳 開扁'],
            ['幹你不要再看了好不好 會不會來幫忙啊 糙'],
            ['你誰都可以得罪就是他媽不要得罪瘋子啊'],
            ['幹你老師的勒 媽的我給你嚇大的啊'],
            ['還想髒阿底迪','還想髒阿 **{0}**'],
            ['我沒投在...'],
            ['拉進垃圾車！！'],
            ['狠狠的 把他甩到旁邊去','狠狠的 把 **{0}** 甩到旁邊去'],
            ['從現在開始 瘋 狂 送 頭！'],
            ['幸福好運到 主委加碼','幸福好運到 **{0}** 主委加碼'],
            ['乞丐大劍 轟'],
            ['你到底在幹嘛啊 天啊','**{0}** 你到底在幹嘛啊 天啊'],
            ['還想閃現阿 HEHEHE','**{0}** 還想閃現阿 HEHEHE'],
            ['一定打你 一定把你鼻樑打歪','**{0}** 一定打你 一定把你鼻樑打歪'],
            ['太舒服拉'],
            ['下去囉！'],
            ['爽嗎兄弟','爽嗎 **{0}** 兄弟'],
            ['下面一位'],
            ['整場上來零次！']
    )

    temp = []
    for i in range(0,amount): 
        new=random.choice(don) #任選一個國動語錄
        while new in temp:  new=random.choice(don) #若重複就重新選
        temp.append(new)
    
    for reply in temp:
        if member:
            try: msg = reply[1]
            except: msg = reply[0]
            await ctx.send(msg.format(member.nick if member.nick else member.name))
        else:
            msg = reply[0]
            await ctx.send(msg)
        


#測試輸入
@client.command()
async def testinput(ctx,*,arg):
    #link=' '.join(arg)
    await ctx.send(f'input = [{arg}]')
'''
#test class
class Slapper(commands.Converter):
    async def convert(self, ctx, argument):
        #to_slap = random.choice(ctx.guild.members)
        to_slap = ctx.author 
        return '{0} slapped {1} because *{2}*'.format(ctx.author, to_slap, argument)

@client.command()
async def slap(ctx, *, reason: Slapper):
    await ctx.send(reason)
'''

#哪時候加入
@client.command()
async def joined(ctx,members: commands.Greedy[discord.Member]):
    if not members:
        members=[ctx.author]
    for member in members:
        await ctx.send('{0.mention} joined on {0.joined_at}'.format(member))

@client.event
async def on_message(message):
    #避免讀到自己的訊息
    if message.author == client.user:
        return
    keys=[  ['聽話','你幹嘛'],#0
            ["就是遜","我超勇的","超會喝"],#1
            ["聽你這麼說","你很勇哦"],#2
            ["我看看","讓我康康"],#3
            ["懂什麼","懂甚麼"],#4
            ["新遊戲"],#5
            ["累了","睡覺","先下","晚安","下線"],#6
            #["你好","你們好","傑哥","杰哥","阿杰","阿傑","HI","hi","Hi"],#7
            ['好蒿','爽爽'],#8
            ['好爽']
    ]
    replys=[['讓我看看！'],#0
            ["我看你...完全是不懂哦","聽你這麼說...你很勇哦"],#1
            ["開玩笑 我超勇的好不好 超會喝的啦"],#2
            ["不要！"],#3
            ["你想懂 我房裡有些好康的","來啦 來看就知道了"],#4
            ["什麼新遊戲 比遊戲還刺激"],#5
            ["玩累了...就直接睡覺 沒問題的"],#6
            #["你們好 我叫阿傑 大家都叫我傑哥","我家很大 歡迎你們來我家玩"],#7
            [f'**{message.author.mention}** 和我，我們倆要...好蒿爽爽！'],#8
            [f'**{message.author.mention}** 爽嗎兄弟']
    ]
    for i in range(len(keys)):
        for keyword in keys[i]:
            if keyword in message.content:
                await message.channel.send(random.choice(replys[i]))
                break
    
    #將訊息當成command再辨識一遍，不然其他的指令就沒用
    await client.process_commands(message)



# cogs 是裡面有discord command的一種class
cogs = [music]
#cogs = [music2]

for cog in cogs:
    cog.setup(client)


client.run(secret.TOKEN)

    

