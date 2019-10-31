import logging
import arrow
import time
import datetime
import json
import grpc
from google.protobuf.timestamp_pb2 import Timestamp

from core.singleton import Singleton
from microserver.pb import pbfeed_pb2
from microserver.mserver import MServer


class FeedServer(metaclass=Singleton):
    async def create_feed(self, feed_id, space_id, creator_id, word, feed_type=None, files=None, location=None,
                          location_name=None, likes_count=0, comments_count=0, feed_size=0, privacy=None, deleted=False,
                          record_at=None, request_id=None):
        """创建 feed

        """
        try:
            date = Timestamp()
            date.FromDatetime(datetime.datetime.strptime(record_at.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"))
            if location_name:
                location = pbfeed_pb2.Point(x=location[0], y=location[1])
                msg = pbfeed_pb2.Feed(feed_id=feed_id, spaces=[pbfeed_pb2.SpaceID(space_id=s) for s in space_id],
                                      creator_id=creator_id, feed_type=feed_type,
                                      word=word, files=json.dumps(files), record_at=date, deleted=deleted,
                                      location=location, location_name=location_name,
                                      likes_count=likes_count, comments_count=comments_count, feed_size=feed_size)
            else:
                msg = pbfeed_pb2.Feed(feed_id=feed_id, spaces=[pbfeed_pb2.SpaceID(space_id=s) for s in space_id],
                                      creator_id=creator_id, feed_type=feed_type,
                                      word=word, files=json.dumps(files), record_at=date, deleted=deleted,
                                      location=None, location_name=None,
                                      likes_count=likes_count, comments_count=comments_count, feed_size=feed_size)

            result = await MServer().call("feed-server", "CreateFeed", msg, request_id)
            return result.is_done, result.message

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def update_feed(self, feed_id, space_id, creator_id, word, location=None,
                          location_name=None, request_id=None):
        try:
            if location_name:
                location = pbfeed_pb2.Point(x=location[0], y=location[1])
                msg = pbfeed_pb2.UpdateFeedRequest(feed_id=feed_id, creator_id=creator_id, word=word,
                                                   location=location, location_name=location_name,
                                                   spaces=[pbfeed_pb2.SpaceID(space_id=s) for s in space_id])
            else:
                msg = pbfeed_pb2.UpdateFeedRequest(feed_id=feed_id, creator_id=creator_id,
                                                   spaces=[pbfeed_pb2.SpaceID(space_id=s) for s in space_id],
                                                   word=word, location=None, location_name=None)

            result = await MServer().call("feed-server", "UpdateFeed", msg, request_id)
            return result.is_done

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def feed_lists(self, space_id, last_feed_id, creator_id, rn=5, request_id=None):
        """ 获取feed流

        :return: 
        """
        try:
            msg = pbfeed_pb2.FeedRequest(space_id=space_id, rn=rn, last_feed_id=last_feed_id, creator_id=creator_id)

            pb_feed_lists = await MServer().call(
                "feed-server", "GetFeedList", msg, request_id)
            return pb_feed_lists

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def delete_feed(self, feed_id, space_id, creator_id, request_id):
        """删除 feed

        :return: 
        """
        try:
            msg = pbfeed_pb2.DeleteFeedRequest(feed_id=feed_id, space_id=space_id, creator_id=creator_id)

            result = await MServer().call(
                "feed-server", "DeleteFeed", msg, request_id)
            return result.is_done, result.message

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def like(self, feed_id, space_id, like_by, request_id):
        """ 点赞

        :return: 
        """
        try:
            msg = pbfeed_pb2.Likes(feed_id=feed_id, space_id=space_id, like_by=like_by)

            result = await MServer().call(
                "feed-server", "CreateLikes", msg, request_id)
            return result.is_done

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def dislike(self, feed_id, space_id, like_by, request_id):
        """ 取消赞
        
        :return: 
        """
        try:
            msg = pbfeed_pb2.Likes(feed_id=feed_id, space_id=space_id, like_by=like_by)

            result = await MServer().call(
                "feed-server", "DeleteLikes", msg, request_id)
            return result.is_done

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_like_list(self, feed_id, space_id, account_id, request_id):
        """ 获取like_by 列表
        
        :param feed_id: 
        :param space_id: 
        :param request_id: 
        :return: like_by[]
        """
        try:
            msg = pbfeed_pb2.LikesRequest(feed_id=feed_id, space_id=space_id, account_id=account_id)

            like_by = await MServer().call(
                "feed-server", "GetLikesLists", msg, request_id)
            return like_by

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def create_comment(self, comment_id, feed_id, space_id, author, word, request_id):
        """ 创建评论
        
        :param comment_id: 
        :param feed_id: 
        :param space_id: 
        :param author: 
        :param word: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbfeed_pb2.Comments(comment_id=comment_id, feed_id=feed_id, space_id=space_id, author=author,
                                      word=word)

            result = await MServer().call(
                "feed-server", "CreateComments", msg, request_id)
            return result.is_done

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def delete_comment(self, comment_id, request_id):
        """ 删除评论
        
        :param comment_id: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbfeed_pb2.CommentID(comment_id=comment_id)

            result = await MServer().call(
                "feed-server", "DeleteComments", msg, request_id)
            return result.is_done

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_comment_list(self, feed_id, account_id, space_id, request_id):
        """ 获取评论列表
        
        :param feed_id: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbfeed_pb2.GetCommentsListsRequest(feed_id=feed_id, account_id=account_id, space_id=space_id)

            pb_comment_list = await MServer().call(
                "feed-server", "GetCommentsLists", msg, request_id)
            return pb_comment_list

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_comment(self, comment_id, account_id, space_id, request_id):
        try:
            msg = pbfeed_pb2.GetCommentRequest(comment_id=comment_id, account_id=account_id, space_id=space_id)

            pb_comment = await MServer().call(
                "feed-server", "GetComment", msg, request_id)
            return pb_comment

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def upsert_last_read(self, space_id, follower_id, last_feed_id, request_id):
        """
        
        :param space_id: 
        :param follower_id: 
        :param last_feed_id: 
        :return: 
        """
        try:
            msg = pbfeed_pb2.LastReadRequest(space_id=space_id, follower_id=follower_id, last_feed_id=last_feed_id)

            result = await MServer().call(
                "feed-server", "UpsertLastRead", msg, request_id)
            return result.is_done

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_last_read(self, space_id, follower_id, request_id):
        """
        
        :param space_id: 
        :param follower_id: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbfeed_pb2.GetLastReadRequest(space_id=space_id, follower_id=follower_id)

            result = await MServer().call(
                "feed-server", "GetLastRead", msg, request_id)
            return result.feed_id

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def likes_is_exists(self, feed_id, space_id, like_by, request_id):
        """

        :param feed_id:
        :param space_id:
        :param like_by:
        :return:
        """
        try:
            msg = pbfeed_pb2.LikesIsExistsRequest(feed_id=feed_id, space_id=space_id, like_by=like_by)

            result = await MServer().call(
                "feed-server", "LikesIsExists", msg, request_id)
            return result.is_done

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def update_likes_count(self, feed_id, value, request_id):
        """
        
        :param feed_id: 
        :param value: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbfeed_pb2.UpdateCountRequest(feed_id=feed_id, value=value)

            result = await MServer().call(
                "feed-server", "UpdateLikesCount", msg, request_id)
            return result

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def update_comments_count(self, feed_id, value, request_id):
        """

        :param feed_id: 
        :param value: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbfeed_pb2.UpdateCountRequest(feed_id=feed_id, value=value)

            result = await MServer().call(
                "feed-server", "UpdateCommentsCount", msg, request_id)
            return result

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def create_photo(self, photo_id, spaces, feed_id, creator_id, filename, filetype, filesize, attributes,
                           feed_record_at, photo_at=None, location=None, location_name=None, likes_count=None,
                           comments_count=None, request_id=None):
        """

        :param photo_id: 
        :param spaces: 
        :param feed_id: 
        :param creator_id: 
        :param filename: 
        :param filetype: 
        :param filesize: 
        :param attributes: 
        :param location: 
        :param location_name: 
        :param likes_count: 
        :param comments_count: 
        :param photo_at: 
        :return: 
        """
        try:
            record_timestamp = Timestamp()
            record_timestamp.FromDatetime(datetime.datetime.utcfromtimestamp(time.mktime(feed_record_at.timetuple())))
            if photo_at:
                photo_timestamp = Timestamp()
                photo_timestamp.FromDatetime(datetime.datetime.utcfromtimestamp(photo_at))
            else:
                photo_timestamp = None
            if filetype == 1:
                filetype = pbfeed_pb2.TYPE_STATIC_PHOTO
            elif filetype == 3:
                filetype = pbfeed_pb2.TYPE_VIDEO

            location = pbfeed_pb2.Point(x=location[0], y=location[1])
            msg = pbfeed_pb2.PhotoInfo(photo_id=photo_id, spaces=[pbfeed_pb2.SpaceID(space_id=s) for s in spaces],
                                       feed_id=feed_id, creator_id=creator_id,
                                       filename=filename, filetype=filetype, filesize=filesize,
                                       attributes=json.dumps(attributes),
                                       location=location, location_name=location_name, likes_count=likes_count,
                                       comments_count=comments_count, photo_at=photo_timestamp,
                                       feed_record_at=record_timestamp)

            result = await MServer().call(
                "feed-server", "CreatePhoto", msg, request_id)
            return result

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def delete_photo(self, photo_id, space_id, creator_id, request_id):
        """

        :param photo_id: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbfeed_pb2.DeletePhotoRequest(photo_id=photo_id, space_id=space_id, creator_id=creator_id)

            result = await MServer().call(
                "feed-server", "DeletePhoto", msg, request_id)
            return result

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_feed_size(self, feed_id, request_id):
        """
        
        :param feed_id: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbfeed_pb2.FeedID(feed_id=feed_id)
            result = await MServer().call("feed-server", "GetFeedSize", msg, request_id)
            return result.feed_size

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def upsert_album(self, space_id, account_id, album_name, photo_count, video_count, create_year, create_month,
                           auto_create,
                           create_date, request_id):
        """
        
        :param space_id: 
        :param album_name: 
        :param photo_count: 
        :param video_count: 
        :param create_year: 
        :param create_month: 
        :param auto_create: 
        :param create_date: 
        :return: 
        """
        try:
            msg = pbfeed_pb2.UpsertAlbumRequest(space_id=space_id, account_id=account_id, album_name=album_name,
                                                photo_count=photo_count, video_count=video_count,
                                                create_year=create_year,
                                                create_month=create_month, auto_create=auto_create,
                                                create_date=create_date)
            result = await MServer().call("feed-server", "UpsertAlbum", msg, request_id)
            return result.is_done

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_album(self, space_id, account_id, request_id):
        """
        
        :param space_id: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbfeed_pb2.GetAlbumRequest(space_id=space_id, account_id=account_id)
            result = await MServer().call("feed-server", "GetAlbum", msg, request_id)
            return result

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_count_daily(self, space_id, account_id, filetype, date, request_id):
        """
        
        :param space_id: 
        :param type: 
        :param date: 
        :return: 
        """
        try:
            date_stamp = Timestamp()
            date_stamp.FromDatetime(datetime.datetime.strptime(date, '%Y-%m-%d'))
            msg = pbfeed_pb2.GetCountDailyRequest(space_id=space_id, account_id=account_id, filetype=filetype,
                                                  date=date_stamp)
            pbcount_daily = await MServer().call("feed-server", "GetCountDaily", msg, request_id)
            return pbcount_daily

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

        return None

    async def get_count_monthly(self, space_id, account_id, filetype, year, month, request_id):
        """

        :param space_id:
        :param type:
        :param date:
        :return:
        """
        try:
            msg = pbfeed_pb2.GetCountMonthlyRequest(space_id=space_id, account_id=account_id, filetype=filetype,
                                                    create_year=year, create_month=month)
            pbcount_daily = await MServer().call("feed-server", "GetCountMonthly", msg, request_id)
            return pbcount_daily

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

        return None

    async def get_last_photo(self, space_id, account_id, filetype, request_id):
        """
        
        :param space_id: 
        :param account_id: 
        :param filetype: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbfeed_pb2.GetLastPhotoRequest(space_id=space_id, account_id=account_id, filetype=filetype)
            result = await MServer().call("feed-server", "GetLastPhoto", msg, request_id)
            return result

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

    async def get_feed_type(self, feed_id, request_id):
        try:
            msg = pbfeed_pb2.FeedID(feed_id=feed_id)
            result = await MServer().call("feed-server", "GetFeedType", msg, request_id)
            return result.feed_type

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

    async def get_feed(self, feed_id, space_id, account_id, request_id):
        try:
            msg = pbfeed_pb2.GetFeedRequest(feed_id=feed_id, space_id=space_id, account_id=account_id)
            result = await MServer().call("feed-server", "GetFeed", msg, request_id)
            return result

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)
