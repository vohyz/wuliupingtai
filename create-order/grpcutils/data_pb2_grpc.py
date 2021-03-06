# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from grpcutils import data_pb2 as data__pb2


class RouteBuildStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Build = channel.unary_unary(
        '/RouteBuild/Build',
        request_serializer=data__pb2.order_place.SerializeToString,
        response_deserializer=data__pb2.return_message.FromString,
        )


class RouteBuildServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Build(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_RouteBuildServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Build': grpc.unary_unary_rpc_method_handler(
          servicer.Build,
          request_deserializer=data__pb2.order_place.FromString,
          response_serializer=data__pb2.return_message.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'RouteBuild', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
