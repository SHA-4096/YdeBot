from Sql import *
from APIClass import *
import datetime
class nucleic_stat:
    last_timecheck_date = None
    sent_msg_today = False
    send_hour = 16
    send_minute = 0
    def __init__(self,password):
        self.Sql_obj=Sql(password,'127.0.0.2','root','ydebot','gbk')
    def time_check(self):
        now_time = datetime.datetime.now()
        if(now_time.day != self.last_timecheck_date):
            self.Sql_obj.day_end_update()
            self.last_timecheck_date = now_time.day
            self.sent_msg_today = False
        if self.sent_msg_today == False and now_time.hour == self.send_hour and now_time.minute == self.send_minute:
            self.sent_msg_today = True
            res = self.query_undone_persons()
            print(res)
            if res:
                msg_nuc = "未做核酸的有：\n"
                for i in range(0,len(res)):
                    msg_nuc = msg_nuc + str(i+1) + "、" + res[i][1] +"\n"
                    API.send(msg_nuc,"private","3404097842")
            else:
                API.send("所有人均做完核酸","private","3404097842")
            
    def done_test(self,id):
        self.Sql_obj.update_undone_person_update(id)
    def query_undone_persons(self):
        res = self.Sql_obj.get_undone_person_query()
        return res
    def add_namelist(self,id,name):
        self.Sql_obj.add_name_list(id,name)
        if API.msg_type == "private":
            API.send("已添加"+name,API.msg_type,API.user_id)
        else:
            API.send("已添加"+name,API.msg_type,API.group_id)

    def person_find(self,id):
        return self.Sql_obj.person_find_query(id)

    def is_adm(self,id):
        return self.Sql_obj.is_adm_query(id)

    def query_resp(self):
        res = self.query_undone_persons()
        print(res)
        if res:
            msg_nuc = "未做核酸的有：\n"
            for i in range(0,len(res)):
                msg_nuc = msg_nuc + str(i+1) + "、" + res[i][1] +"\n"
            if API.msg_type == "private":
                API.send(msg_nuc,API.msg_type,API.user_id)
            else:
                API.send(msg_nuc,API.msg_type,API.group_id)
        else:
            if API.msg_type == "private":
                API.send("所有人均做完核酸",API.msg_type,API.user_id)
            else:
                API.send("所有人均做完核酸",API.msg_type,API.group_id)