from flask import Flask
from flask_cors import CORS, cross_origin
from flask_restful import Api, Resource, reqparse
import datetime
import pymysql
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import datetime
import random

app = Flask(__name__)
api = Api(app)
cors = CORS(app)

class Send_sms(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('userphone', type=str)

    def post(self):                                         # 发送验证码
        data = self.parser.parse_args()
        userphone = data.get('userphone')
        mobile = userphone
        conn,cursor = connect_mysql()                       # 连接到mysql
        result = random.randint(0, 999999)                  # 生成验证码
        sms_code = "%06d" % result
        print("验证码：{}".format(sms_code))

        try:                                                # 将手机号和验证码存入数据库
            sql = 'SELECT user_phone from Code'
            cursor.execute(sql)
            phonenumbers = cursor.fetchall()
            t = datetime.datetime.now()
            print(t)
            if (mobile,) in phonenumbers:
                sql = 'UPDATE Code SET code = %s, addtime = %s WHERE user_phone = %s'
                args = (sms_code, t, mobile)
            else:
                sql = 'INSERT into Code (user_phone, addtime, code) VALUES (%s, %s, %s)'
                args = (mobile, t, sms_code)
            result = cursor.execute(sql, args)
            conn.commit()
            cursor.close()
            conn.close()
            try:                                                # 调用阿里云去发送短信
                getaliyun(mobile, sms_code)
            except Exception as e:
                print(e)
                return {'errno':'databaseerror', 'errmsg':"发送短信失败"}
        except Exception as e:
            print(e)
            return {'errno':'codestoreerror', 'errmsg':"手机验证码保存失败"}

        return {'errno':'ok', 'errmsg':"发送成功"}
def getaliyun(phonenumber, code):#调用阿里云去发送短信
    client = AcsClient('LTAI4FomtQh5Gs5d8fSGkZ4i', 'ADe4EjDzszIRWTxZkj9Ej5M3GntIDW', 'cn-hangzhou')
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https') # https | http
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('RegionId', "cn-hangzhou")
    request.add_query_param('PhoneNumbers', phonenumber)
    request.add_query_param('SignName', "vohyz")
    request.add_query_param('TemplateCode', "SMS_177242135")
    request.add_query_param('TemplateParam', "{\"code\":\"%s\"}"%code)

    response = client.do_action(request)
    print(str(response, encoding = 'utf-8'))

def connect_mysql():#链接mysql
    conn = pymysql.connect(host="cdb-mw8hntaa.bj.tencentcdb.com", port=10027, user="root", password="lx123456", database="SE-Platform")
    cursor = conn.cursor()
    return conn, cursor

api.add_resource(Send_sms, '/sms')

def post(userphone):                                         # 发送验证码
    mobile = userphone
    conn,cursor = connect_mysql()                       # 连接到mysql
    result = random.randint(0, 999999)                  # 生成验证码
    sms_code = "%06d" % result
    print("验证码：{}".format(sms_code))

    try:                                                # 将手机号和验证码存入数据库
        sql = 'SELECT user_phone from Code'
        cursor.execute(sql)
        phonenumbers = cursor.fetchall()
        t = datetime.datetime.now()
        t = t.strftime("%Y-%m-%d %H:%M:%S")
        if (mobile,) in phonenumbers:
            sql = 'UPDATE Code SET code = %s, addtime = %s WHERE user_phone = %s'
            args = (sms_code, t, mobile)
        else:
            sql = 'INSERT into Code (user_phone, addtime, code) VALUES (%s, %s, %s)'
            args = (mobile, t, sms_code)
        result = cursor.execute(sql, args)
        conn.commit()
        cursor.close()
        conn.close()
        try:                                                # 调用阿里云去发送短信
            getaliyun(mobile, sms_code)
        except Exception as e:
            print(e)
            return {'errno':'databaseerror', 'errmsg':"发送短信失败"}
    except Exception as e:
        print(e)
        return {'errno':'codestoreerror', 'errmsg':"手机验证码保存失败"}

    return {'errno':'ok', 'errmsg':"发送成功"}

if __name__ == '__main__':
    # app.run(debug=True, port= 5001)
    print(post('15316172791'))