#coding:gbk
from pymysql import NULL
from APIClass import *
import re
import random
from Sql import *
from Werewolf import *
from Nucleic_stat import *
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
    pat_werewolf_start_owner = r"开始狼人杀-建房"
    pat_werewolf_common_user = r"开始狼人杀-加房"
    pat_werewolf_end = r"结束狼人杀"
    pat_werewolf_game_start = r"开始游戏"
    pat_nucleic_test_done = r"已做"
    pat_nucleic_query = r"查询核酸"
    pat_add_member = r"姓名="
#vars for photos
#    tagged_photos={}
    statag = 'a'
    ready_for_pics = False
    Sql_obj = None
    Wwk_obj = None
    Nuc_obj = None
#vars for werewolf_killtime.sleep(0.2)
    

#Functions

    def __init__(self,password):
        self.Sql_obj = Sql(password,'127.0.0.2','root','ydebot','gbk')
        self.Wwk_obj = Werewolf_kill(password)
        self.Nuc_obj = nucleic_stat(password)
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
        key=re.split(r'[],，]',key_t[1])
        return key[0]
    

    def msg_handling(self):
        '''
        #-----------------------werewolf kill handling-----------------------

        if self.Wwk_obj.check_player_in_game(API.user_id) != "Not in any group" and re.findall(re.compile(r"操作="),API.raw_message):
            room_number = self.Wwk_obj.check_player_in_game(API.user_id)
            id_to_act_on = self.content_gen(r"操作=",API.raw_message)
            self.Wwk_obj.resp_to_data('5',room_number,'',API.user_id,'',id_to_act_on,'','','','')
            return

        if re.findall(re.compile(self.pat_werewolf_start_owner),API.raw_message):
            player_name = self.content_gen(r'昵称=',API.raw_message)
            room_number = self.content_gen(r"房号=",API.raw_message)
            room_size = self.content_gen(r"人数=",API.raw_message)
            self.Wwk_obj.resp_to_data('2',room_number,player_name,API.user_id,room_size,' ','','','','')
            return
        if re.findall(re.compile(self.pat_werewolf_common_user),API.raw_message):
            player_name = self.content_gen(r'昵称=',API.raw_message)
            room_number = self.content_gen(r"房号=",API.raw_message)
            self.Wwk_obj.resp_to_data('1',room_number,player_name,API.data['user_id'],'','','','','','')
            return
        if re.findall(re.compile(self.pat_werewolf_end),API.raw_message):
            room_number = self.Wwk_obj.check_player_in_game(API.user_id)
            self.Wwk_obj.resp_to_data('3',room_number,' ',API.data['user_id'],'','','','','','')
            return
        
        if re.findall(re.compile(self.pat_werewolf_game_start),API.raw_message):
            room_number = self.Wwk_obj.check_player_in_game(API.user_id)
            werewolf_num = self.content_gen(r"狼人=",API.raw_message)
            villager_num = self.content_gen(r"村民=",API.raw_message)
            hunter_num = self.content_gen(r"猎人=",API.raw_message)
            prophet_num = self.content_gen(r"预言家=",API.raw_message)
            self.Wwk_obj.resp_to_data('4',room_number,'',API.data['user_id'],'','',werewolf_num,villager_num,hunter_num,prophet_num)
            return
        
        


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
                    API.send("user "+str(API.data['sender']['user_id'])+" is banned!",API.msg_type,API.group_id)
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

        #------------------------nucleic_test_handling-----------------------
        if re.findall(self.pat_nucleic_test_done,API.raw_message) and API.msg_type == "private":
            if self.Nuc_obj.person_find(API.user_id):
                API.send("你已经上报了哦","private",API.user_id)
            else:
                self.Nuc_obj.done_test(API.user_id)
                API.send("bot收到！","private",API.user_id)
        
        if re.findall(self.pat_nucleic_query,API.raw_message) and self.Nuc_obj.is_adm(API.user_id):
            self.Nuc_obj.query_resp()
        

        if re.findall(self.pat_add_member,API.raw_message) and API.msg_type == "private":
            res = self.content_gen("姓名=",API.raw_message)
            self.Nuc_obj.add_namelist(API.user_id,res)




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

