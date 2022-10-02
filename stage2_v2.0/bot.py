#coding:gbk
from flask import Flask,request
import re
import random
import Bing_API
from APIClass import *
from message_handling import *
from Sql import *

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
    pswrd = input("password")
#    Sql_obj = Sql(pswrd,"127.0.0.2:3306",'root','YdeBot','utf8')
    print(pswrd)
    MSG_obj = MSGHandling(pswrd)
    app.run(host='0.0.0.0',port=5701)


#    {"data":{"group":true,"group_id":725849620,"message":"[CQ:image,file=01cbb2b4f4c379207fd1e50f4f3915da.image,subType=0,url=https://gchat.qpic.cn/gchatpic_new/1/0-0-01CBB2B4F4C379207FD1E50F4F3915DA/0?term=2]","message_id":-482959512,"message_id_v2":"000000002b4396140000028f","message_seq":655,"message_type":"group","real_id":655,"sender":{"nickname":"SHAbot","user_id":1061417898},"time":1664686521},"retcode":0,"status":"ok"}