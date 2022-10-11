#coding:gbk
import requests
import datetime
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
        now_time = datetime.datetime.now()
        if msg_type == 'group':
            url= "http://127.0.0.1:5700/send_msg"
            params = {
                'message_type':msg_type,
                'group_id':qid,
                'message':msg + "\ntime: " + str(now_time.hour) +" : " +str(now_time.minute) + " : " + str(now_time.second)
            }
            requests.get(url,params)
            print("MSGSENT")
        else:
            url= "http://127.0.0.1:5700/send_msg"
            params = {
                'message_type':msg_type,
                'user_id':qid,
                'message':msg + "\ntime: " + str(now_time.hour) +" : " +str(now_time.minute) + " : " + str(now_time.second)
            }
            requests.get(url,params)
            print("MSGSENT")

    def getmsg(msgid):
        url= "http://127.0.0.1:5700/get_msg"
        params = {
            'message_id':msgid
        }
        return requests.get(url,params).json()

    def send_privately_by_group(user_ids,msg):
        now_time = datetime.datetime.now()
        for i in user_ids:
            url= "http://127.0.0.1:5700/send_msg"
            params = {
                'message_type':"private",
                'user_id':i,
                'message':msg + "\ntime: " + str(now_time.hour) +" : " +str(now_time.minute) + " : " + str(now_time.second)
            }
            requests.get(url,params)
            print("MSGSENT")
        