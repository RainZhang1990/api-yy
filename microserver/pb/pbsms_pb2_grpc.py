# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import pbsms_pb2 as pbsms__pb2


class SmsServiceStub(object):
    # missing associated documentation comment in .proto file
    pass

    def __init__(self, channel):
        """Constructor.

        Args:
          channel: A grpc.Channel.
        """
        self.Send = channel.unary_unary(
            '/pbsms.SmsService/Send',
            request_serializer=pbsms__pb2.SmsRequest.SerializeToString,
            response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
        self.SendInstant = channel.unary_unary(
            '/pbsms.SmsService/SendInstant',
            request_serializer=pbsms__pb2.SmsRequest.SerializeToString,
            response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )


class SmsServiceServicer(object):
    # missing associated documentation comment in .proto file
    pass

    def Send(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendInstant(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SmsServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'Send': grpc.unary_unary_rpc_method_handler(
            servicer.Send,
            request_deserializer=pbsms__pb2.SmsRequest.FromString,
            response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        ),
        'SendInstant': grpc.unary_unary_rpc_method_handler(
            servicer.SendInstant,
            request_deserializer=pbsms__pb2.SmsRequest.FromString,
            response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'pbsms.SmsService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
