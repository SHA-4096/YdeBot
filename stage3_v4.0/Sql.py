#coding:gbk
import pymysql
import random
from APIClass import *

class Sql:
    password = ''
    host = ''
    user = ''
    database = ''
    charset = ''
    cursor = pymysql.NULL
    conn = pymysql.NULL
    def __init__(self,password,host,user,database,charset):
        self.password = password
        self.host = host
        self.user = user
        self.database = database
        self.charset = charset
        self.cursor = self.GetCursor()
    def GetCursor(self):
        self.conn = pymysql.connect(
            host = self.host,
            user = self.user,
            password = self.password,
            database = self.database,
            charset = self.charset
            )
        print("******Successfully Connected******")
        cursor = self.conn.cursor()
        return cursor
    #--------------------pictures--------------------
    def query(self,tag):
        sql = "select tag,CQ from favorite_pics where tag = '%s'"%(tag)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res
    def insert(self,tag,CQ,file):
        sql = 'insert into favorite_pics(tag,CQ,filename) values(%s,%s,%s)'
        data = [tag,CQ,file]
        self.cursor.execute(sql,data)
        self.conn.commit()
    def delete_by_CQ(self,file):
        sql = "delete from favorite_pics where filename=%s "
        data = [file]
        self.cursor.execute(sql,data)
        self.conn.commit()
    def clear(self):
        sql = 'delete from favorite_pics'
        self.cursor.execute(sql)
        self.conn.commit()


    #--------------------ban and unban--------------------
    def unban_delete(self,user_id):
        sql = 'delete from banned_users where id=%s '
        data = [user_id]
        self.cursor.execute(sql,data)
        self.conn.commit()
    def ban_add(self,user_id):
        sql = "insert into banned_users(id) values(%s)"
        data = [user_id]
        self.cursor.execute(sql,data)
        self.conn.commit()
    def ban_query(self,query_id):
        sql = "select id from banned_users where id='%s'"%(query_id)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if res:
            return True
        return False

    #--------------------upload_rank--------------------
    def Get_Date(self):
        sql = 'select current_date()'
        self.cursor.execute(sql)
        date = self.cursor.fetchall()
        return str(date[0][0])

    def update_status(self,user_name):
        sql_query = "select id,latest_upload_time,upload_count from uploads where id = '%s'"%(user_name)
        sql_query2 = "select * from uploads"
        sql_clear = 'delete from uploads'
        sql_insert = 'insert into uploads(id,latest_upload_time,upload_count) values(%s,%s,%s)'
        sql_update = 'update uploads set upload_count=%s where id=%s'
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        if res:#uploaded before
            if res[0][1] != self.Get_Date():#not today
                self.cursor.execute(sql_clear)
                self.conn.commit()
                data = [user_name,self.Get_Date(),'1']
                self.cursor.execute(sql_insert,data)
                self.conn.commit()
            else:
                str(int(res[0][2])+1)
                data = [str(int(res[0][2])+1),res[0][0]]
                print(res[0][2])
                self.cursor.execute(sql_update,data)
                self.conn.commit()
        else:
            self.cursor.execute(sql_query2)
            tmp = self.cursor.fetchall()
            if tmp:
                now = tmp[0][1]
                if now != self.Get_Date():
                    self.cursor.execute(sql_clear)
                    self.conn.commit()
                    data = [user_name,self.Get_Date(),'1']
                    self.cursor.execute(sql_insert,data)
                    self.conn.commit()
                    return
            data = [user_name,self.Get_Date(),'1']
            self.cursor.execute(sql_insert,data)
            self.conn.commit()
            return

    def upload_rank(self):
        '''return a set of names and times of uploading'''
        sql_order = 'select * from uploads order by upload_count DESC'
        self.cursor.execute(sql_order)
        res = self.cursor.fetchall()
        ret = []
        for i in range(0,min(5,len(res))):
            print("i="+str(i))
            ret.append([res[i][0],res[i][2]])
        return ret

    #--------------------Werewolf Kill--------------------
    def enter_room_add(self,name,room_number,player_id,room_size):
        '''About Roomsize:Only have effect when room is created'''
        sql_query_user = "select * from werewolf where player_id='%s'"%(player_id)
        sql_query_playernum = "select member_number from werewolf_roomsize where room_number='%s'"%(room_number)
        sql_insert = "insert into werewolf(name,voting,role,is_out,room_number,game_status,player_id,id,have_voted,game_role) values(%s,%s,%s,%s,%s,%s,%s,%s,'False','Not assigned') "
        sql_new_room = "insert into werewolf_roomsize(room_number,room_size,member_number,game_started,Re_voting,game_stage) values(%s,%s,%s,'False','False','werewolf')"
        self.cursor.execute(sql_query_user)
        res = self.cursor.fetchall()
        if res:
            API.send("You're already in a room","private",API.user_id)
        else:
            chk = self.check_avail(room_number)
            if  chk == "True":
                self.cursor.execute(sql_query_playernum)
                cnt = self.cursor.fetchall()
                data = [name,'0','Common member','False',room_number,"Available",player_id,str(int(cnt[0][0])+1)]
                self.cursor.execute(sql_insert,data)
                self.conn.commit()
                self.update_playernum(room_number,1)
                return
            if chk == "No such room":#enter as owner
                data = [name,'0','Owner','False',room_number,"Available",player_id,'1']
                data_create = [room_number,room_size,'1']
                self.cursor.execute(sql_insert,data)
                self.conn.commit()
                self.cursor.execute(sql_new_room,data_create)
                self.conn.commit()
                return
            print(chk)

    def id_assign_update(self,room_number):
        sql_query = "select player_id from werewolf where room_number=%s"%(room_number)
        sql_alter = "update werewolf set id=%s where player_id=%s and room_number=%s"
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        for i in range(0,len(res)):
            data = [str(i+1),res[i][0],room_number]
            self.cursor.execute(sql_alter,data)
            self.conn.commit()

    def game_role_assign(self,room_number,num_of_werewolf,num_of_villager,num_of_hunter,num_of_prophet):
        res = self.get_room_status_query(room_number)
        player_num = int(res[1])
        not_assigned_players = []
        for i in range(0,player_num):
            not_assigned_players.append(i+1)
        sql_update = 'update werewolf set game_role=%s where id=%s and room_number=%s'
        werewolves_user_id = []
        werewolves_id = []
        for i in range(0,num_of_werewolf):
            j = random.randint(0,player_num-1)
            data = ["werewolf",str(not_assigned_players[j]),room_number]
            self.cursor.execute(sql_update,data)
            self.conn.commit()
            res = self.get_individual_status_by_id_and_room_number(not_assigned_players[j],room_number)
            werewolves_user_id.append(res[6])
            werewolves_id.append(res[7])
            not_assigned_players.pop(j)
            player_num -= 1
        wrfs = " "
        for i in werewolves_id:
            wrfs += i
        API.send_privately_by_group(werewolves_user_id,"You are the werewolf,werewolfs are "+wrfs)
        villagers_user_id = []
        for i in range(0,num_of_villager):
            j = random.randint(0,player_num-1)
            data = ["villager",str(not_assigned_players[j]),room_number]
            self.cursor.execute(sql_update,data)
            self.conn.commit()
            res = self.get_individual_status_by_id_and_room_number(not_assigned_players[j],room_number)
            villagers_user_id.append(res[6])
            not_assigned_players.pop(j)
            player_num -= 1
        API.send_privately_by_group(villagers_user_id,"You are the villager")
        hunters_user_id = []
        for i in range(0,num_of_hunter):
            j = random.randint(0,player_num-1)
            data = ["hunter",str(not_assigned_players[j]),room_number]
            self.cursor.execute(sql_update,data)
            self.conn.commit()
            res = self.get_individual_status_by_id_and_room_number(not_assigned_players[j],room_number)
            hunters_user_id.append(res[6])
            not_assigned_players.pop(j)
            player_num -= 1
        API.send_privately_by_group(hunters_user_id,"You are the hunter")
        prophets_user_id = []
        for i in range(0,num_of_prophet):
            j = random.randint(0,player_num-1)
            data = ["prophet",str(not_assigned_players[j]),room_number]
            self.cursor.execute(sql_update,data)
            self.conn.commit()
            res = self.get_individual_status_by_id_and_room_number(not_assigned_players[j],room_number)
            prophets_user_id.append(res[6])
            not_assigned_players.pop(j)
            player_num -= 1
        API.send_privately_by_group(prophets_user_id,"You are the prophet")
        print("assign finished,"+str(player_num)+" people are not assigned")

    def quit_room_delete(self,player_qq):
        sql_query_user = "select * from werewolf where player_id=%s"%(player_qq)
        sql_delete_user = "delete from werewolf where player_id=%s"%(player_qq)
        self.cursor.execute(sql_query_user)
        res = self.cursor.fetchall()
        if res:
            if self.check_avail(res[0][4]) == 'Game started':
                print("Sorry,can't run away since game has started")
                API.send("Sorry,can't run away since game has started","private",API.user_id)
            else:
                self.update_playernum(res[0][4],-1)
                self.cursor.execute(sql_delete_user)
                self.conn.commit()
            return
        else:
            print("You haven't joined any groups yet")
            API.send("You haven't joined any groups yet","private",API.user_id)
            return

    def update_playernum(self,room_number,t):
        '''t = 1 or -1'''
        sql_update = "update werewolf_roomsize set member_number=%s where room_number=%s"
        sql_query = "select * from werewolf_roomsize where room_number=%s"%(room_number)
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        data = [str(int(res[0][2])+t),room_number]
        self.cursor.execute(sql_update,data)
        self.conn.commit()

    def update_roomstatus(self,room_number,stat):
        sql_update = "update werewolf_roomsize set game_started='%s' where room_number=%s"%(stat,room_number)
        self.cursor.execute(sql_update)
        self.conn.commit()

    def check_avail(self,room_number):
        '''CAUTION:Return value is a string(True/Room is full/No such room/Game started)'''
        sql_query = "select * from werewolf_roomsize where room_number=%s"%(room_number)
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        if res:
            if res[0][3] == "True":
                return "Game started"
            elif res[0][1] == res[0][2]:
                return "Room is full"
            else:
                return "True"
        return "No such room"

    def get_avail_rooms(self):
        '''Return a list of rooms available'''
        sql_query = "select room_number from werewolf_roomsize"
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        ret = []
        if res:
            for i in range(0,len(res)):
                ret.append(res[i])
        return ret
    
    def check_player_in_game_query(self,player_qq):
        '''return the number of the room'''
        sql = 'select room_number from werewolf where player_id=%s'%(player_qq)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if res:
            return res[0][0]
        return "Not in any group"

    def get_surviving_players(self,room_number):
        '''return a two dimensional list of id of surviving players and player name'''
        sql_query = 'select * from werewolf where is_out="False" and room_number=%s'%(room_number)
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        ret = []
        ret.clear()
        for i in range(0,len(res)):
            ret.append([res[i][7],res[i][0]])
        return ret

    def get_individual_status(self,player_id):
        '''return the information in a one dimensional list or "No such player"'''
        sql_query = "select * from werewolf where player_id=%s"%(player_id)
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        if res:
            return res[0]
        else:
            return "No such player"
    
    def get_individual_status_by_id_and_room_number(self,id,room_number):
        sql_query = " SELECT * FROM werewolf WHERE id='%s' AND room_number='%s'"%(id,room_number)
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        if res:
            return res[0]
        else:
            return "No such player"

    def get_voting_finishing_status(self,room_number):
        '''return a bool value describing whether everyone surviving finished voting(Run each time when receving a message)'''
        sql_query = 'select * from werewolf where is_out="False" and have_voted="False" and room_number=%s'%(room_number)
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        if res:
            return False
        return True
        
    def get_player_list_query(self,room_number):
        '''return a list of all players'info in the room'''
        sql_query = 'select * from werewolf where room_number=%s'%(room_number)
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        return res

    def end_game(self,room_number):
        sql_del_1 = 'delete from werewolf where room_number=%s'%(room_number)
        sql_del_2 = 'delete from werewolf_roomsize where room_number=%s'%(room_number)
        self.cursor.execute(sql_del_1)
        self.conn.commit()
        self.cursor.execute(sql_del_2)
        self.conn.commit()

    def vote_update(self,id_to_vote,voter_id,room_number):
        '''id_to_vote = 0 means abandon voting'''
        sql_update_to_vote = 'update werewolf set voting=%s where id=%s and room_number=%s'
        sql_update_voter = 'update werewolf set have_voted="True" where id=%s and room_number=%s'
        sql_query = 'select voting from werewolf where id=%s and room_number=%s'%(id_to_vote,room_number)
        if id_to_vote == '0':
            room_info = self.get_room_status_query(room_number)
            if room_info != "No such room":
                if room_info[4] == "False":
                    print("Player No."+voter_id+" has abandoned voting")
                    API.send("Player No."+voter_id+" has abandoned voting","group","206419158")
                    data_voter = [voter_id,room_number]
                    self.cursor.execute(sql_update_voter,data_voter)
                    self.conn.commit()
                    return
                else:
                    print("Can't abandon voting now,please vote again")
                    API.send("Can't abandon voting now,please vote again","private",API.user_id)
                    return
            else:
                print(room_info)
                return
        #Not abandon voting
        self.cursor.execute(sql_query)
        q_res = self.cursor.fetchall()
        if q_res:
            data_to_vote = [str(int(q_res[0][0])+1),id_to_vote,room_number]
            data_voter = [voter_id,room_number]
            self.cursor.execute(sql_update_to_vote,data_to_vote)
            self.conn.commit()
            self.cursor.execute(sql_update_voter,data_voter)
            self.conn.commit()
            API.send("No."+voter_id + " has voted No."+id_to_vote,"group","206419158")
            
        else:
            print("No such player")
    
    def prophet_inquired_update(self,id_of_prophet,room_number):
        sql_update_voter = 'update werewolf set have_voted="True" where player_id=%s and room_number=%s'%(id_of_prophet,room_number)
        self.cursor.execute(sql_update_voter)
        self.conn.commit()
    
    def prophet_finished_query(self,room_number):
        '''return a boolean value of whether a prophet hasn't inquired yet'''
        sql_query = 'select * from werewolf where is_out="False" and have_voted="False" and game_role="prophet" and room_number=%s'%(room_number)
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        if res:
            return False
        else:
            return True

    def check_game_end_query(self,room_number):
        '''end game when TUCHENG,return string'''
        sql_werewolf_lose = 'select * from werewolf where game_role="werewolf" and is_out="False" and room_number="%s"'%(room_number)
        self.cursor.execute(sql_werewolf_lose)
        res1 = self.cursor.fetchall()
        if res1:
            pass
        else:
            return "Werewolves have lost"
        sql_werewolf_win = 'select * from werewolf where game_role!="werewolf" and is_out="False" and room_number="%s"'%(room_number)
        self.cursor.execute(sql_werewolf_win)
        res2 = self.cursor.fetchall()
        if res2:
            return "Game continue"
        else:
            return "Werewolves have win"
    
    def check_game_role_living_query(self,game_role,room_number):
        '''return the number of surviving game_role inquired'''
        sql_query = 'select * from werewolf where game_role="%s" and room_number="%s"'%(game_role,room_number)
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        if res:
            return True
        return False
        
    def eliminate_update(self,room_number):
        sql_order = 'select * from werewolf order by voting DESC'
        sql_eli = 'update werewolf set is_out="True" where id=%s and room_number=%s'
        self.cursor.execute(sql_order)
        res = self.cursor.fetchall()
        if res[0][1] != res[1][1]:#exist a most_voted player
            data = [res[0][7],room_number]
            print("Player No."+res[0][7]+" is eliminated")
            API.send("Player No."+res[0][7]+" is eliminated","group","206419158")
            self.survivors_update(room_number)
            self.cursor.execute(sql_eli,data)
            self.conn.commit()
            self.reset_vote_update(room_number,"False")
            return "Elimination finished"
        else:
            print("Start voting again,until someone is eliminated")
            API.send("Start voting again,until someone is eliminated,NO abandoning voting","group","206419158")
            self.reset_vote_update(room_number,"True")
            return "Re-voting"

    def killed_by_werewolf_update(self,id_to_act_on,room_number):
        sql = 'update werewolf set is_out="True" where room_number=%s and id=%s'%(room_number,id_to_act_on)
        self.cursor.execute(sql)
        self.conn.commit()
        print("No."+id_to_act_on+" is out")
        API.send("No."+id_to_act_on+" is out","group","206419158")
        return

    def reset_vote_update(self,room_number,is_revoting):
        sql_werewolf_roomsize = 'update werewolf_roomsize set Re_voting ="%s" where room_number=%s'%(is_revoting,room_number,)
        sql_werewolf = 'update werewolf set voting="0",have_voted="False" where room_number=%s'%(room_number)
        self.cursor.execute(sql_werewolf)
        self.conn.commit()
        self.cursor.execute(sql_werewolf_roomsize)
        self.conn.commit()
    
    def reset_isout_update(self,room_number):
        sql_update = 'update werewolf set is_out="False" where room_number=%s'%(room_number)
        self.cursor.execute(sql_update)
        self.conn.commit()

    def get_room_status_query(self,room_number):
        '''return a list of room status or string "No such room"'''
        sql_query = "select * from werewolf_roomsize where room_number=%s"%(room_number)
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        if res:
            return res[0]
        else:
            return "No such room"

    def set_room_status_update(self,room_number,input_key_name,input_content):
        '''update the info in werewolf_roomsize'''
        sql_update = 'UPDATE werewolf_roomsize SET %s="%s" WHERE room_number="%s"'%(input_key_name,input_content,room_number)
        self.cursor.execute(sql_update)
        self.conn.commit()
        print(input_key_name+" has been set as "+input_content)
        API.send(input_key_name+" has been set as "+input_content,"group","206419158")
        self.survivors_update(room_number)
        

    def send_pri_by_grp(self,room_number,msg):
        res = self.get_player_list_query(room_number)
        player_ids = []
        for i in range(0,len(res)):
            player_ids.append(res[i][6])
        API.send_privately_by_group(player_ids,msg)

    def end(self):
        self.cursor.close()
        self.conn.close()

    def survivors_update(self,room_number):
        res = self.get_surviving_players(room_number)
        msg = 'Now surviving:\n'
        for i in range(0,len(res)):
            msg += 'No.' + res[i][0] + " " + res[i][1] + '\n'
        API.send(msg,"group","206419158")
    
    def in_room_update(self,room_number):
        res = self.get_surviving_players(room_number)
        msg = 'Now in_room:\n'
        for i in range(0,len(res)):
            msg += 'No.' + res[i][0] + " " + res[i][1] + '\n'
        API.send(msg,"group","206419158")





    


