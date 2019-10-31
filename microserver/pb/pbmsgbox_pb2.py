# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pbmsgbox.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='pbmsgbox.proto',
  package='pbmsgbox',
  syntax='proto3',
  serialized_pb=_b('\n\x0epbmsgbox.proto\x12\x08pbmsgbox\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1cgoogle/protobuf/struct.proto\x1a\x1bgoogle/protobuf/empty.proto\"\x87\x01\n\x19GroupMessageCreateRequest\x12\x18\n\x10group_message_id\x18\x01 \x01(\x03\x12\x12\n\nproduct_id\x18\x02 \x01(\x03\x12+\n\x0cmessage_body\x18\x03 \x01(\x0b\x32\x15.pbmsgbox.MessageBody\x12\x0f\n\x07\x66rom_id\x18\x04 \x01(\x03\"N\n\x0bMessageBody\x12\x11\n\tmsg_title\x18\x01 \x01(\t\x12,\n\x0bmsg_content\x18\x02 \x01(\x0b\x32\x17.google.protobuf.Struct\"\xd5\x01\n\x11MessageAddRequest\x12\x12\n\nmessage_id\x18\x01 \x01(\x03\x12\x12\n\nproduct_id\x18\x02 \x01(\x03\x12\x10\n\x08msg_type\x18\x03 \x01(\x05\x12-\n\x0cmessage_body\x18\x04 \x01(\x0b\x32\x15.pbmsgbox.MessageBodyH\x00\x12\x1a\n\x10group_message_id\x18\x05 \x01(\x03H\x00\x12\x10\n\x08space_id\x18\x06 \x01(\x03\x12\x0f\n\x07\x66rom_id\x18\x07 \x01(\x03\x12\r\n\x05to_id\x18\x08 \x01(\x03\x42\t\n\x07message\"7\n\x12MessageItemRequest\x12\x12\n\nmessage_id\x18\x01 \x01(\x03\x12\r\n\x05to_id\x18\x02 \x01(\x03\"C\n\x12MessageAddRequests\x12-\n\x08messages\x18\x01 \x03(\x0b\x32\x1b.pbmsgbox.MessageAddRequest\"\xdf\x01\n\x07Message\x12\x12\n\nmessage_id\x18\x01 \x01(\x03\x12\x12\n\nproduct_id\x18\x02 \x01(\x03\x12\x10\n\x08msg_type\x18\x03 \x01(\x05\x12+\n\x0cmessage_body\x18\x04 \x01(\x0b\x32\x15.pbmsgbox.MessageBody\x12\x10\n\x08space_id\x18\x05 \x01(\x03\x12\x0f\n\x07\x66rom_id\x18\x06 \x01(\x03\x12\r\n\x05to_id\x18\x07 \x01(\x03\x12\x0c\n\x04read\x18\x08 \x01(\x08\x12-\n\tcreate_at\x18\x0f \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x87\x01\n\x13MessageQueryRequest\x12\x12\n\nproduct_id\x18\x01 \x01(\x03\x12\x10\n\x08msg_type\x18\x02 \x01(\x05\x12\x10\n\x08space_id\x18\x03 \x01(\x03\x12\r\n\x05to_id\x18\x04 \x01(\x03\x12\x17\n\x0f\x66rom_message_id\x18\x05 \x01(\x03\x12\x10\n\x08per_page\x18\x06 \x01(\x03\"Q\n\x14MessageQueryResponse\x12#\n\x08messages\x18\x01 \x03(\x0b\x32\x11.pbmsgbox.Message\x12\x14\n\x0cis_last_page\x18\x02 \x01(\x08\"_\n\x16MessageQueryAllRequest\x12\x12\n\nproduct_id\x18\x01 \x01(\x03\x12\x10\n\x08msg_type\x18\x02 \x01(\x05\x12\x10\n\x08space_id\x18\x03 \x01(\x03\x12\r\n\x05to_id\x18\x04 \x01(\x03\"b\n\x19MessageUnReadCountRequest\x12\x12\n\nproduct_id\x18\x01 \x01(\x03\x12\x10\n\x08msg_type\x18\x02 \x01(\x05\x12\x10\n\x08space_id\x18\x03 \x01(\x03\x12\r\n\x05to_id\x18\x04 \x01(\x03\"+\n\x1aMessageUnReadCountResponse\x12\r\n\x05\x63ount\x18\x01 \x01(\x05\x32\x8e\x05\n\rMsgboxService\x12Q\n\x12\x43reateGroupMessage\x12#.pbmsgbox.GroupMessageCreateRequest\x1a\x16.google.protobuf.Empty\x12;\n\x03\x41\x64\x64\x12\x1c.pbmsgbox.MessageAddRequests\x1a\x16.google.protobuf.Empty\x12\x46\n\x05Query\x12\x1d.pbmsgbox.MessageQueryRequest\x1a\x1e.pbmsgbox.MessageQueryResponse\x12>\n\x06\x44\x65lete\x12\x1c.pbmsgbox.MessageItemRequest\x1a\x16.google.protobuf.Empty\x12\x45\n\tDeleteAll\x12 .pbmsgbox.MessageQueryAllRequest\x1a\x16.google.protobuf.Empty\x12<\n\x04Read\x12\x1c.pbmsgbox.MessageItemRequest\x1a\x16.google.protobuf.Empty\x12\x43\n\x07ReadAll\x12 .pbmsgbox.MessageQueryAllRequest\x1a\x16.google.protobuf.Empty\x12>\n\x06UnRead\x12\x1c.pbmsgbox.MessageItemRequest\x1a\x16.google.protobuf.Empty\x12[\n\x0eGetUnReadCount\x12#.pbmsgbox.MessageUnReadCountRequest\x1a$.pbmsgbox.MessageUnReadCountResponseb\x06proto3')
  ,
  dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,google_dot_protobuf_dot_struct__pb2.DESCRIPTOR,google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,])




_GROUPMESSAGECREATEREQUEST = _descriptor.Descriptor(
  name='GroupMessageCreateRequest',
  full_name='pbmsgbox.GroupMessageCreateRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='group_message_id', full_name='pbmsgbox.GroupMessageCreateRequest.group_message_id', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='product_id', full_name='pbmsgbox.GroupMessageCreateRequest.product_id', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='message_body', full_name='pbmsgbox.GroupMessageCreateRequest.message_body', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='from_id', full_name='pbmsgbox.GroupMessageCreateRequest.from_id', index=3,
      number=4, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=121,
  serialized_end=256,
)


_MESSAGEBODY = _descriptor.Descriptor(
  name='MessageBody',
  full_name='pbmsgbox.MessageBody',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='msg_title', full_name='pbmsgbox.MessageBody.msg_title', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='msg_content', full_name='pbmsgbox.MessageBody.msg_content', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=258,
  serialized_end=336,
)


_MESSAGEADDREQUEST = _descriptor.Descriptor(
  name='MessageAddRequest',
  full_name='pbmsgbox.MessageAddRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message_id', full_name='pbmsgbox.MessageAddRequest.message_id', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='product_id', full_name='pbmsgbox.MessageAddRequest.product_id', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='msg_type', full_name='pbmsgbox.MessageAddRequest.msg_type', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='message_body', full_name='pbmsgbox.MessageAddRequest.message_body', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='group_message_id', full_name='pbmsgbox.MessageAddRequest.group_message_id', index=4,
      number=5, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='space_id', full_name='pbmsgbox.MessageAddRequest.space_id', index=5,
      number=6, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='from_id', full_name='pbmsgbox.MessageAddRequest.from_id', index=6,
      number=7, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='to_id', full_name='pbmsgbox.MessageAddRequest.to_id', index=7,
      number=8, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='message', full_name='pbmsgbox.MessageAddRequest.message',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=339,
  serialized_end=552,
)


_MESSAGEITEMREQUEST = _descriptor.Descriptor(
  name='MessageItemRequest',
  full_name='pbmsgbox.MessageItemRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message_id', full_name='pbmsgbox.MessageItemRequest.message_id', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='to_id', full_name='pbmsgbox.MessageItemRequest.to_id', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=554,
  serialized_end=609,
)


_MESSAGEADDREQUESTS = _descriptor.Descriptor(
  name='MessageAddRequests',
  full_name='pbmsgbox.MessageAddRequests',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='messages', full_name='pbmsgbox.MessageAddRequests.messages', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=611,
  serialized_end=678,
)


_MESSAGE = _descriptor.Descriptor(
  name='Message',
  full_name='pbmsgbox.Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message_id', full_name='pbmsgbox.Message.message_id', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='product_id', full_name='pbmsgbox.Message.product_id', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='msg_type', full_name='pbmsgbox.Message.msg_type', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='message_body', full_name='pbmsgbox.Message.message_body', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='space_id', full_name='pbmsgbox.Message.space_id', index=4,
      number=5, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='from_id', full_name='pbmsgbox.Message.from_id', index=5,
      number=6, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='to_id', full_name='pbmsgbox.Message.to_id', index=6,
      number=7, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='read', full_name='pbmsgbox.Message.read', index=7,
      number=8, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='create_at', full_name='pbmsgbox.Message.create_at', index=8,
      number=15, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=681,
  serialized_end=904,
)


_MESSAGEQUERYREQUEST = _descriptor.Descriptor(
  name='MessageQueryRequest',
  full_name='pbmsgbox.MessageQueryRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='product_id', full_name='pbmsgbox.MessageQueryRequest.product_id', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='msg_type', full_name='pbmsgbox.MessageQueryRequest.msg_type', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='space_id', full_name='pbmsgbox.MessageQueryRequest.space_id', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='to_id', full_name='pbmsgbox.MessageQueryRequest.to_id', index=3,
      number=4, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='from_message_id', full_name='pbmsgbox.MessageQueryRequest.from_message_id', index=4,
      number=5, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='per_page', full_name='pbmsgbox.MessageQueryRequest.per_page', index=5,
      number=6, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=907,
  serialized_end=1042,
)


_MESSAGEQUERYRESPONSE = _descriptor.Descriptor(
  name='MessageQueryResponse',
  full_name='pbmsgbox.MessageQueryResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='messages', full_name='pbmsgbox.MessageQueryResponse.messages', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='is_last_page', full_name='pbmsgbox.MessageQueryResponse.is_last_page', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1044,
  serialized_end=1125,
)


_MESSAGEQUERYALLREQUEST = _descriptor.Descriptor(
  name='MessageQueryAllRequest',
  full_name='pbmsgbox.MessageQueryAllRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='product_id', full_name='pbmsgbox.MessageQueryAllRequest.product_id', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='msg_type', full_name='pbmsgbox.MessageQueryAllRequest.msg_type', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='space_id', full_name='pbmsgbox.MessageQueryAllRequest.space_id', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='to_id', full_name='pbmsgbox.MessageQueryAllRequest.to_id', index=3,
      number=4, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1127,
  serialized_end=1222,
)


_MESSAGEUNREADCOUNTREQUEST = _descriptor.Descriptor(
  name='MessageUnReadCountRequest',
  full_name='pbmsgbox.MessageUnReadCountRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='product_id', full_name='pbmsgbox.MessageUnReadCountRequest.product_id', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='msg_type', full_name='pbmsgbox.MessageUnReadCountRequest.msg_type', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='space_id', full_name='pbmsgbox.MessageUnReadCountRequest.space_id', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='to_id', full_name='pbmsgbox.MessageUnReadCountRequest.to_id', index=3,
      number=4, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1224,
  serialized_end=1322,
)


_MESSAGEUNREADCOUNTRESPONSE = _descriptor.Descriptor(
  name='MessageUnReadCountResponse',
  full_name='pbmsgbox.MessageUnReadCountResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='count', full_name='pbmsgbox.MessageUnReadCountResponse.count', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1324,
  serialized_end=1367,
)

_GROUPMESSAGECREATEREQUEST.fields_by_name['message_body'].message_type = _MESSAGEBODY
_MESSAGEBODY.fields_by_name['msg_content'].message_type = google_dot_protobuf_dot_struct__pb2._STRUCT
_MESSAGEADDREQUEST.fields_by_name['message_body'].message_type = _MESSAGEBODY
_MESSAGEADDREQUEST.oneofs_by_name['message'].fields.append(
  _MESSAGEADDREQUEST.fields_by_name['message_body'])
_MESSAGEADDREQUEST.fields_by_name['message_body'].containing_oneof = _MESSAGEADDREQUEST.oneofs_by_name['message']
_MESSAGEADDREQUEST.oneofs_by_name['message'].fields.append(
  _MESSAGEADDREQUEST.fields_by_name['group_message_id'])
_MESSAGEADDREQUEST.fields_by_name['group_message_id'].containing_oneof = _MESSAGEADDREQUEST.oneofs_by_name['message']
_MESSAGEADDREQUESTS.fields_by_name['messages'].message_type = _MESSAGEADDREQUEST
_MESSAGE.fields_by_name['message_body'].message_type = _MESSAGEBODY
_MESSAGE.fields_by_name['create_at'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_MESSAGEQUERYRESPONSE.fields_by_name['messages'].message_type = _MESSAGE
DESCRIPTOR.message_types_by_name['GroupMessageCreateRequest'] = _GROUPMESSAGECREATEREQUEST
DESCRIPTOR.message_types_by_name['MessageBody'] = _MESSAGEBODY
DESCRIPTOR.message_types_by_name['MessageAddRequest'] = _MESSAGEADDREQUEST
DESCRIPTOR.message_types_by_name['MessageItemRequest'] = _MESSAGEITEMREQUEST
DESCRIPTOR.message_types_by_name['MessageAddRequests'] = _MESSAGEADDREQUESTS
DESCRIPTOR.message_types_by_name['Message'] = _MESSAGE
DESCRIPTOR.message_types_by_name['MessageQueryRequest'] = _MESSAGEQUERYREQUEST
DESCRIPTOR.message_types_by_name['MessageQueryResponse'] = _MESSAGEQUERYRESPONSE
DESCRIPTOR.message_types_by_name['MessageQueryAllRequest'] = _MESSAGEQUERYALLREQUEST
DESCRIPTOR.message_types_by_name['MessageUnReadCountRequest'] = _MESSAGEUNREADCOUNTREQUEST
DESCRIPTOR.message_types_by_name['MessageUnReadCountResponse'] = _MESSAGEUNREADCOUNTRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

GroupMessageCreateRequest = _reflection.GeneratedProtocolMessageType('GroupMessageCreateRequest', (_message.Message,), dict(
  DESCRIPTOR = _GROUPMESSAGECREATEREQUEST,
  __module__ = 'pbmsgbox_pb2'
  # @@protoc_insertion_point(class_scope:pbmsgbox.GroupMessageCreateRequest)
  ))
_sym_db.RegisterMessage(GroupMessageCreateRequest)

MessageBody = _reflection.GeneratedProtocolMessageType('MessageBody', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGEBODY,
  __module__ = 'pbmsgbox_pb2'
  # @@protoc_insertion_point(class_scope:pbmsgbox.MessageBody)
  ))
_sym_db.RegisterMessage(MessageBody)

MessageAddRequest = _reflection.GeneratedProtocolMessageType('MessageAddRequest', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGEADDREQUEST,
  __module__ = 'pbmsgbox_pb2'
  # @@protoc_insertion_point(class_scope:pbmsgbox.MessageAddRequest)
  ))
_sym_db.RegisterMessage(MessageAddRequest)

MessageItemRequest = _reflection.GeneratedProtocolMessageType('MessageItemRequest', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGEITEMREQUEST,
  __module__ = 'pbmsgbox_pb2'
  # @@protoc_insertion_point(class_scope:pbmsgbox.MessageItemRequest)
  ))
_sym_db.RegisterMessage(MessageItemRequest)

MessageAddRequests = _reflection.GeneratedProtocolMessageType('MessageAddRequests', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGEADDREQUESTS,
  __module__ = 'pbmsgbox_pb2'
  # @@protoc_insertion_point(class_scope:pbmsgbox.MessageAddRequests)
  ))
_sym_db.RegisterMessage(MessageAddRequests)

Message = _reflection.GeneratedProtocolMessageType('Message', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGE,
  __module__ = 'pbmsgbox_pb2'
  # @@protoc_insertion_point(class_scope:pbmsgbox.Message)
  ))
_sym_db.RegisterMessage(Message)

MessageQueryRequest = _reflection.GeneratedProtocolMessageType('MessageQueryRequest', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGEQUERYREQUEST,
  __module__ = 'pbmsgbox_pb2'
  # @@protoc_insertion_point(class_scope:pbmsgbox.MessageQueryRequest)
  ))
_sym_db.RegisterMessage(MessageQueryRequest)

MessageQueryResponse = _reflection.GeneratedProtocolMessageType('MessageQueryResponse', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGEQUERYRESPONSE,
  __module__ = 'pbmsgbox_pb2'
  # @@protoc_insertion_point(class_scope:pbmsgbox.MessageQueryResponse)
  ))
_sym_db.RegisterMessage(MessageQueryResponse)

MessageQueryAllRequest = _reflection.GeneratedProtocolMessageType('MessageQueryAllRequest', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGEQUERYALLREQUEST,
  __module__ = 'pbmsgbox_pb2'
  # @@protoc_insertion_point(class_scope:pbmsgbox.MessageQueryAllRequest)
  ))
_sym_db.RegisterMessage(MessageQueryAllRequest)

MessageUnReadCountRequest = _reflection.GeneratedProtocolMessageType('MessageUnReadCountRequest', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGEUNREADCOUNTREQUEST,
  __module__ = 'pbmsgbox_pb2'
  # @@protoc_insertion_point(class_scope:pbmsgbox.MessageUnReadCountRequest)
  ))
_sym_db.RegisterMessage(MessageUnReadCountRequest)

MessageUnReadCountResponse = _reflection.GeneratedProtocolMessageType('MessageUnReadCountResponse', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGEUNREADCOUNTRESPONSE,
  __module__ = 'pbmsgbox_pb2'
  # @@protoc_insertion_point(class_scope:pbmsgbox.MessageUnReadCountResponse)
  ))
_sym_db.RegisterMessage(MessageUnReadCountResponse)



_MSGBOXSERVICE = _descriptor.ServiceDescriptor(
  name='MsgboxService',
  full_name='pbmsgbox.MsgboxService',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=1370,
  serialized_end=2024,
  methods=[
  _descriptor.MethodDescriptor(
    name='CreateGroupMessage',
    full_name='pbmsgbox.MsgboxService.CreateGroupMessage',
    index=0,
    containing_service=None,
    input_type=_GROUPMESSAGECREATEREQUEST,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Add',
    full_name='pbmsgbox.MsgboxService.Add',
    index=1,
    containing_service=None,
    input_type=_MESSAGEADDREQUESTS,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Query',
    full_name='pbmsgbox.MsgboxService.Query',
    index=2,
    containing_service=None,
    input_type=_MESSAGEQUERYREQUEST,
    output_type=_MESSAGEQUERYRESPONSE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Delete',
    full_name='pbmsgbox.MsgboxService.Delete',
    index=3,
    containing_service=None,
    input_type=_MESSAGEITEMREQUEST,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='DeleteAll',
    full_name='pbmsgbox.MsgboxService.DeleteAll',
    index=4,
    containing_service=None,
    input_type=_MESSAGEQUERYALLREQUEST,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Read',
    full_name='pbmsgbox.MsgboxService.Read',
    index=5,
    containing_service=None,
    input_type=_MESSAGEITEMREQUEST,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='ReadAll',
    full_name='pbmsgbox.MsgboxService.ReadAll',
    index=6,
    containing_service=None,
    input_type=_MESSAGEQUERYALLREQUEST,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='UnRead',
    full_name='pbmsgbox.MsgboxService.UnRead',
    index=7,
    containing_service=None,
    input_type=_MESSAGEITEMREQUEST,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='GetUnReadCount',
    full_name='pbmsgbox.MsgboxService.GetUnReadCount',
    index=8,
    containing_service=None,
    input_type=_MESSAGEUNREADCOUNTREQUEST,
    output_type=_MESSAGEUNREADCOUNTRESPONSE,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_MSGBOXSERVICE)

DESCRIPTOR.services_by_name['MsgboxService'] = _MSGBOXSERVICE

# @@protoc_insertion_point(module_scope)
