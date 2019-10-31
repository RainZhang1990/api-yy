from google.protobuf.json_format import MessageToDict

class Vaccine(object):
    def __init__(self, pb):
        self.vaccine = MessageToDict(pb, including_default_value_fields=True, preserving_proto_field_name=True)


class InjectDetail(object):
    def __init__(self, pb):
        self.inject_detail = MessageToDict(pb, including_default_value_fields=True, preserving_proto_field_name=True)
