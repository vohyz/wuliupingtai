from flask import Flask
from flask_cors import CORS, cross_origin
from flask_restful import Api, Resource, reqparse
import threading
import time
import pymysql

app = Flask(__name__)
api = Api(app)
cors = CORS(app)

# 时间模拟器
class write(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('Time', type=str)
        self.parser.add_argument('ID', type=str)

    def timer(self, Time, id):
        for i in Time:
            time.sleep(i)
            now = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))  # 当前时间
            # 打开数据库连接
            db = pymysql.connect(host="cdb-518aglpe.bj.tencentcdb.com", port=10101, user="root", password="zyx1999zyx",
                                database="service")
            # 使用cursor()方法获取操作游标
            cursor = db.cursor()

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
        db = pymysql.connect(host="cdb-518aglpe.bj.tencentcdb.com", port=10101, user="root", password="zyx1999zyx",
                                database="service")
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()

        sql = "UPDATE `order` SET `order_state` = %s where `order_id` = %s"
        value = ('已完成', id)
            
        cursor.execute(sql, value)
        db.commit()
        cursor.close()  # 关闭游标
        db.close()

    def get(self):
        data = self.parser.parse_args()
        Time = list(map(int, data.get('Time').split()))
        ID = data.get('ID')

        print(Time, ID)

        timer = threading.Thread(target=self.timer, args=(Time, ID))
        timer.start()

        return {'ok': ID}


api.add_resource(write, '/')

if __name__ == '__main__':
    app.run(debug=True, port= 5003)
