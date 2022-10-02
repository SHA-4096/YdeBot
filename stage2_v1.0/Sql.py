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
    def query(self,tag):
#        cursor = self.GetCursor()
        sql = "select tag,CQ from favorite_pics where tag = '%s'"%(tag)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res
    def insert(self,tag,CQ):
        sql = 'insert into favorite_pics(tag,CQ) values(%s,%s)'
        data = [tag,CQ]
        self.cursor.execute(sql,data)
        self.conn.commit()
    def clear(self):
        sql = 'delete from favorite_pics'
        self.cursor.execute(sql)
        self.conn.commit()
    def end(self):
        self.cursor.close()
        self.conn.close()


