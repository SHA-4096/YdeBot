#coding:gbk
from flask import Flask,request
import requests
import re
import random
import os
class API:
    data = {}
    raw_message="NULL"
    msg_type = "NULL"
    sender_nickname = "NULL"
    user_id = "NULL"
    group_id = "NULL"
    '''
        self.raw_message=self.data['raw_message']
        self.msg_type = self.data['message_type']
        self.sender_nickname = self.data['sender']['nickname']
        self.user_id = self.data['user_id']
        self.group_id = 'None'
'''
    def send(msg,msg_type,qid):
        if msg_type == 'group':
            url= "http://127.0.0.1:5700/send_msg"
            params = {
                'message_type':msg_type,
                'group_id':qid,
                'message':msg
            }
            requests.get(url,params)
        else:
            url= "http://127.0.0.1:5700/send_msg"
            params = {
                'message_type':msg_type,
                'user_id':qid,
                'message':msg
            }
            requests.get(url,params)


class functions:
#patterns
    pat_image = r'CQ:image'
    pat_favorites = r"收藏 tag="
    pat_getpic = r"发"
#vars for photos
    tagged_photos={}
    statag = 'a'
    ready_for_pics = False


#Functions

#可以用来提取CQ码中的特定数据
    def content_gen(self,keys,msg):
#        example: keys=
        key_t=re.split(re.compile(keys),msg[1])
#        print(key_t)
        key=re.split('[],]',key_t[1])
        return key[0]
       
    def add_pics(self,tag,CQ):
        if tag not in self.tagged_photos:
            self.tagged_photos[tag] = [CQ]
        else:
            self.tagged_photos[tag].append(CQ)
    def post_pics(self,tag):
        if tag not in self.tagged_photos:
            pass
        else:
            i=random.randint(0,len(self.tagged_photos[tag]))
            if API.msg_type == "group":
                API.send(self.tagged_photos[tag][i-1],API.msg_type,API.group_id)
            else:
                API.send(self.tagged_photos[tag][i-1],API.msg_type,API.user_id)


    def reply(self,sender,msg):
        API.send("@"+sender+' '+msg)
    def msg_handling(self):

 
        #picture save handling
        if self.ready_for_pics:
            self.ready_for_pics = False
            if re.findall(re.compile(self.pat_image),API.raw_message):
#               pic=re.split(re.compile(self.pat_image),raw_message) 直接提取出了url（不看API的后果）
               self.add_pics(self.statag,API.raw_message)
               print("Picture added")
#               self.post_pics(self.statag)
               
               return
        
        #picture get handling
        if re.findall(re.compile(self.pat_getpic),API.raw_message):
            tag = re.split(re.compile(self.pat_getpic),API.raw_message)
            self.post_pics(tag[1])
            return

        #plain text handling
        if re.findall(re.compile(self.pat_favorites),API.raw_message):
            #Adding Favorites
            tag_t = re.split(self.pat_favorites,API.raw_message)
            if self.ready_for_pics == False:
                self.statag = tag_t[1]
                self.ready_for_pics=True
                print("Ready for pictures")
            return
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
        f.msg_handling()
    return 'OK'
if __name__ == '__main__':
    f = functions()
    app.run(host='0.0.0.0',port=5701)