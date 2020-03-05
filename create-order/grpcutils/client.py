#! /usr/bin/env python
# -*- coding: utf-8 -*-
import grpc
from grpcutils import data_pb2, data_pb2_grpc

_HOST = 'localhost'
_PORT = '5002'

def run(begin_place, end_place, id):
    conn = grpc.insecure_channel(_HOST + ':' + _PORT)
    client = data_pb2_grpc.RouteBuildStub(channel=conn)
    response = client.Build(data_pb2.order_place(begin_place=begin_place, end_place=end_place, id=id))
    print("received: " + response.ok)
    return response.ok

if __name__ == '__main__':
    run()