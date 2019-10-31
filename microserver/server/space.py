import logging

import grpc

from tornado.web import HTTPError
from core.singleton import Singleton
from core.server_status import get_server_status
from microserver.pb import pbspace_pb2
from microserver.mserver import MServer


class SpaceServer(metaclass=Singleton):
    async def create_space(self, space_id, owner_id, create_by, request_id, status=0):
        """创建space
        
         如果失败了会返回None
         
         Arguments:
            space_id  -- 外部生成的id
            owner_id  -- 宝宝的 account_id
            create_by  -- 创建者的 account_id
            status  -- space 状态 0 激活 1 已暂停 2 已删除

        Returns:
            pb_space 
        """
        try:
            msg = pbspace_pb2.SpaceCreate(space_id=space_id, owner_id=owner_id, create_by=create_by, status=status)
            pb_space = await MServer().call(
                "space-server", "CreateSpace", msg, request_id)
            return pb_space

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def set_follower(self, space_id, follower_id, group_id=None, relation_id=None, relation_name=None,
                           space_nickname=None, request_id=None):
        """设置 follower
        
        如果失败了会返回None
         
         Arguments:
            space_id  -- 外部生成的id
            follower_id  -- 
            relation  -- 与宝宝的关系
            nickname -- space nickname

        Returns:
            pb_follower 
        
        """
        try:

            msg = pbspace_pb2.FollowerData(space_id=int(space_id), follower_id=follower_id, group_id=group_id,
                                           relation_id=relation_id,
                                           relation_name=relation_name, space_nickname=space_nickname)
            pb_follower = await MServer().call(
                "space-server", "SetFollower", msg, request_id)
            return pb_follower.is_done

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def update_follower(self, params, request_id):
        """更新follower信息


        """
        try:
            msg = pbspace_pb2.FollowerInfo(params=params)
            result = await MServer().call("space-server", "UpdateFollower", msg, request_id)
            return result.is_done, result.message

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_all_follower(self, space_id, request_id):
        """通过space id 获取所有的follower信息
        
        Returns:
            pb_follower_details list 
        """

        try:

            msg = pbspace_pb2.SpaceID(space_id=space_id)
            pb_follower = await MServer().call(
                "space-server", "GetFollowerDetailsBySpaceID", msg, request_id)
            return pb_follower

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_space_details(self, space_id, request_id):
        """通过space_id 获取space 详情
        
        """
        try:
            msg = pbspace_pb2.SpaceID(space_id=int(space_id))
            pb_space_detail = await MServer().call("space-server", "GetSpaceDetailsBySpaceID", msg, request_id)
            return pb_space_detail

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_all_space(self, follower_id, request_id):
        """通过follower id 获取所有的space信息
        
        Returns:
            pb_follower_details list 
        """
        try:

            msg = pbspace_pb2.FollowerID(follower_id=follower_id)
            pb_space_details = await MServer().call(
                "space-server", "GetSpaceDetailsByFollowerID", msg, request_id)
            return pb_space_details

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_all_auth_space(self, follower_id, request_id):
        """通过follower id 获取所有的有修改权限的space信息

        Returns:
            pb_follower_details list 
        """
        try:

            msg = pbspace_pb2.FollowerID(follower_id=follower_id)
            pb_space_details = await MServer().call(
                "space-server", "GetAuthSpaceDetailsByFollowerID", msg, request_id)
            return pb_space_details

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_auth_space_owner_id(self, follower_id, request_id):
        """ 通过follower id 获取拥有修改space权限 的 宝宝id 列表
        
        :param follower_id: 
        :param request_id: 
        :return: [space_id, owner_id]
        """
        try:

            msg = pbspace_pb2.FollowerID(follower_id=follower_id)
            pb_space_owner_list = await MServer().call(
                "space-server", "GetAuthOwnerIDList", msg, request_id)
            return pb_space_owner_list

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def search_follower(self, space_id, follower_id, request_id):
        """查询follower
        """
        try:
            msg = pbspace_pb2.FollowerKey(space_id=int(space_id), follower_id=follower_id)
            pbfollower = await MServer().call("space-server", "SearchFollower", msg, request_id)
            return pbfollower

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def update_space_info(self, params, request_id):
        """更新space信息
        
      
        """
        try:
            msg = pbspace_pb2.Info(params=params)
            await MServer().call("space-server", "UpdateSpaceInfo", msg, request_id)

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def update_space_status(self, creator_id, space_id, status, request_id):
        """更新space 状态

         Arguments:
            status  -- space状态 0 激活, 1 已暂停, 2 已删除
            space_id  -- 

        Returns:
            result bool 
        """
        try:
            msg = pbspace_pb2.Status(space_id=int(space_id), status=status, creator_id=creator_id)
            result = await MServer().call("space-server", "UpdateSpaceStatus", msg, request_id)
            return result.is_done, result.message

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_space_count(self, follower_id, request_id):
        """获取可创建baby space的总数
        
        :param follower_id: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbspace_pb2.Status(space_id=int(follower_id))
            pbcount = await MServer().call("space-server", "GetSpaceCount", msg, request_id)
            return pbcount.space_count

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def save_invite_id(self, space_id, invite_code, request_id):
        """创建invite_id
        
        :param space_id: 
        :param invite_code: 
        :return: 
        """
        try:
            msg = pbspace_pb2.SpaceIDCode(space_id=space_id, invite_code=invite_code)
            result = await MServer().call("space-server", "SaveInviteCode", msg, request_id)

            return result.is_done

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_invite_id(self, space_id, request_id):
        """获取邀请码
        
        :param space_id: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbspace_pb2.SpaceID(space_id=space_id)
            result = await MServer().call("space-server", "GetInviteCode", msg, request_id)

            return result.invite_code

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def delete_follower(self, creator_id, space_id, follower_id, request_id):
        """移除follower
        
        :param space_id: 
        :param follower_id: 
        :return: 
        """
        try:
            msg = pbspace_pb2.DeleteFollowerRequest(creator_id=creator_id, space_id=space_id, follower_id=follower_id)
            result = await MServer().call("space-server", "DeleteFollower", msg, request_id)

            return result.is_done, result.message

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_space_id(self, invite_code, request_id):
        """ 获取 space_id 
        
        :param invite_code: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbspace_pb2.InviteCode(invite_code=invite_code)
            result = await MServer().call("space-server", "GetSpaceID", msg, request_id)

            return result.space_id


        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def add_group(self, creator_id, space_id, permission_level, group_name=None, request_id=None):
        """　创建用户组
        
        :return: 
        """
        try:
            msg = pbspace_pb2.AddGroupRequest(creator_id=creator_id, space_id=space_id, group_name=group_name,
                                              permission_level=permission_level)
            result = await MServer().call("space-server", "AddGroup", msg, request_id)

            return result.group_id


        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            if e.code().__dict__.get('_name_') == 'PERMISSION_DENIED':
                raise HTTPError(-1, "permission denied", reason="权限不足！")
            logging.warning(msg)

            return None

    async def update_group(self, params, request_id):
        try:
            msg = pbspace_pb2.Info(params=params)
            result = await MServer().call("space-server", "SetGroup", msg, request_id)
            return result.is_done, result.message

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def delete_group(self, group_id, space_id, creator_id, request_id):
        try:
            msg = pbspace_pb2.DeleteGroupRequest(group_id=group_id, space_id=space_id, creator_id=creator_id)
            result = await MServer().call("space-server", "DeleteGroup", msg, request_id)
            return result.is_done, result.message

        except grpc.RpcError as e:
            if e.code().__dict__.get('_name_') == 'PERMISSION_DENIED':
                raise HTTPError(-1, "permission denied", reason="权限不足！")
            logging.warning(msg)
            return None

    async def get_group_by_group_id(self, group_id, request_id):
        """
        
        :param group_id: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbspace_pb2.GroupID(group_id=int(group_id))
            pb_group = await MServer().call("space-server", "GetGroupByGroupID", msg, request_id)

            return pb_group


        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_all_group_by_space_id(self, space_id, request_id):
        """
        
        :param space_id: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbspace_pb2.SpaceID(space_id=int(space_id))
            pb_group_list = await MServer().call("space-server", "GetAllGroup", msg, request_id)

            return pb_group_list


        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_group_count_by_group_id(self, group_id, request_id):
        """

        :param space_id: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbspace_pb2.GroupID(group_id=int(group_id))
            pb_count = await MServer().call("space-server", "GetGroupCountByGroupID", msg, request_id)

            return pb_count.group_count


        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_default_group_count_by_group_id(self, space_id, request_id):
        """

        :param space_id: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbspace_pb2.SpaceID(space_id=int(space_id))
            pb_count = await MServer().call("space-server", "GetDefaultGroupCountByGroupID", msg, request_id)

            return pb_count.group_count


        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_relation_by_relation_id(self, relation_id, request_id):
        """
        
        :param relation_id: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbspace_pb2.RelationID(relation_id=int(relation_id))
            pb_relation = await MServer().call("space-server", "GetRelationByRelationID", msg, request_id)

            return pb_relation

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_all_relation(self, request_id):
        """
        
        :param request_id: 
        :return: 
        """
        try:
            msg = pbspace_pb2.Empty()
            pb_relation = await MServer().call("space-server", "GetAllRelation", msg, request_id)
            return pb_relation

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_permission_level(self, space_id, follower_id, request_id):
        """

        :param space_id:
        :param follower_id:
        :param request_id:
        :return:
        """
        try:
            msg = pbspace_pb2.GetPermissionLevelRequest(space_id=space_id, follower_id=follower_id)
            pb_permission_level = await MServer().call("space-server", "GetPermissionLevel", msg, request_id)
            return pb_permission_level
        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None