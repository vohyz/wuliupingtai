from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask_restful import Api, Resource, reqparse
import datetime
import pymysql
import random

app = Flask(__name__)
api = Api(app)
cors = CORS(app)
class User_login(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('userphone', type=str)
        self.parser.add_argument('sms_code', type=str)

    def get(self):
        data = self.parser.parse_args()
        userphone = data.get('userphone')
        sms_code = data.get('sms_code')
        message = self.login_in(userphone, sms_code)
        return message

    def login_in(self, userphone, sms_code):

        conn,cursor = connect_mysql()                       # 连接到mysql

        try:                                                # 判断验证码是否通过
            sql = 'SELECT phonenumber,code from sms_code'
            cursor.execute(sql)
            p_code = cursor.fetchall()
            #print(p_code)
            #print((userphone, sms_code) )
            if (userphone, sms_code) in p_code:             # 验证码通过
                try:                                        # 判断手机是否已被注册
                    sql = 'SELECT user_phone from user'
                    cursor.execute(sql)
                    phonenumbers = cursor.fetchall()
                    if (userphone,) in phonenumbers:        # 如果手机号已存在，则直接登录
                        pass
                    else:                                   # 如不存在则存入数据库再登录
                        sql = 'INSERT into user VALUES (%s,%s,%s)'
                        args = ('Null', 'Null', userphone)
                        cursor.execute(sql, args)
                        pass
                    conn.commit()
                    cursor.close()
                    conn.close()
                    return {'errno':'ok', 'errmsg':"登录成功"}
                except Exception as e:
                    return {'errno':'notok', 'errmsg':"用户数据读取失败"}
            else:                                           # 验证码不通过
                return {'errno':'notok', 'errmsg':"验证码错误"}
        except Exception as e:
            return {'errno':'notok','errmsg':"数据库查询错误"}

class Send_sms(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('userphone', type=str)

    def get(self):
        data = self.parser.parse_args()
        userphone = data.get('userphone')
        message = self.sms_code(userphone)
        return message

    def sms_code(self, userphone):                                         # 发送验证码
        
        mobile = userphone

        conn,cursor = connect_mysql()                       # 连接到mysql

        result = random.randint(0, 999999)                  # 生成验证码
        sms_code = "%06d" % result
        print("验证码：{}".format(sms_code))


        try:                                                # 调用阿里云去发送短信
            getaliyun(mobile, sms_code)
        except Exception as e:
            return {'errno':'databaseerror', 'errmsg':"发送短信失败"}

        try:                                                # 将手机号和验证码存入数据库
            sql = 'SELECT phonenumber from sms_code'
            cursor.execute(sql)
            phonenumbers = cursor.fetchall()
            if (mobile,) in phonenumbers:
                sql = 'UPDATE sms_code SET code = %s WHERE phonenumber = %s'
                args = (sms_code, mobile)
            else:
                sql = 'INSERT into sms_code VALUES (%s,%s)'
                args = (mobile, sms_code)
            result = cursor.execute(sql, args)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            return {'errno':'codestoreerror', 'errmsg':"手机验证码保存失败"}

        return {'errno':'ok', 'errmsg':"发送成功"}

def getaliyun(phonenumber, code):#调用阿里云去发送短信
  
    response = client.do_action(request)
    print(str(response, encoding = 'utf-8'))

def connect_mysql():#链接mysql
    conn = pymysql.connect(host="cdb-518aglpe.bj.tencentcdb.com", port=10101, user="root", password="zyx1999zyx", database="service")
    cursor = conn.cursor() 
    return conn,cursor


api.add_resource(User_login, '/login')
api.add_resource(Send_sms, '/sms')

if __name__ == '__main__':
    app.run(debug=True, port = 5004)        
