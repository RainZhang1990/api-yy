import json
import logging
import os
import platform
import time
from concurrent.futures import ThreadPoolExecutor
from ctypes import *
from functools import wraps

import tornado
import tornado.gen
import tornado.ioloop
from tornado import concurrent, ioloop
from tornado.concurrent import run_on_executor
from tornado.platform.asyncio import to_tornado_future

from core.config import Config

lib_path = None
bk = None

sys = platform.system()
if sys == "Linux":
    lib_path = './libs/libbackend.linux.so'
elif sys == "Darwin":
    lib_path = './libs/libbackend.darwin.so'

if lib_path:
    bk = cdll.LoadLibrary(lib_path)
    logging.info("Loaded libbackend library")
else:
    raise Exception("api-gw不支持"+sys+"系统")

backend_user_media = None

# -------------------------------------------------------------------------------------------------


def init_backend():
    global backend_user_media
    backend_user_media, error = Backend().create(
        Config().backend["access_key"],
        Config().backend["access_secret"],
        Config().backend["bucket"],
        Config().backend["endpoint"],
        Config().backend["visit_host"],
        Config().backend["temp_filepath"],
    )
    return error


def blocking(method):
    """Wraps the method in an async method, and executes the function on `self.executor`."""

    @wraps(method)
    @tornado.gen.coroutine
    def wrapper(self, *args, **kwargs):
        fut = self.executor.submit(method, self, *args, **kwargs)
        return (yield fut)

    return wrapper


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return json.JSONEncoder.default(self, obj)

# -------------------------------------------------------------------------------------------------


class Dimensions:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class GPSCoordinates:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude


class MetaDataPhoto:
    def __init__(self, json_str):
        metadata = json.loads(json_str)
        self.filename = metadata.get("Filename")
        self.filesize = metadata.get("Filesize")
        self.dimensions = Dimensions(metadata.get("Dimensions").get("Width"), metadata.get("Dimensions").get("Height"))
        self.model = metadata.get("Model")
        self.orientation = metadata.get("Orientation")

        self.gps = None
        if metadata.get("Gps"):
            self.gps = GPSCoordinates(metadata.get("Gps").get("Latitude"), metadata.get("Gps").get("Longitude"))

        self.create_at = metadata.get("CreateAt")
        self.origin_exif = metadata.get("OriginExif")


class MetaDataVideo:
    def __init__(self, dimensions, rotate, cover_image_filename):
        self.dimensions = dimensions
        self.rotate = rotate
        self.cover_image_filename = cover_image_filename


class MetaDataAudio:
    def __init__(self, sample_rate, channels, channel_layout):
        self.sample_rate = sample_rate
        self.channels = channels
        self.channel_layout = channel_layout


class MetaDataMedia:
    def __init__(self, json_str):
        metadata = json.loads(json_str)

        self.media_type = metadata.get("MediaType")
        self.format = metadata.get("Format")
        self.filename = metadata.get("Filename")
        self.filesize = metadata.get("Filesize")

        self.codec_name = metadata.get("CodecName")

        self.duration = metadata.get("Duration")
        self.start_time = metadata.get("StartTime")
        self.create_at = metadata.get("CreateAt")
        self.origin_exif = metadata.get("OriginExif")

        self.video_info = None
        self.audio_info = None

        if metadata.get("VideoInfo"):
            dimensions = None
            if metadata.get("VideoInfo").get("Dimensions"):
                dimensions = Dimensions(
                    metadata.get("VideoInfo").get("Dimensions").get("Width"),
                    metadata.get("VideoInfo").get("Dimensions").get("Height"))

            self.video_info = MetaDataVideo(
                dimensions,
                metadata.get("VideoInfo").get("Rotate"),
                metadata.get("VideoInfo").get("CoverImageFilename")
            )

        if metadata.get("AudioInfo"):
            self.audio_info = MetaDataAudio(
                metadata.get("AudioInfo").get("SampleRate"),
                metadata.get("AudioInfo").get("Channels"),
                metadata.get("AudioInfo").get("ChannelLayout")
            )


class GoString(Structure):
    _fields_ = [("p", c_char_p), ("n", c_longlong)]


class GetPublicURL_return(Structure):
    _fields_ = [("url", c_char_p), ("error", c_char_p)]


class Init_return(Structure):
    _fields_ = [("bk", c_int), ("error", c_char_p)]


class UploadAvatar_return(Structure):
    _fields_ = [("filename", c_char_p), ("error", c_char_p)]


class TransmitWechatAvatar_return(Structure):
    _fields_ = [("filename", c_char_p), ("error", c_char_p)]


class UploadPhoto_return(Structure):
    _fields_ = [("metadata", c_char_p), ("error", c_char_p)]


class UploadMedia_return(Structure):
    _fields_ = [("metadata", c_char_p), ("error", c_char_p)]

# -------------------------------------------------------------------------------------------------


class Backend(object):
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)

        self._bk = None

    def __del__(self):
        if self._bk:
            bk.FreeBackend.argtypes = [c_int]
            bk.FreeBackend.restype = None
            bk.FreeBackend(self._bk)
            logging.info("backend released")

    @classmethod
    def create(cls, access_key, access_secret, bucket, endpoint, visit_host, temp_filepath):
        """初始化backend lib
        """

        o = cls()
        o._access_key = access_key
        o._access_secret = access_secret
        o._bucket = bucket
        o._endpoint = endpoint
        o._visit_host = visit_host
        o._temp_filepath = temp_filepath

        if not os.path.exists(o._temp_filepath):
            os.makedirs(o._temp_filepath)

        bk.Init.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
        bk.Init.restype = Init_return

        ret = bk.Init(
            o._access_key.encode(),
            o._access_secret.encode(),
            o._bucket.encode(),
            o._endpoint.encode(),
            o._visit_host.encode(),
            o._temp_filepath.encode(),
        )
        o._bk = ret.bk
        return o if ret.bk else None, ret.error.decode() if ret.error else None

    @blocking
    def get_public_url(self, filename):
        """获得资源的公共访问地址

        Arguments:
            filename {string} -- 资源文件名

        Returns:
            string -- url
            string -- error
        """

        bk.GetPublicURL.argtypes = [c_int, c_char_p]
        bk.GetPublicURL.restype = GetPublicURL_return

        ret = bk.GetPublicURL(self._bk, filename.encode())
        return ret.url.decode() if ret.url else None, ret.error.decode() if ret.error else None

    @blocking
    def delete_object(self, filename):
        """删除文件

        Arguments:
            filename {string} -- 资源文件名

        Returns:
            string -- error
        """

        bk.DeleteObject.argtypes = [c_int, c_char_p]
        bk.DeleteObject.restype = c_char_p

        err = bk.DeleteObject(self._bk, filename.encode())
        return err.decode() if err else None

    @blocking
    def upload_avatar(self, zid, image_filepath, shape):
        """上传头像

        Arguments:
            zid {long} -- zid 值
            image_filepath {string} -- 头像文件路径
            shape {string} -- 头像图片的形状（square/circle/origin）

        Returns:
            string -- 头像的文件名
            string -- error
        """

        bk.UploadAvatar.argtypes = [c_int, c_longlong, c_char_p, c_char_p]
        bk.UploadAvatar.restype = UploadAvatar_return

        ret = bk.UploadAvatar(self._bk, zid, image_filepath.encode(), shape.encode())

        return ret.filename.decode() if ret.filename else None, ret.error.decode() if ret.error else None

    @blocking
    def transmit_wechat_avatar(self, zid, remote_url):
        """转存微信头像

        Arguments:
            zid {long} -- zid 值
            remote_url {string} -- 微信头像的URL地址

        Returns:
            string -- 头像的文件名
            string -- error
        """

        bk.TransmitWechatAvatar.argtypes = [c_int, c_longlong, c_char_p]
        bk.TransmitWechatAvatar.restype = TransmitWechatAvatar_return

        ret = bk.TransmitWechatAvatar(self._bk, zid, remote_url.encode())

        return ret.filename.decode() if ret.filename else None, ret.error.decode() if ret.error else None

    @blocking
    def upload_photo(self, zid, image_filepath):
        """上传普通照片

        Arguments:
            zid {long} -- zid 值
            image_filepath {string} -- 照片的文件路径

        Returns:
            string -- 照片的metadata信息
            string -- error
        """

        bk.UploadPhoto.argtypes = [c_int, c_longlong, c_char_p]
        bk.UploadPhoto.restype = UploadPhoto_return

        ret = bk.UploadPhoto(self._bk, zid, image_filepath.encode())

        return MetaDataPhoto(ret.metadata.decode()) if ret.metadata else None, ret.error.decode() if ret.error else None

    @blocking
    def upload_media(self, zid, media_filepath):
        """上传媒体资源（视频和音频）

        Arguments:
            zid {long} -- zid 值
            media_filepath {string} -- 媒体的文件路径

        Returns:
            string -- 媒体的metadata信息
            string -- error
        """

        bk.UploadMedia.argtypes = [c_int, c_longlong, c_char_p]
        bk.UploadMedia.restype = UploadMedia_return

        ret = bk.UploadMedia(self._bk, zid, media_filepath.encode())

        return MetaDataMedia(ret.metadata.decode()) if ret.metadata else None, ret.error.decode() if ret.error else None
