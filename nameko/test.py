from flask import Flask, request

from flasgger import Swagger
import pymysql
from nameko.standalone.rpc import ClusterRpcProxy

app = Flask(__name__)

Swagger(app)

CONFIG = {'AMQP_URI': "amqp://guest:guest@localhost"}

@app.route('/compute', methods=['POST'])

def compute():

    """

    Micro Service Based Compute and Mail API

    This API is made with Flask, Flasgger and Nameko

    ---

    parameters:

      - name: body

        in: body

        required: true

        schema:

          id: data

          properties:

            operation:

              type: string

              enum:

                - sum

                - mul

                - sub

                - div

            email:

              type: string

            value:

              type: integer

            other:

              type: integer

    responses:

      200:

        description: Please wait the calculation, you'll receive an email with results

    """

    Time = request.json.get('time')

    ID = request.json.get('id')

    with ClusterRpcProxy(CONFIG) as rpc:

        # asynchronously spawning and email notification

        a = rpc.TimeSimulate.get(Time, ID)
        
        print(a)
        # asynchronously spawning the compute task

        return msg, 200

#app.run(debug=True)
# with ClusterRpcProxy(CONFIG) as rpc:

#     # asynchronously spawning and email notification

#     a = rpc.PathCalculate.Build('上海', '北京', '100001')
        
#     print(a)
conn = pymysql.connect(host="cdb-518aglpe.bj.tencentcdb.com", port=10101, user="root", password="zyx1999zyx", database="service")
cursor = conn.cursor()  
sql = 'UPDATE `order` SET order_userstate = "t"'
cursor.execute(sql)
conn.commit()
cursor.close()
conn.close()

def connect_mysql():  #链接mysql
  conn = pymysql.connect(host="cdb-518aglpe.bj.tencentcdb.com", port=10101, user="root", password="zyx1999zyx", database="service")
  cursor = conn.cursor()
  return conn,cursor
    # asynchronously spawning the compute task