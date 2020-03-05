from flask import Flask
from flask_cors import CORS, cross_origin
from flask_restful import Api, Resource, reqparse
import datetime
import time
import pymysql
from nameko.standalone.rpc import ClusterRpcProxy

app = Flask(__name__)
api = Api(app)
cors = CORS(app)
CONFIG = {'AMQP_URI': "amqp://guest:guest@localhost"}

# 创建订单类
class Order_create(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('orders', type=list)
        self.parser.add_argument('order_begin_name', type=str)
        self.parser.add_argument('order_begin_phone', type=str)
        self.parser.add_argument('order_begin_city', type=str)
        self.parser.add_argument('order_end_name', type=str)
        self.parser.add_argument('order_end_phone', type=str)
        self.parser.add_argument('order_end_city', type=str)

    def get(self):
        data = self.parser.parse_args()
        orders = data.get('orders')
        rst = []
        for order in orders:
            rst.append(self.create(order))
        return {'rst': rst}

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
            sql = 'INSERT into `order` VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            args = (pymysql.escape_string(str(neworder_id)), \
                    pymysql.escape_string(t), pymysql.escape_string(begin_name), \
                    pymysql.escape_string(begin_phone), pymysql.escape_string(end_name), \
                    pymysql.escape_string(end_phone), pymysql.escape_string(begin_city), \
                    pymysql.escape_string(end_city), pymysql.escape_string('进行中'), \
                    pymysql.escape_string(t), pymysql.escape_string(begin_city), \
                    pymysql.escape_string('已出发'))
            cursor.execute(sql, args)
            conn.commit()
            cursor.close()
            conn.close()
            # 与生成路径模块通过grpc通信
            with ClusterRpcProxy(CONFIG) as rpc:
                return_message = rpc.PathCalculate.Build(begin_city, end_city, str(neworder_id).encode('UTF-8'))
            return return_message

        except Exception as e:
            print(e)
            return False

# 搜索订单（按订单号）类
class Order_searchbyOrder(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('order_id', type=str)

    def get(self):
        data = self.parser.parse_args()
        order_id = data.get('order_id')
        orders = self.search(order_id)
        #print(orders)
        
        if orders != 'error':
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
                    'order_transport_place':order[10],
                    }
                for order in orders]
            }
            return {
                'order_message': params,
                'error_message': '0'
                }
        else:
            return {
                'order_message': '0',
                'error_message': 'error'
                }

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
            sql = 'SELECT * FROM `order` WHERE %s'%command
            print(sql)
            cursor.execute(sql)
            orders = cursor.fetchall()
            conn.commit()
            cursor.close()
            conn.close()
            return orders
        except:
            return 'error'

# 搜索订单（按用户）类
class Order_searchbyUser(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('userphone', type=str)

    def get(self):
        data = self.parser.parse_args()
        order_id = data.get('userphone')

        orders = self.search(order_id)

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
        if orders != 'error':
            return {
                'order_message': params,
                'error_message': '0'
                }
        else:
            return {
                'order_message': '0',
                'error_message': 'error'
                }

    def search(self, userphone):
        try:
            conn,cursor = connect_mysql()           # 连接到mysql
            sql = 'SELECT * from `order` where begin_user_phone = %s'%userphone
            cursor.execute(sql) 
            orders = cursor.fetchall()
            conn.commit()
            cursor.close()
            conn.close()
            return orders
        except:
            return 'error'

def connect_mysql():# 链接mysql
    conn = pymysql.connect(host="cdb-518aglpe.bj.tencentcdb.com", port=10101, user="root", password="zyx1999zyx", database="service")
    cursor = conn.cursor()
    return conn,cursor

api.add_resource(Order_create, '/create/')
api.add_resource(Order_searchbyOrder, '/searchbyOrder/')
api.add_resource(Order_searchbyUser, '/searchbyUser/')

if __name__ == '__main__':
    app.run(debug=True, port= 5001)