from pydantic import BaseModel
import requests
import fastapi
from fastapi import FastAPI, Request
import uvicorn
import logging


class Color:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


class CustomFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: f'{Color.BLUE}[%(asctime)s]{Color.RESET} - {Color.GREEN}%(levelname)s: %(message)s{Color.RESET}',
        logging.INFO: f'{Color.BLUE}[%(asctime)s]{Color.RESET} - {Color.WHITE}%(levelname)s: %(message)s{Color.RESET}',
        logging.WARNING: f'{Color.BLUE}[%(asctime)s]{Color.RESET} - {Color.YELLOW}%(levelname)s: %(message)s{Color.RESET}',
        logging.ERROR: f'{Color.BLUE}[%(asctime)s]{Color.RESET} - {Color.RED}%(levelname)s: %(message)s{Color.RESET}',
        logging.CRITICAL: f'{Color.BLUE}[%(asctime)s]{Color.RESET} - {Color.PURPLE}%(levelname)s: %(message)s{Color.RESET}',
    }

    def format(self, record):
        log_format = self.FORMATS.get(record.levelno, self.FORMATS[logging.DEBUG])
        formatter = logging.Formatter(log_format)
        return formatter.format(record)


# 配置日志
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# 创建控制台处理器，并设置自定义格式化器
console_handler = logging.StreamHandler()
console_formatter = CustomFormatter()
console_handler.setFormatter(console_formatter)

# 将处理器添加到日志记录器
log.addHandler(console_handler)


class Type:
    error = -1
    privateMsgEvent = 0
    groupMsgEvent = 1
    friendRecallEvent = 2
    groupRecallEvent = 3
    touchEvent = 4


class Event:
    time: int
    self_id: int
    post_type: str


class PrivateMsg(BaseModel, Event):
    message_type: str
    sub_type: str
    message_id: int
    target_id: int
    peer_id: int
    user_id: int
    message: object
    raw_message: str
    font: int
    sender: object


class GroupMsg(BaseModel, Event):
    message_type: str
    sub_type: str
    message_id: int
    group_id: int
    peer_id: int
    user_id: int
    message: object
    raw_message: str
    font: int
    sender: object


class GroupRecall(BaseModel, Event):
    notice_type: str
    group_id: int
    operator_id: int
    user_id: int
    message_id: int
    tip_text: str | None = None


class FriendRecall(BaseModel, Event):
    notice_type: str
    operator_id: int
    user_id: int
    message_id: int
    tip_text: str


class GroupTouch(BaseModel):
    time: int
    self_id: int
    post_type: str
    notice_type: str
    sub_type: str
    group_id: int
    operator_id: int
    user_id: int
    target_id: int
    poke_detail: object


class interfaces:
    def __init__(self, url: str):
        self.__address = url

    async def sendPrivateMsg(self, qqid: int, msg):
        j = {
            'user_id': qqid,
            'message': msg,
            'auto_escape': False
        }
        ret = requests.post(f"{self.__address}/send_private_msg", json=j)
        print(ret.json())
        return ret.json()

    async def sendGroupMsg(self, groupId: int, msg):
        j = {
            'group_id': groupId,
            'message': msg,
            'auto_escape': False
        }
        ret = requests.post(f"{self.__address}/send_group_msg", json=j)
        print(ret.json())
        return ret.json()

    async def setGroupAdmin(self, groupId: int, qqid: int, enable: bool):
        j = {
            'group_id': groupId,
            'user_id': qqid,
            'enable': enable
        }
        ret = requests.post(f"{self.__address}/set_group_admin", json=j)
        print(ret.json())
        return ret.json()

    async def setGroupSpecialTitle(self, groupId: int, qqid: int, specialTitle: str):
        j = {
            'group_id': groupId,
            'user_id': qqid,
            'special_title': specialTitle
        }
        ret = requests.post(f"{self.__address}/set_group_special_title", json=j)
        print(ret.json())
        return ret.json()

    async def setGroupBan(self, groupId: int, qqid: int, duration: int):
        j = {
            'group_id': groupId,
            'user_id': qqid,
            'duration': duration
        }
        ret = requests.post(f"{self.__address}/set_group_ban", json=j)
        print(ret.json())
        return ret.json()

    async def setGroupWholeBan(self, groupId: int, enable: bool):
        j = {
            'group_id': groupId,
            'enable': enable
        }
        ret = requests.post(f"{self.__address}/set_group_whole_ban", json=j)
        print(ret.json())
        return ret.json()

    async def setGroupKick(self, groupId: int, qqid: int, reject: bool):
        j = {
            'group_id': groupId,
            'user_id': qqid,
            'reject_add_request': reject
        }
        ret = requests.post(f"{self.__address}/set_group_kick", json=j)
        print(ret.json())
        return ret.json()

    async def groupTouch(self, groupId: int, qqid: int):
        j = {
            'group_id': groupId,
            'user_id': qqid,
        }
        ret = requests.post(f"{self.__address}/group_touch", json=j)
        print(ret.json())
        return ret.json()

    def fastResponse(self, reply: str):  # 返回响应
        j = {
            'reply': reply,
            'auto_escape': False,
            'auto_reply': False
        }
        return j


class bot(interfaces):
    def __init__(self, url: str):
        super().__init__(url)
        __app = FastAPI()
        __app.add_route('/', self.checkState, methods=['GET'])
        __app.add_route('/', self.callback, methods=['POST'])
        uvicorn.run(app=__app,
                    host="0.0.0.0",
                    port=8080,
                    workers=1)
        return

    async def checkState(self, data: Request):
        content = {"message": "Running"}
        response = fastapi.responses.JSONResponse(content=content, status_code=200)
        return response

    async def callback(self, data: Request):
        j = await data.json()
        await self.proc(j)
        content = {"message": "OK"}
        response = fastapi.responses.JSONResponse(content=content, status_code=200)
        return response

    async def on_privateMsgEvent(self, data: PrivateMsg):
        return

    async def on_groupMsgEvent(self, data: GroupMsg):
        return

    async def on_friendRecallEvent(self, data: FriendRecall):
        return

    async def on_groupRecallEvent(self, data: GroupRecall):
        return

    async def on_touchEvent(self, data: GroupTouch):
        return

    def get_event_type(self, j: dict):
        if j['post_type'] == 'message':
            if j['message_type'] == 'private':
                return Type.privateMsgEvent
            if j['message_type'] == 'group':
                return Type.groupMsgEvent
        if j['post_type'] == 'notice':
            if j['notice_type'] == 'friend_recall':
                return Type.friendRecallEvent
            if j['notice_type'] == 'group_recall':
                return Type.groupRecallEvent
            if j['notice_type'] == 'notify' and j['sub_type'] == 'poke':
                return Type.touchEvent
        return Type.error

    async def proc(self, j: dict):
        event_type = self.get_event_type(j)
        if event_type == Type.error:
            return
        if event_type == Type.privateMsgEvent:
            await self.on_privateMsgEvent(PrivateMsg(**j))
            return
        if event_type == Type.groupMsgEvent:
            await self.on_groupMsgEvent(GroupMsg(**j))
            return
        if event_type == Type.friendRecallEvent:
            await self.on_friendRecallEvent(FriendRecall(**j))
            return
        if event_type == Type.groupRecallEvent:
            await self.on_groupRecallEvent(GroupRecall(**j))
            return
        if event_type == Type.touchEvent:
            if 'group_id' not in j:
                return
            await self.on_touchEvent(GroupTouch(**j))


def msg(*args):
    msg = []
    for i in args:
        if type(i) is str:
            j = {
                'type': 'text',
                'data': {
                    'text': i
                }
            }
            msg.append(j)
            continue
        if type(i) is dict:
            msg.append(i)
            continue
    return msg


def pic(path: str):  # 绝对路径
    j = {
        "type": "image",
        "data": {
            "file": f"file://{path}"
        }
    }
    return j


def pic_b64(data: str):  # 绝对路径
    j = {
        "type": "image",
        "data": {
            "file": f"base64://{data}"
        }
    }
    return j


def pic_url(url: str):  # 请务必要http://或https://开头
    j = {
        "type": "image",
        "data": {
            "file": url
        }
    }
    return j


def face(id: int):
    j = {
        "type": "face",
        "data": {
            "id": id
        }
    }
    return j


def audio(path: str):
    j = {
        "type": "record",
        "data": {
            "file": f"file://{path}"
        }
    }
    return j


def audio_url(url: str):
    j = {
        "type": "record",
        "data": {
            "file": url
        }
    }
    return j
def audio_b64(url: str):
    j = {
        "type": "record",
        "data": {
            "file": f"base64://{data}"
        }
    }
    return j

def at(qq: str):
    j = {
        "type": "at",
        "data": {
            "qq": qq
        }
    }
    return j


def json_card(data: dict):
    j = {
        'type': 'json',
        'data': {
            'data': '{"app":"com.tencent.eventshare.lua","desc":"","view":"eventshare","bizsrc":"tianxuan.business","ver":"0.0.0.1","prompt":"我喜欢你","appID":"","sourceName":"","actionData":"","actionData_A":"","sourceUrl":"","meta":{"eventshare":{"button1URL":"https://ys.mihoyo.com/?utm_source=adbdpz&from_channel=adbdpz#/","button1disable":false,"button1title":"是的，我想","button2URL":"https://sr.mihoyo.com/ad?from_channel=adbdpz&utm_source=mkt&utm_medium=branding&utm_campaign=871858","button2disable":false,"button2title":"不，算了","buttonNum":2,"jumpURL":"https://h5.qzone.qq.com/v2/vip/card/page/home?_wv=16778146&enteranceId=shareark&visitUin=3470558502","preview":"https://tianquan.gtimg.cn//chatBg//item//51841//newPreview2.png","tag":"QQ","tagIcon":"http://gchat.qpic.cn/gchatpic_new/0/0-0-C5B80B435F21247D9BC6225EAA9A3A76/0?term=2","title":"是否进入虚拟猫娘世界Neko World"}},"config":{"autosize":0,"collect":0,"ctime":1707209474,"forward":1,"height":336,"reply":0,"round":1,"token":"68fb63bdfc5fd39744233bcc72b1ef66","type":"normal","width":263},"text":"","extraApps":[],"sourceAd":"","extra":""}'
        }
    }
