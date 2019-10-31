# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pbzid.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='pbzid.proto',
  package='pbzid',
  syntax='proto3',
  serialized_pb=_b('\n\x0bpbzid.proto\x12\x05pbzid\"\x1b\n\tIDRequest\x12\x0e\n\x06number\x18\x01 \x01(\x03\"\x19\n\nIDResponse\x12\x0b\n\x03IDs\x18\x01 \x03(\x03\"\x1f\n\x10IDBase58Response\x12\x0b\n\x03IDs\x18\x01 \x03(\t2v\n\nZIDService\x12,\n\x05Query\x12\x10.pbzid.IDRequest\x1a\x11.pbzid.IDResponse\x12:\n\rQueryEncode58\x12\x10.pbzid.IDRequest\x1a\x17.pbzid.IDBase58Responseb\x06proto3')
)




_IDREQUEST = _descriptor.Descriptor(
  name='IDRequest',
  full_name='pbzid.IDRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='number', full_name='pbzid.IDRequest.number', index=0,
      number=1, type=3, cpp_type=2, label=1,
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
  serialized_start=22,
  serialized_end=49,
)


_IDRESPONSE = _descriptor.Descriptor(
  name='IDResponse',
  full_name='pbzid.IDResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='IDs', full_name='pbzid.IDResponse.IDs', index=0,
      number=1, type=3, cpp_type=2, label=3,
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
  serialized_start=51,
  serialized_end=76,
)


_IDBASE58RESPONSE = _descriptor.Descriptor(
  name='IDBase58Response',
  full_name='pbzid.IDBase58Response',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='IDs', full_name='pbzid.IDBase58Response.IDs', index=0,
      number=1, type=9, cpp_type=9, label=3,
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
  serialized_start=78,
  serialized_end=109,
)

DESCRIPTOR.message_types_by_name['IDRequest'] = _IDREQUEST
DESCRIPTOR.message_types_by_name['IDResponse'] = _IDRESPONSE
DESCRIPTOR.message_types_by_name['IDBase58Response'] = _IDBASE58RESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

IDRequest = _reflection.GeneratedProtocolMessageType('IDRequest', (_message.Message,), dict(
  DESCRIPTOR = _IDREQUEST,
  __module__ = 'pbzid_pb2'
  # @@protoc_insertion_point(class_scope:pbzid.IDRequest)
  ))
_sym_db.RegisterMessage(IDRequest)

IDResponse = _reflection.GeneratedProtocolMessageType('IDResponse', (_message.Message,), dict(
  DESCRIPTOR = _IDRESPONSE,
  __module__ = 'pbzid_pb2'
  # @@protoc_insertion_point(class_scope:pbzid.IDResponse)
  ))
_sym_db.RegisterMessage(IDResponse)

IDBase58Response = _reflection.GeneratedProtocolMessageType('IDBase58Response', (_message.Message,), dict(
  DESCRIPTOR = _IDBASE58RESPONSE,
  __module__ = 'pbzid_pb2'
  # @@protoc_insertion_point(class_scope:pbzid.IDBase58Response)
  ))
_sym_db.RegisterMessage(IDBase58Response)



_ZIDSERVICE = _descriptor.ServiceDescriptor(
  name='ZIDService',
  full_name='pbzid.ZIDService',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=111,
  serialized_end=229,
  methods=[
  _descriptor.MethodDescriptor(
    name='Query',
    full_name='pbzid.ZIDService.Query',
    index=0,
    containing_service=None,
    input_type=_IDREQUEST,
    output_type=_IDRESPONSE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='QueryEncode58',
    full_name='pbzid.ZIDService.QueryEncode58',
    index=1,
    containing_service=None,
    input_type=_IDREQUEST,
    output_type=_IDBASE58RESPONSE,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_ZIDSERVICE)

DESCRIPTOR.services_by_name['ZIDService'] = _ZIDSERVICE

# @@protoc_insertion_point(module_scope)
