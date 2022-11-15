import os
import requests
from youtube_scraper.scraper import scrape_url
from bs4 import BeautifulSoup

from dotenv import load_dotenv

load_dotenv()
YT_API_KEY = os.getenv('YT_API_KEY')
ID = 'mixer'


def yt_id_to_icon():
    """組合 URL 後 GET 網頁並轉換成 JSON"""
    api_url = f"https://youtube.googleapis.com/youtube/v3/channels?part=snippet&id={ID}&key={YT_API_KEY}"
    response = requests.get(api_url)
    data = response.json()

    print(api_url)
    print(data['pageInfo']['totalResults'])
    # return (data['items'][0]['snippet']['thumbnails']['medium']['url'])

#yt_id_to_icon()



from googlesearch import search

headers = {'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

query = "聽海"+' 魔鏡歌詞網'

def mojin(query):
    for url in search(query, stop=5, pause=2.0):
        if url.startswith('https://mojim.com/twy'):
            return url
    return None

url=mojin(query)

print(url)
try:
    url_old=url
    url = url.replace('https://mojim.com/twy','https://mojim.com/twthx')
    url = url.replace('.htm','x1.htm')
    print('2',url)

    html = requests.get(url,headers=headers)
    #html.text.replace('<br>','\n')
    soup = BeautifulSoup(html.text, 'html.parser')
    text = str(soup.find('textarea',id='aaa_d'))
    newstart=text.find('【')
    newstart=text.find('【',newstart+1)
    newend=text.find('】',newstart+1)
    print(text[newstart+1:newend])
    start=text.find('>')
    end=text.find('\n',start+1)

    title=text[start:end].replace('>修改 ','')
    lyrics=text[end:].replace('</textarea>','')

    while True:
        start = lyrics.find("[")
        end = lyrics.find("\n",start+1)
        if start==-1 or end==-1:
            break
        lyrics=lyrics.replace(lyrics[start:end+1],'')
    # 刪除前後的換行
    while True:
        if lyrics.startswith('\n'):
            lyrics=lyrics[1:]
        elif lyrics.endswith('\n'):
            lyrics=lyrics[:-1]
        else:
            break

    print(title)
    print(lyrics)
    #s_replace = dl.replace('<br/>',"\n")    #用換行符替換'<br/>'
    #print('replace=',s_replace)
    # for s in dl:
    #     print(s)
    #     print('qq')


except:
    pass