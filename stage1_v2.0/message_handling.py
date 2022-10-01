#coding:gbk
from APIClass import *
import re
import random
class MSGHandling:
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