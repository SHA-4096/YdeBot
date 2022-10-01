#coding:gbk
from flask import Flask,request
import re
import random
import Bing_API
from APIClass import *
from message_handling import *


app = Flask(__name__)
 
@app.route('/',methods=['POST'])
def post_data():
    temp = request.get_json()
    API.data = temp
    if API.data['post_type'] == 'message':
        API.raw_message=API.data['message']
        API.sender_nickname=API.data['sender']['nickname']
        API.msg_type = API.data['message_type']
        API.sender_nickname = API.data['sender']['nickname']
        API.user_id = API.data['user_id']
        API.group_id = 'None'
        if API.msg_type == 'group':
            API.group_id = API.data['group_id']
#        print(data)
        MSG_obj.msg_handling()
    return 'OK'
if __name__ == '__main__':
    MSG_obj = MSGHandling()
    app.run(host='0.0.0.0',port=5701)