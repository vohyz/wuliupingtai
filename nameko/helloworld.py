from nameko.rpc import rpc, RpcProxy

import threading
import time

from concurrent import futures
import random
import json, urllib
from urllib import parse
from urllib.request import urlopen

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import datetime

import pymysql

class TimeSimulate(object):
    name = "TimeSimulate"
    def timer(self, Time, id):
        for i in Time:
            time.sleep(i)
            now = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))  # 当前时间
            # 打开数据库连接
            db, cursor = connect_mysql()

            sql = "select transport_time from `order` where `order_id` = %s"
            args = id
            cursor.execute(sql, args)
            tuple_time = cursor.fetchone()
            order_time = tuple_time[0]
            print(order_time)
            order_time += ' '
            order_time += now
            sql = "UPDATE `order` SET transport_time = %s where `order_id` = %s"
            value = (order_time, id)

            # cursor.execute(sql)
            cursor.execute(sql, value)
            db.commit()
            cursor.close()  # 关闭游标
            db.close()

        db, cursor = connect_mysql()

        sql = "UPDATE `order` SET `order_state` = %s where `order_id` = %s"
        value = ('已完成', id)
            
        cursor.execute(sql, value)
        db.commit()
        cursor.close()  # 关闭游标
        db.close()

    @rpc
    def get(self, Time, ID):
        Time = list(map(int, Time.split()))
        ID = ID

        print(Time, ID)

        timer = threading.Thread(target=self.timer, args=(Time, ID))
        timer.start()

        return {'ok': ID}

class PathCalculate(object):
    name = 'PathCalculate'
    Timer = RpcProxy("TimeSimulate")

    def GetDistance(self, x1, x2, y1, y2):
        x = x1 - x2
        y = y1 - y2

        distance = ((x ** 2) + (y ** 2)) ** 0.5 // 10
        return distance

    @rpc
    def Build(self, begin_place, end_place, id):
        print('收到消息:' + begin_place + end_place + id)
        # 获取起点
        try:
            connect, cursor = connect_mysql()
            sql1 = 'select * from place where place_name = %s'
            args1 = begin_place
            cursor.execute(sql1, args1)
            place1 = cursor.fetchone()
            connect.commit()
            cursor.close()
            connect.close()
        except:
            return 'place_name_error'
        # 获取终点
        try:
            connect, cursor = connect_mysql()
            sql2 = 'select * from place where place_name = %s'
            args2 = end_place
            cursor.execute(sql2, args2)
            place2 = cursor.fetchone()
            connect.commit()
            cursor.close()
            connect.close()
        except:
            return 'place_name_error'

        if place1[1]<place2[1]:
            x1,x2 = place1[1],place2[1]
        else:
            x1,x2 = place2[1],place1[1]

        if place1[2]<place2[2]:
            y1,y2 = place1[2],place2[2]
        else:
            y1,y2 = place2[2],place1[2]
        # 获取随机点
        connect, cursor = connect_mysql()
        sql3 = 'select * from place where (place_x between %s and %s) and (place_y between %s and %s)'
        args3 = (x1 + 1, x2 - 1, y1 + 1, y2 - 1)
        cursor.execute(sql3,args3)
        place_in = cursor.fetchmany(random.randint(3, 5))
        connect.commit()
        cursor.close()
        connect.close()

        placefaker = []
        for i in place_in:
            placefaker.append(list(i))
        if place1[1]>place2[1]:
            flag = True
        else:
            flag = False
        place_better_in = sorted(placefaker,key=lambda x:x[1],reverse=flag)
        place_all = [place1] + place_better_in + [place2]
        print(place_all)
        size = len(place_all)
        print('起点为' + place_all[0][0])
        order_time = ''
        order_place = ''

        for i in range(size - 1):
            x = str(int(self.GetDistance(place_all[i][1], place_all[i + 1][1], place_all[i][2], place_all[i + 1][2])))
            order_time += ' '
            order_time += x
            order_place += ' '
            order_place += place_all[i][0]
            state = place_all[i+1][0]
            print('经过' + str(x) + '到达了' + state)

        order_place += ' ' + place_all[-1][0]

        connect, cursor = connect_mysql()
        sql4 = 'UPDATE `order` set transport_place = %s where `order_id` = %s'
        args4 = (order_place, id)
        cursor.execute(sql4, args4)
        connect.commit()
        cursor.close()
        connect.close()

        params = {
            "Time": order_time,
            "ID": id
        }
        print(id)
        self.Timer.get(order_time, id)

        return 'ok'

class User_login(object):
    name = 'User_login'
    @rpc
    def login(self, userphone, sms_code):

        conn, cursor = connect_mysql()                       # 连接到mysql

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

class Send_sms(object):
    name = 'Send_sms'
    @rpc
    def send(self, userphone):                                         # 发送验证码
        
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

# 创建订单类
class Order_create(object):
    name = 'Order_create'
    Path = RpcProxy("PathCalculate")

    @rpc
    def create(self, params):
        begin_name = params['order_begin_name']
        begin_phone = params['order_begin_phone']
        begin_city = params['order_begin_city']
        end_name = params['order_end_name']
        end_phone = params['order_end_phone']
        end_city = params['order_end_city']
        '''
        此处可能需要支付
        '''
        conn, cursor = connect_mysql()  # 连接到mysql

        sql = 'SELECT max(`order_id`) from `order`'
        cursor.execute(sql)
        orders = cursor.fetchone()
        neworder_id = orders[0] + 1
        try:
            sql = 'INSERT into `order` VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            args = (pymysql.escape_string(str(neworder_id)), \
                    pymysql.escape_string(t), pymysql.escape_string(begin_name), \
                    pymysql.escape_string(begin_phone), pymysql.escape_string(end_name), \
                    pymysql.escape_string(end_phone), pymysql.escape_string(begin_city), \
                    pymysql.escape_string(end_city), pymysql.escape_string('进行中'), \
                    pymysql.escape_string(t), pymysql.escape_string(begin_city), \
                    pymysql.escape_string('已出发'), 't')
            cursor.execute(sql, args)
            conn.commit()
            cursor.close()
            conn.close()
            # 与生成路径模块通过rpc通信
            return_message = self.Path.Build(begin_city, end_city, str(neworder_id).encode('UTF-8'))

            return {'rst': return_message}

        except Exception as e:
            print(e)
            return {'rst': False}

# 删除订单类
class Order_delete(object):
    name = 'Order_delete'

    @rpc
    def delete(self, order_id):
        conn, cursor = connect_mysql()  # 连接到mysql
        try:
            sql = 'UPDATE `order` SET `order_userstate` = "f" WHERE `order_id` = %s'
            args = (order_id)
            print(sql)
            cursor.execute(sql, args)
            conn.commit()
            cursor.close()
            conn.close()

            return {'rst': 'ok'}

        except Exception as e:
            print(e)
            return {'rst': False}

# 搜索订单（按订单号）类
class Order_searchbyOrder(object):
    name = 'Order_searchbyOrder'

    @rpc
    def search(self, order_id):
        command = ''
        if len(order_id) <= 10:
            command = '`order_id` = ' + order_id
        else:
            orders = order_id.split()
            item = '`order_id` = ' + orders[0]
            command += item
            for i in orders[1:]:
                item = ' or `order_id` = ' + i
                command += item
        try:
            conn,cursor = connect_mysql()                       # 连接到mysql
            sql = 'SELECT * FROM `order` WHERE `order_userstate` <> "f" and (%s)'%command
            print(sql)
            cursor.execute(sql)
            orders = cursor.fetchall()
            conn.commit()
            cursor.close()
            conn.close()
            params = {
            'orders':[
                {
            'order_id':order[0],
            'begin_time_1':order[1][:11],
            'begin_time_2':order[1][11:],
            'begin_name':order[2],
            'begin_phone':order[3],
            'end_name':order[4],
            'end_phone':order[5],
            'begin_city':order[6],
            'end_city':order[7],
            'order_state':order[8],
            'order_transport_time':order[9],
            'order_transport_place':order[10]
            }
            for order in orders]
            }
            return {
                'order_message': params,
                'error_message': '0'
                }
        except:
            return {
                'order_message': '0',
                'error_message': 'error'
                }

# 搜索订单（按用户）类
class Order_searchbyUser(object):
    name = 'Order_searchbyUser'
    
    @rpc
    def search(self, userphone):
        try:
            conn,cursor = connect_mysql()           # 连接到mysql
            sql = 'SELECT * from `order` where `order_userstate` <> "f" and (begin_user_phone = %s)'%userphone
            cursor.execute(sql) 
            orders = cursor.fetchall()
            conn.commit()
            cursor.close()
            conn.close()
            params = {
            'orders':[
                {
            'order_id':order[0],
            'begin_time_1':order[1][:11],
            'begin_time_2':order[1][11:],
            'begin_name':order[2],
            'begin_phone':order[3],
            'end_name':order[4],
            'end_phone':order[5],
            'begin_city':order[6],
            'end_city':order[7],
            'order_state':order[8],
            'order_transport_time':order[9],
            'order_transport_place':order[10]
            }
            for order in orders]
            }
            return {
                'order_message': params,
                'error_message': '0'
                }
        except:
            return {
                'order_message': '0',
                'error_message': 'error'
                }
class Get_Address(object):
    name = 'Get_Address'
    
    @rpc
    def get(self, userphone):
        conn,cursor = connect_mysql()           # 连接到mysql
        sql = 'SELECT `address` from user_address where user_phone = %s'%userphone
        cursor.execute(sql) 
        address = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        print(address)
                                                # 此处需要补异常处理，限于时间原因以后再补
        return address

class Change_Address(object):
    name = 'Change_Address'

    @rpc
    def add(self, userphone, address):
        conn,cursor = connect_mysql()           # 连接到mysql
        sql = 'INSERT INTO user_address VALUES (%s, \"%s\")'%(userphone, address)
        cursor.execute(sql) 
        print(sql)
        conn.commit()
        cursor.close()
        conn.close()                   # 此处需要补异常处理，限于时间原因以后再补
        return 'ok'

    @rpc
    def change(self, userphone, oldaddress, newaddress):
        conn,cursor = connect_mysql()           # 连接到mysql
        sql = 'UPDATE user_address SET `address` = \"%s\" where user_phone = %s and `address` = \"%s\"'%(newaddress, userphone, oldaddress)
        print(sql)
        cursor.execute(sql) 
        
        conn.commit()
        cursor.close()
        conn.close()                   # 此处需要补异常处理，限于时间原因以后再补
        return 'ok'

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
    conn = pymysql.connect(host="cdb-518aglpe.bj.tencentcdb.com", port=10101, user="root", password="zyx1999zyx", database="service")
    cursor = conn.cursor()
    return conn, cursor