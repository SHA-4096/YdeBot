#coding:gbk
from pymysql import NULL
from APIClass import *
import re
import random
from Sql import *
class MSGHandling:
#patterns
    pat_image = r'CQ:image'
    pat_favorites = r"收藏 tag="
    pat_getpic = r"发"
    pat_reply = r'CQ:reply'
    pat_split_CQ = r'[]]'
    pat_del = r"取消收藏"
    pat_unban = r"unban.CQ:at"
    pat_ban = r"ban.CQ:at" #Caution:USE AFTER pat_unban
    pat_rank = r"rank"
#vars for photos
#    tagged_photos={}
    statag = 'a'
    ready_for_pics = False
    Sql_obj = None
#Functions

    def __init__(self,password):
        self.Sql_obj=Sql(password,'127.0.0.2','root','ydebot','gbk')
    def add_pics(self,tag,CQ,filename):
        self.Sql_obj.insert(tag,CQ,filename)
        print(CQ+"MSG,Line29")
    def post_pics(self,tag):
        res = self.Sql_obj.query(tag)
        if res:
            i=random.randint(0,len(res))
            if API.msg_type == "group":
                API.send(res[i-1][1],API.msg_type,API.group_id)
            else:
                API.send(res[i-1][1],API.msg_type,API.user_id)
#可以用来提取CQ码中的特定数据                
    def content_gen(self,keys,msg):
#        example: keys=
        key_t=re.split(re.compile(keys),msg)
#        print(key_t)
        key=re.split(r'[],]',key_t[1])
        return key[0]
    

    def msg_handling(self):
        #-----------------------picture save handling-----------------------
        if self.ready_for_pics:
            self.ready_for_pics = False
            if re.findall(re.compile(self.pat_image),API.raw_message):
                if not self.Sql_obj.ban_query(str(API.data['sender']['user_id'])):
                    self.Sql_obj.update_status(API.data['sender']['nickname'])
                    pic=re.split(re.compile(self.pat_image),API.raw_message)
                    print("OK_CQ:"+pic[1])
                    file = self.content_gen("file=",pic[1])
                    print("FILE:"+file)
                    self.add_pics(self.statag,API.raw_message,file)
                    print("Picture added")
#                    self.post_pics(self.statag)
                    return
                else:
                    print("user "+str(API.data['sender']['user_id'])+" is banned!")
            return
        
        #-----------------------picture get handling-----------------------
        if re.findall(re.compile(self.pat_getpic),API.raw_message):
            tag = re.split(re.compile(self.pat_getpic),API.raw_message)
            self.post_pics(tag[1])
            return

        #-----------------------favorite_pictures handling-----------------------
        if re.findall(re.compile(self.pat_favorites),API.raw_message):
            #Adding Favorites
            tag_t = re.split(self.pat_favorites,API.raw_message)
            if self.ready_for_pics == False:
                self.statag = tag_t[1]
                self.ready_for_pics=True
                print("Ready for pictures")
            return
        
        #----------------------Cancel favorite handling-----------------------
        if re.findall(re.compile(self.pat_reply),API.raw_message):
#            print(API.raw_message)
            temp = re.split(re.compile(self.pat_reply),API.raw_message)
            msg_id = self.content_gen('id=',temp[1])
            msg = re.split(re.compile(self.pat_split_CQ),API.raw_message)
            real_msg = msg[len(msg)-1]
            if re.findall(re.compile(self.pat_del),real_msg):
                if API.data['sender']['role'] == 'owner' or API.data['sender']['role'] == 'admin' or re.findall(re.compile(API.user_id),msg[1]):
                    CQ_temp = API.getmsg(msg_id)
                    CQ = CQ_temp["data"]['message']
                    print("DEL_CQ:"+CQ)
                    file = self.content_gen("file=",CQ)
                    print("CQ2FILE:"+file)
                    self.Sql_obj.delete_by_CQ(file)
                    print(CQ)
                    print("Deleted")
            return

        #-----------------------unbanning handling-----------------------
        if re.findall(self.pat_unban,API.raw_message):
            id_to_unban = self.content_gen("qq=",API.raw_message)
            self.Sql_obj.unban_delete(id_to_unban)
            return
        
        #-----------------------banning handling-----------------------
        if re.findall(self.pat_ban,API.raw_message):
            id_to_ban = self.content_gen("qq=",API.raw_message)
            self.Sql_obj.ban_add(id_to_ban)
            return
        
        #-----------------------ranking handling-----------------------
        if re.findall(self.pat_rank,API.raw_message) and API.msg_type == "group":
            rnk = self.Sql_obj.upload_rank()
            if rnk:
                rnk_txt = "今天发送图片最多的几位同学有：\n"
                for i in range(0,len(rnk)):
                    rnk_txt = rnk_txt + "NO." + str(i+1) + " " + rnk[i][0] + " (" + rnk[i][1] + "次)\n"
                API.send(rnk_txt,API.msg_type,API.group_id)
            else:
                API.send("今天还没有人上传图片哦",API.msg_type,API.group_id)
'''       
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
'''
