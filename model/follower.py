from google.protobuf.json_format import MessageToDict

from libs import zbase62

class Follower(object):
    def __init__(self, pb):
        self.follower_lists = MessageToDict(pb, including_default_value_fields=True, preserving_proto_field_name=True)
        self.follower_lists["space_id"] = zbase62.encode(pb.space_id)
        self.follower_lists["follower_id"] = zbase62.encode(pb.follower_id)
        self.follower_lists["group_id"] = pb.group_id