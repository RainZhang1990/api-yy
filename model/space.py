from google.protobuf.json_format import MessageToDict
from libs import zbase62


class SpaceInfo(object):
     def __init__(self, pb_space):
        self.spaceinfo = MessageToDict(pb_space, including_default_value_fields=True,
                                       preserving_proto_field_name=True)
        self.spaceinfo["space_id"] = zbase62.encode(pb_space.space_id)
        self.spaceinfo["owner_id"] = zbase62.encode(pb_space.owner_id)
        self.spaceinfo["create_by"] = zbase62.encode(pb_space.create_by)


class Group(object):
    def __init__(self, pb_group):
        self.groupinfo = MessageToDict(pb_group, including_default_value_fields=True,
                                       preserving_proto_field_name=True)
        self.groupinfo["group_id"] = pb_group.group_id
        self.groupinfo["space_id"] = zbase62.encode(pb_group.space_id)


class Relation(object):
    def __init__(self, pb_group):
        self.relationinfo = MessageToDict(pb_group, including_default_value_fields=True,
                                          preserving_proto_field_name=True)
