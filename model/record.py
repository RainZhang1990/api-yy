from google.protobuf.json_format import MessageToDict
import time

class GrowthDetail(object):
    def __init__(self, pb):
        self.growth_detail = MessageToDict(pb, including_default_value_fields=True, preserving_proto_field_name=True)
        self.growth_detail["height"] = pb.height if pb.height != 0.0 else None
        self.growth_detail["weight"] = pb.weight if pb.weight != 0.0 else None
        self.growth_detail["head_circumference"] = pb.head_circumference if pb.head_circumference != 0.0 else None
        self.growth_detail["bmi"] = pb.bmi if pb.bmi != 0.0 else None
        self.growth_detail["record_at"] = time.strftime('%Y-%m-%d', time.localtime(pb.record_at.seconds))