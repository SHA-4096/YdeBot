#coding:gbk
import pymysql

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
#        cursor = self.GetCursor()
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
#        print("ID to unban is:"+user_id)
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
#        sql_query_room_num = "select * from werewolf where room_number='%s'"%(room_number)
        sql_insert = "insert into werewolf(name,voting,role,is_out,room_number,game_status,player_id) values(%s,%s,%s,%s,%s,%s,%s) "
        sql_new_room = "insert into werewolf_roomsize(room_number,room_size,member_number) values(%s,%s,%s)"
        self.cursor.execute(sql_query_user)
        res = self.cursor.fetchall()
        if res:
            '''Configure Later'''
            pass
        else:
            chk = self.check_avail(room_number)
            if  chk == "True":
#                self.cursor.execute(sql_query_room_num)
#                res_2 = self.cursor.fetchall()
#                if res_2:#enter as a common member
                data = [name,'0','Common member','False',room_number,"Available",player_id]
                self.cursor.execute(sql_insert,data)
                self.conn.commit()
                return
            if chk == "No such room":#enter as owner
                data = [name,'0','Owner','False',room_number,"Available",player_id]
                data_create = [room_number,room_size,'1']
                self.cursor.execute(sql_insert,data)
                self.conn.commit()
                self.cursor.execute(sql_new_room,data_create)
                self.conn.commit()
                return
            print(chk)

    def check_avail(self,room_number):
        '''CAUTION:Return value is a string(True/Room is full/No such room)'''
        sql_query = "select * from werewolf_roomsize where room_number=%s"%(room_number)
        sql_add = "update werewolf_roomsize set member_number=%s where room_number=%s"
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        if res:
            if res[0][1] == res[0][2]:
                return "Room is full"
            else:
                data = [str(int(res[0][2])+1),room_number]
                self.cursor.execute(sql_add,data)
                self.conn.commit()
                return "True"
        return "No such room"
    def end_game(self,room_number):
        sql_del_1 = 'delete from werewolf where room_number=%s'%(room_number)
        sql_del_2 = 'delete from werewolf_roomsize where room_number=%s'%(room_number)
        self.cursor.execute(sql_del_1)
        self.conn.commit()
        self.cursor.execute(sql_del_2)
        self.conn.commit()

    def end(self):
        self.cursor.close()
        self.conn.close()
'''    
    def check_avail(self,number_of_players,room_number):
#        To determine whether the room is full
        sql_query = "select * from werewolfs where room_number=%s"%(room_number)
        sql_change_status = "update werewolfs set game_status=%s where room_number=%s"
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        if len(res) == number_of_players:
            print("Room is full")
            data = ["Ready",room_number]
            self.cursor.execute(sql_change_status,data)
            return True
        return False
'''





    



