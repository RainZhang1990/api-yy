from google.protobuf.json_format import MessageToDict

from libs import zbase62
import json

class Feed(object):
    def __init__(self, pb):
        self.feed = MessageToDict(pb, including_default_value_fields=True, preserving_proto_field_name=True)
        self.feed["feed_id"] = zbase62.encode(pb.feed_id)
        self.feed["creator_id"] = zbase62.encode(pb.creator_id)
        self.feed["spaces"] = [zbase62.encode(int(s["space_id"])) for s in self.feed["spaces"]]
        self.feed["privacy"] = [int(s["group_id"]) for s in self.feed["privacy"]]
        self.feed["location"] = [round(pb.location.x, 8), round(pb.location.y, 8)]
        self.feed["feed_type"] = pb.feed_type
        if pb.feed_type == 2:
            files = json.loads(self.feed["files"])[0]
            exchange = files.get('width')
            files['width'] = files.get('width') if files.get('rotate') in (0, 180) else files.get('height')
            files['height'] = files.get('height') if files.get('rotate') in (0, 180) else exchange
            self.feed["files"] = [files] if self.feed["files"] else None
        else:
            self.feed["files"] = [file for file in json.loads(self.feed["files"])] if self.feed["files"] else None

class Comment(object):
    def __init__(self, pb):
        self.comment = MessageToDict(pb, including_default_value_fields=True, preserving_proto_field_name=True)
        self.comment["comment_id"] = zbase62.encode(pb.comment_id)
        self.comment["feed_id"] = zbase62.encode(pb.feed_id)
        self.comment["space_id"] = zbase62.encode(pb.space_id)
        self.comment["author_id"] = zbase62.encode(pb.author)

class Album(object):
    def __init__(self, pb):
        self.album = MessageToDict(pb, including_default_value_fields=True, preserving_proto_field_name=True)
        self.album["year"] = pb.year
        self.album["month"] = pb.month
        self.album["photo_count"] = pb.photo_count
        self.album["video_count"] = pb.video_count
        self.album["album_name"] = pb.album_name
        self.album["cover_photo"] = pb.cover_photo
        self.album["filetype"] = pb.filetype

class CountDaily(object):
     def __init__(self, pb):
        self.count_daily = MessageToDict(pb, including_default_value_fields=True, preserving_proto_field_name=True)
        self.count_daily["url"] = pb.url
        self.count_daily["attributes"] = json.loads(pb.attributes)


