import configparser
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageSendMessage
)

import requests
import time
from bs4 import BeautifulSoup
import os
import re
import urllib.request
import json
import random
import time

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

PTT_URL = 'https://www.ptt.cc'

PROMOTION_INTRODUCTION = ''
#line_bot_api = LineBotApi('NCDNNL5THX66jPCkTp570azB9ZzWbB1bSnRjp8H6t6C5AnN7/ar/Iy//OPHYmY8VjvcSKEcwSU71TBDEq+i1yieyLoVwxZk8xQzYQrx3pGSGYY81lgwaIXvEkG4ZYnQLZKVWcoYMG0/fPA9uEMl6UAdB04t89/1O/w1cDnyilFU=')
#handler = WebhookHandler('45ed57b8cf09441d4b82125b1dbd9134')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def _echo(event):
    uid = event.source.user_id
    profile = line_bot_api.get_profile(uid)
    if uid != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        
        if event.message.text == '您好' or event.message.text == 'Hi' or event.message.text == 'hi' or event.message.text == 'HI' or event.message.text == '妳好' or event.message.text == '你好' :
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='您好,'+profile.display_name)
            )
        if event.message.text == '抽男' or event.message.text == '抽女':
            target=''
            if event.message.text == '抽男':
                target='b'
            else:
                target='g'
            resp = requests.get(url=PTT_URL + '/bbs/Beauty/index.html', cookies={'over18': '1'})
            if resp.status_code != 200:
                print('Invalid url: ' + resp.url)
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='首頁尚無此性別')
            )
                
            elif resp.text:
                articles_b = []
                articles_g = []
                date = time.strftime("%m/%d").lstrip('0')
                #line_bot_api.reply_message(event.reply_token,TextSendMessage(text=date))
                soup = BeautifulSoup(resp.text, 'html5lib')
                paging_dev = soup.find('div', 'btn-group btn-group-paging')
                prev_url = paging_dev.find_all('a')[1]['href']
                articles = []
                divs = soup.find_all('div', 'r-ent') #標題

                for div in divs:
                    #_random = random.randint(0,len(divs)-1)
                    push_count = 0
                    push_str = div.find('div', 'nrec').text
                    
                    if push_str:
                        try:
                            push_count = int(push_str)
                        except ValueError:
                            if push_str == '爆':
                                push_count = 99
                            elif push_str.startswith('X'):
                                push_count = -10
                    if div.find('a'):
                        title = div.find('a').text
                        #print(title)
                        b_g =title.find('妹')
                        b_b =title.find('哥')
                        
                        if not((target =='b' and b_b != -1) or (target=='g' and b_g != -1)):
                            continue

                        href = div.find('a')['href']
                        author = div.find('div', 'author').text if div.find('div', 'author') else ''

                        if (target =='b' and b_b != -1):
                            articles_b.append({
                            'title': title,
                            'href': href,
                            'push_count': push_count,
                            'author': author
                        })
                        elif (target=='g' and b_g != -1):
                            articles_g.append({
                            'title': title,
                            'href': href,
                            'push_count': push_count,
                            'author': author
                        }) 
                if target =='b':
                    articles=articles_b
                elif target =='g':
                    articles=articles_g
                if len(articles) ==0:
                    line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='首頁尚無此性別')
                )
                else:
                    _random = random.randint(0,len(articles)-1)
                    resp_1 = requests.get(url=PTT_URL + articles[_random]['href'], cookies={'over18': '1'})
                    if resp_1.status_code != 200:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text='sthwrong with your setting')
                        )
                    elif resp_1.text:
                        soup = BeautifulSoup(resp_1.text, 'html.parser')
                        links = soup.find(id='main-content').find_all('a')
                        img_urls = []
                        for link in links:
                            if re.match(r'^https?://(i.)?(m.)?imgur.com', link['href']):
                                if link['href'].find('.jpg') != -1:
                                    img_urls.append(link['href'])
                                else:
                                    img_urls.append(link['href']+'.jpg')

                        _random = random.randint(0,len(img_urls)-1)
                        #line_bot_api.reply_message(event.reply_token,TextSendMessage(text=img_urls[_random]))
                        line_bot_api.reply_message(event.reply_token,ImageSendMessage(
                            original_content_url=img_urls[_random],
                            preview_image_url=img_urls[_random]
                        ))
        if event.message.text == '介紹自己':
            line_bot_api.push_message(uid, TextSendMessage(text='我是國立臺灣大學資訊管理學系四年級的學生。在大學的三年中我去修習了各種領域的知識，也接觸了各類型的比賽，為的是想確定自己的興趣所在。'))
            time.sleep(1)
            line_bot_api.push_message(uid, TextSendMessage(text='我目前仍在臺灣資訊網路中心擔任網安資訊組的實習生，主要工作在於為公司系統做串接服務，所以對前後端有所了解，同時也對其有一些興趣。'))
            time.sleep(1)
            line_bot_api.push_message(uid, TextSendMessage(text='我想繼續透過實習來增加實務經驗並且確定自己未來想發展的路，而貴公司不管在同儕亦或是長輩間的評價都十分良好，而同系的同學也有在LINE實習，都讚不絕口。希望有機會能加入貴公司並做出一些貢獻與達到自己所期望的高度。'))

if __name__ == "__main__":
    app.run()