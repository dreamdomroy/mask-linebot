from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *

#匯入自己的函式
from function.getOpenData import getMaskOpenData

app = Flask(__name__)

# 設定你的Channel Access Token
line_bot_api = LineBotApi('zdHfPGKV0AQHFI7B/uz+F91zdF8Z8kls+NJ6cR2z7iCtUmXUXG8YWW3FuyNU+a3+S6ORm6WKKE0APGgKX+tEiZEieERgACYlgZhbCgsP5UjNGNhmn5TCV39I0Ku0pc7oaALqenIis0ef4bjbrdgHrgdB04t89/1O/w1cDnyilFU=')
# 設定你的Channel Secret
handler = WebhookHandler('121772424af2e0b4843f59e77f1a08ab')

# 監聽所有來自 /callback 的 Post Request，我們不會動到
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
        abort(400)
    return 'OK'

#處理訊息
#當訊息種類為TextMessage時，從event中取出訊息內容，藉由TextSendMessage()包裝成符合格式的物件，並貼上message的標籤方便之後取用。
#接著透過LineBotApi物件中reply_message()方法，回傳相同的訊息內容。
#之後所有機器人判斷邏輯的編輯區
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    userSentMessage = event.message.text
    message = TemplateSendMessage(
        alt_text='請傳送座標',
        template=ConfirmTemplate(
            text='查詢附近的特約藥局，是否傳送您的經位度座標？',
            actions=[
                URIAction(
                    label='前往地圖',
                    uri='line://nv/location'
                ),
                MessageAction(
                    label='取消',
                    text='下次再查'
                )
            ]
        )
    )

    line_bot_api.reply_message(event.reply_token, message)

# 處理地點訊息，並且回傳經緯度資料
@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    # latitude緯度 longitude經度
    userlat = event.message.latitude
    userlon = event.message.longitude
    useraddress = event.message.address

    # 縣市與地址
    flag = False
    address = ''
    for text in useraddress:
        if not text.isdigit():
            flag = True
        if flag:
            address += text
    address = address[2:]

    addressList = address.split('縣')
    if len(addressList) == 1:
        county = address.split('市')[0] + '市'
    else:
        county = address.split('縣')[0] + '縣'
    
    aroundList = getMaskOpenData(county)
    storeName = ''
    for aroundStore in aroundList:
        storeName += aroundStore[1] + '\n成人口罩：' + str(aroundStore[4]) + '\n兒童口罩：' + str(aroundStore[5] + '\n')

    message = TextSendMessage(text=storeName)
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)