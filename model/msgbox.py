from google.protobuf.json_format import MessageToDict
from libs import zbase62

class MsgBox(object):
    def __init__(self, pb):
        self.msgbox = MessageToDict(pb, including_default_value_fields=True, preserving_proto_field_name=True)
