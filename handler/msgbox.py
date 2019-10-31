from libs import validator
from .api import APIHandler
from .api import authenticated_async
from tornado.web import HTTPError
from core.config import Config
from core import redis as rd
from core import backend
from microserver.server.feed import FeedServer
from microserver.server.msgbox import MsgBoxServer
from microserver.server.space import SpaceServer
from microserver.server.zid import ZIDServer
from microserver.server.account import AccountServer
from model.account import UserInfo
from model.msgbox import MsgBox
from model.feed import Feed
from libs import zbase62


class Center(APIHandler):
    @authenticated_async
    async def post(self):
        message_center_list = []
        type_name = {0: "日记", 1: "照片", 2: "视频", 3: "音频", 4: "故事", 5: "生长发育"}  # feed 类型
        system_pbmsg = await MsgBoxServer().query_message(product_id=Config().product,
                                                          to_id=self.current_user.account_id,
                                                          per_page=1,
                                                          space_id=0,
                                                          request_id=self.request_id,
                                                          msg_type=Config().msgbox.get("msg_type").get("system"),
                                                          )

        if system_pbmsg:
            if MsgBox(system_pbmsg).msgbox.get("messages"):
                unread = await MsgBoxServer().get_unread_count(product_id=Config().product,
                                                               msg_type=Config().msgbox.get("msg_type").get("system"),
                                                               to_id=self.current_user.account_id,
                                                               request_id=self.request_id)

                last_message = MsgBox(system_pbmsg).msgbox.get("messages")[-1]
                message_center_list.append(
                    {
                        "title": "系统消息",
                        "space_id": zbase62.encode(0),
                        "avatar": "",
                        "unread": unread,
                        "from_id": zbase62.encode(self.current_user.account_id),
                        "latest_message": {
                            "msg_type": Config().msgbox.get("msg_type").get("system"),
                            "content": last_message.get("message_body").get("msg_content").get(
                                "body") if last_message.get("message_body").get("msg_content") else "",
                            "create_at": last_message.get("create_at"),
                            "message_id": zbase62.encode(int(last_message.get("message_id")))
                        }
                    })

        # 　获取所有关注的space空间
        pb_space = await SpaceServer().get_all_space(follower_id=self.current_user.account_id,
                                                     request_id=self.request_id)

        for space in pb_space.space_details:
            if space.status == 0:
                pb_userinfo = await AccountServer().get_userinfo(account_id=space.owner_id, app_id=self.app_id_int64,
                                                                 request_id=self.request_id)
                title = "{}的动态".format(pb_userinfo.nickname)
                userinfo = UserInfo(pb_userinfo)
                avatar_name = userinfo.__dict__.get('userinfo').get('avatar')
                if avatar_name:
                    baby_avatar, error = await backend.backend_user_media.get_public_url(avatar_name)
                else:
                    baby_avatar = ""

                unread = 0  # 未读消息数
                pbmsg = await MsgBoxServer().query_message(product_id=Config().product,
                                                           to_id=self.current_user.account_id,
                                                           per_page=1,
                                                           request_id=self.request_id,
                                                           msg_type=Config().msgbox.get("msg_type").get("feed"),
                                                           space_id=space.space_id)

                if pbmsg:
                    if MsgBox(pbmsg).msgbox.get("messages"):
                        last_message = MsgBox(pbmsg).msgbox.get("messages")[0]
                        last_message['message_id'] = zbase62.encode(int(last_message.get("message_id")))

                        del last_message['product_id'], last_message['space_id']
                        feed_type = None
                        if last_message.get("message_body").get("msg_content").get("feed_id"):
                            feed_id = MsgBox(pbmsg).msgbox.get("messages")[-1].get("message_body").get(
                                "msg_content").get("feed_id")
                            last_message['message_body']['msg_content']['feed_id'] = zbase62.encode(
                                int(last_message.get("message_body").get("msg_content").get("feed_id")))
                            feed_type = await FeedServer().get_feed_type(feed_id=int(feed_id),
                                                                         request_id=self.request_id)

                        content = ""
                        if last_message.get("message_body").get("msg_title") == "post":
                            content = "{} 有新{}".format(pb_userinfo.nickname, type_name[feed_type])

                        if last_message.get("message_body").get("msg_title") == "comment":
                            comment = await FeedServer().get_comment(
                                comment_id=int(last_message.get("message_body").get("msg_content").get("comment_id")),
                                space_id=space.space_id, account_id=self.current_user.account_id,
                                request_id=self.request_id)

                            commenter_userinfo = await AccountServer().get_userinfo(account_id=comment.author,
                                                                                    app_id=self.app_id_int64,
                                                                                    request_id=self.request_id)

                            content = "{} 发表了评论".format(commenter_userinfo.nickname)

                        if last_message.get("message_body").get("msg_title") == "like":
                            liker_userinfo = await AccountServer().get_userinfo(
                                account_id=int(last_message.get("message_body").get("msg_content").get("like_id")),
                                app_id=self.app_id_int64,
                                request_id=self.request_id)
                            content = "{} 赞了一下{}的{}".format(liker_userinfo.nickname, pb_userinfo.nickname,
                                                            type_name[feed_type])

                        if last_message.get("message_body").get("msg_title") == "follow":
                            follower_userinfo = await AccountServer().get_userinfo(
                                account_id=int(last_message.get("message_body").get("msg_content").get("follower_id")),
                                app_id=self.app_id_int64,
                                request_id=self.request_id)

                            content = "{} 关注了{}".format(follower_userinfo.nickname, pb_userinfo.nickname)
                        if last_message.get("message_body").get("msg_content").get("comment_id"):
                            last_message['message_body']['msg_content']['comment_id'] = zbase62.encode(
                                int(last_message.get("message_body").get("msg_content").get("comment_id")))

                        unread = await MsgBoxServer().get_unread_count(product_id=Config().product,
                                                                       msg_type=Config().msgbox.get("msg_type").get(
                                                                           "feed"), space_id=space.space_id,
                                                                       to_id=self.current_user.account_id,
                                                                       request_id=self.request_id)
                        message_center_list.append(
                            {"title": title,
                             "space_id": zbase62.encode(space.space_id),
                             "avatar": baby_avatar,
                             "unread": unread,
                             "from_id": zbase62.encode(self.current_user.account_id),
                             "latest_message": {"content": content, "create_at": last_message.get("create_at"),
                                                "message_id": last_message.get("message_id"),
                                                "msg_type": last_message.get("msg_type")}
                             })

        if message_center_list is not None:
            self.send_to_client(0, '获取消息成功', response=sorted(message_center_list, key=lambda x: zbase62.decode(
                x['latest_message']['message_id']), reverse=True))

        else:
            self.send_to_client(-1, '获取消息失败')


class CreateGroupMessage(APIHandler):
    async def post(self):
        try:
            validator.msg_title(self.post_data.get('msg_title'))
            validator.word(self.post_data.get('msg_content'))
            validator.account_id(self.post_data.get('from_id'))
        except validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return
        group_message_id = await ZIDServer().generate(self.request_id)
        if group_message_id is None:
            raise HTTPError(500, "zid-server generate failed", reason="服务器出错，请联系客服解决")
        result = await MsgBoxServer().create_group_message(group_message_id=group_message_id,
                                                           product_id=Config().product,
                                                           msg_title=self.post_data.get("msg_title"),
                                                           msg_content=self.post_data.get("msg_content"),
                                                           from_id=zbase62.decode(self.post_data.get("from_id")),
                                                           request_id=self.request_id)
        if result:
            self.send_to_client(-1, '消息发送失败！')
            return

        self.send_to_client(0, '消息发送成功！')
        return


# class AddMessage(APIHandler):
#     async def post(self):
#         await MsgBoxServer().add_message()


class QueryMessage(APIHandler):
    @authenticated_async
    async def post(self):
        try:
            validator.space_id(self.post_data.get('space_id'))
            validator.msgtype(self.post_data.get('msg_type'))
        except validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return
        message_list = []
        type_name = {0: "日记", 1: "照片", 2: "视频", 3: "音频", 4: "故事", 5: "生长发育"}
        pbmsg = await MsgBoxServer().query_message(product_id=Config().product,
                                                   msg_type=self.post_data.get("msg_type"),
                                                   space_id=zbase62.decode(self.post_data.get("space_id")),
                                                   to_id=self.current_user.account_id,
                                                   from_message_id=zbase62.decode(
                                                       self.post_data.get("from_message_id")) if self.post_data.get(
                                                       "from_message_id") else (1 << 63) - 1,
                                                   per_page=Config().msgbox.get("per_page"),
                                                   request_id=self.request_id)

        avatar = ""
        if pbmsg:
            for msg in MsgBox(pbmsg).msgbox.get("messages"):
                del msg["product_id"], msg["to_id"], msg["from_id"], msg["space_id"],
                msg["message_id"] = zbase62.encode(int(msg.get("message_id")))
                feed_id = msg.get("message_body").get(
                    "msg_content").get("feed_id")
                feed_type = None
                if msg.get("message_body").get("msg_content").get("feed_id"):
                    msg['message_body']['msg_content']['feed_id'] = zbase62.encode(
                        int(msg.get("message_body").get("msg_content").get("feed_id")))
                    feed_type = await FeedServer().get_feed_type(feed_id=int(feed_id), request_id=self.request_id)
                title = ""
                content = ""
                snapshot = {}
                if msg.get("message_body").get("msg_title") == "post":
                    pb_space_detail = await SpaceServer().get_space_details(
                        space_id=zbase62.decode(self.post_data.get("space_id")), request_id=self.request_id)
                    owner_userinfo = await AccountServer().get_userinfo(
                        account_id=pb_space_detail.owner_id,
                        app_id=self.app_id_int64,
                        request_id=self.request_id)
                    title = "{} 有新{}".format(owner_userinfo.nickname, type_name.get(feed_type))
                    avatar_name = owner_userinfo.avatar
                    if avatar_name:
                        avatar, error = await backend.backend_user_media.get_public_url(avatar_name)
                    else:
                        avatar = ""
                    feed = await FeedServer().get_feed(feed_id=int(feed_id),
                                                       space_id=zbase62.decode(self.post_data.get("space_id")),
                                                       account_id=self.current_user.account_id,
                                                       request_id=self.request_id)
                    content = Feed(feed).feed.get("word") if Feed(feed).feed.get("word") else ""
                    msg["feed_id"] = msg["message_body"]["msg_content"]["feed_id"]
                    if Feed(feed).feed.get("feed_type") == 1:
                        snapshot = {"url": Feed(feed).feed.get("files")[0]["url"],
                                    "width": Feed(feed).feed.get("files")[0]["width"],
                                    "height": Feed(feed).feed.get("files")[0]["height"]}
                    if Feed(feed).feed.get("feed_type") == 2:
                        snapshot = {"url": Feed(feed).feed.get("files")[0]["cover_image_url"],
                                    "width": Feed(feed).feed.get("files")[0]["width"],
                                    "height": Feed(feed).feed.get("files")[0]["height"]}
                if msg.get("message_body").get("msg_title") == "comment":
                    comment = await FeedServer().get_comment(
                        comment_id=int(msg.get("message_body").get("msg_content").get("comment_id")),
                        space_id=zbase62.decode(self.post_data.get("space_id")),
                        account_id=self.current_user.account_id,
                        request_id=self.request_id)

                    if comment.word is "":
                        continue

                    commenter_userinfo = await AccountServer().get_userinfo(account_id=comment.author,
                                                                            app_id=self.app_id_int64,
                                                                            request_id=self.request_id)
                    title = "{} 发表了新评论".format(commenter_userinfo.nickname)
                    content = comment.word
                    avatar_name = commenter_userinfo.avatar
                    if avatar_name:
                        avatar, error = await backend.backend_user_media.get_public_url(avatar_name)
                    else:
                        avatar = ""

                if msg.get("message_body").get("msg_title") == "like":
                    liker_userinfo = await AccountServer().get_userinfo(
                        account_id=int(msg.get("message_body").get("msg_content").get("like_id")),
                        app_id=self.app_id_int64,
                        request_id=self.request_id)
                    title = "{} 赞了一下".format(liker_userinfo.nickname)
                    avatar_name = liker_userinfo.avatar
                    if avatar_name:
                        avatar, error = await backend.backend_user_media.get_public_url(avatar_name)
                    else:
                        avatar = ""

                    content = ""
                if msg.get("message_body").get("msg_title") == "follow":
                    pb_space_detail = await SpaceServer().get_space_details(
                        space_id=zbase62.decode(self.post_data.get("space_id")), request_id=self.request_id)
                    owner_userinfo = await AccountServer().get_userinfo(
                        account_id=pb_space_detail.owner_id,
                        app_id=self.app_id_int64,
                        request_id=self.request_id)
                    follower_userinfo = await AccountServer().get_userinfo(
                        account_id=int(msg.get("message_body").get("msg_content").get("follower_id")),
                        app_id=self.app_id_int64,
                        request_id=self.request_id)
                    title = "{} 有一个新粉丝了".format(owner_userinfo.nickname)
                    avatar_name = owner_userinfo.avatar
                    if avatar_name:
                        avatar, error = await backend.backend_user_media.get_public_url(avatar_name)
                    else:
                        avatar = ""
                    content = "{} 关注了{}".format(follower_userinfo.nickname, owner_userinfo.nickname)
                if msg.get("message_body").get("msg_content").get("comment_id"):
                    msg['message_body']['msg_content']['comment_id'] = zbase62.encode(
                        int(msg.get("message_body").get("msg_content").get("comment_id")))
                msg["msg_content"] = msg["message_body"]["msg_content"]
                # system message
                if msg["msg_type"] == 4:
                    title = msg.get("message_body").get("msg_title") if msg.get("message_body").get(
                        "msg_title") else ""
                    content = msg.get("message_body").get("msg_content").get("body") if msg.get("message_body").get(
                        "msg_content").get("body") else ""
                    msg["type"] = msg["message_body"]["msg_content"]["type"]
                if msg["msg_type"] == 3:
                    msg["action"] = msg["message_body"]["msg_content"]["action"]
                msg["snapshot"] = snapshot

                del msg["message_body"]
                del msg["msg_content"]
                message_list.append(
                    {"title": title,
                     "content": content,
                     "from_id": zbase62.encode(self.current_user.account_id),
                     "space_id": self.post_data.get("space_id"),
                     "avatar": avatar,
                     "msg": msg,
                     })
            self.send_to_client(0, '查询消息成功！', response={"message_list": message_list,
                                                        "is_last_page": MsgBox(pbmsg).msgbox.get("is_last_page")})
            return
        else:
            self.send_to_client(-1, '查询消息失败！')
            return


class DeleteMessage(APIHandler):
    async def post(self):
        try:
            validator.message_id(self.post_data.get('message_id'))
            validator.account_id(self.post_data.get('from_id'))
        except validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return
        result = await MsgBoxServer().delete_message(message_id=zbase62.decode(self.post_data.get("message_id")),
                                                     to_id=zbase62.decode(self.post_data.get("from_id")),
                                                     request_id=self.request_id)
        rd.redis_del('message_center_list:{}'.format(zbase62.decode(self.post_data.get("from_id"))))
        if result:
            self.send_to_client(-1, '删除消息失败！')
            return

        self.send_to_client(0, '删除消息成功！')
        return


class DeleteAllMessage(APIHandler):
    async def post(self):
        try:
            validator.message_id(self.post_data.get('message_id'))
            validator.account_id(self.post_data.get('from_id'))
            validator.space_id(self.post_data.get('space_id'))
            validator.msgtype(self.post_data.get('msg_type'))
        except validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return
        result = await MsgBoxServer().delete_all_message(product_id=Config().product,
                                                         msg_type=self.post_data.get("msg_type"),
                                                         space_id=zbase62.decode(self.post_data.get("space_id")),
                                                         to_id=zbase62.decode(self.post_data.get("from_id")),
                                                         request_id=self.request_id)
        rd.redis_del('message_center_list:{}'.format(zbase62.decode(self.post_data.get("from_id"))))
        if result:
            self.send_to_client(-1, '删除所有消息失败！')
            return

        self.send_to_client(0, '删除所有消息成功！')
        return


class SetReadMessage(APIHandler):
    async def post(self):
        try:
            validator.message_id(self.post_data.get('message_id'))
            validator.account_id(self.post_data.get('from_id'))
        except validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return
        result = await MsgBoxServer().set_message_as_read(message_id=zbase62.decode(self.post_data.get("message_id")),
                                                          to_id=zbase62.decode(self.post_data.get("from_id")),
                                                          request_id=self.request_id)
        rd.redis_del('message_center_list:{}'.format(zbase62.decode(self.post_data.get("from_id"))))
        if result:
            self.send_to_client(-1, '设置消息已读失败！')
            return

        self.send_to_client(0, '设置消息已读成功！')
        return


class ReadAllMessage(APIHandler):
    async def post(self):
        try:
            validator.account_id(self.post_data.get('from_id'))
            validator.space_id(self.post_data.get('space_id'))
            validator.msgtype(self.post_data.get('msg_type'))
        except validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return
        result = await MsgBoxServer().set_all_message_as_read(product_id=Config().product,
                                                              to_id=zbase62.decode(self.post_data.get("from_id")),
                                                              msg_type=self.post_data.get("msg_type"),
                                                              space_id=zbase62.decode(self.post_data.get("space_id")),
                                                              request_id=self.request_id)
        rd.redis_del('message_center_list:{}'.format(zbase62.decode(self.post_data.get("from_id"))))
        if result:
            self.send_to_client(-1, '设置所有消息已读失败！')
            return

        self.send_to_client(0, '设置所有消息已读成功！')
        return


class SetUnReadMessage(APIHandler):
    async def post(self):
        try:
            validator.account_id(self.post_data.get('from_id'))
            validator.message_id(self.post_data.get('message_id'))
        except validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return
        result = await MsgBoxServer().set_message_as_unread(message_id=zbase62.decode(self.post_data.get("message_id")),
                                                            to_id=zbase62.decode(self.post_data.get("from_id")),
                                                            request_id=self.request_id)
        rd.redis_del('message_center_list:{}'.format(zbase62.decode(self.post_data.get("from_id"))))
        if result:
            self.send_to_client(-1, '设置消息未读失败！')
            return

        self.send_to_client(0, '设置消息未读成功！')
        return


class UnReadCountHandler(APIHandler):
    @authenticated_async
    async def post(self):
        unread_count = 0
        system_pbmsg = await MsgBoxServer().query_message(product_id=Config().product,
                                                          to_id=self.current_user.account_id,
                                                          per_page=1,
                                                          space_id=0,
                                                          request_id=self.request_id,
                                                          msg_type=Config().msgbox.get("msg_type").get("system"),
                                                          )
        if system_pbmsg:
            if MsgBox(system_pbmsg).msgbox.get("messages"):
                unread = await MsgBoxServer().get_unread_count(product_id=Config().product,
                                                               msg_type=Config().msgbox.get("msg_type").get("system"),
                                                               to_id=self.current_user.account_id,
                                                               request_id=self.request_id)
                unread_count += unread
        # 　获取所有关注的space空间
        pb_space = await SpaceServer().get_all_space(follower_id=self.current_user.account_id,
                                                     request_id=self.request_id)

        for space in pb_space.space_details:
            if space.status == 0:
                unread = await MsgBoxServer().get_unread_count(product_id=Config().product,
                                                               msg_type=Config().msgbox.get("msg_type").get(
                                                                   "feed"), space_id=space.space_id,
                                                               to_id=self.current_user.account_id,
                                                               request_id=self.request_id)
                unread_count += unread

        self.send_to_client(0, '获取未读消息总数成功！', response={"unread_count": unread_count})
