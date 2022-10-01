from flask import Flask,request
import requests


class API:
    def send(msg):
        url= "http://127.0.0.1:5700/send_msg"
        params = {
            'message_type':'public',
            'group_id':'725849620',
            'message':msg
            }
        requests.get(url,params)


class functions:
    def reply(sender,msg):
        API.send("@"+sender+' '+msg)



app = Flask(__name__)
 
@app.route('/',methods=['POST'])
def post_data():
    data=request.get_json()
    if data['post_type'] == 'message':
        print(data)
        message=data['message']
        sender=data['sender']['nickname']
        print(message)
        functions.reply(sender,message)
    return 'OK'
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5701)