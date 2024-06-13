import asyncio
from bot import *
import requests
import yaml
import random
import subprocess

class Mybot(bot):
    async def on_privateMsgEvent(self, data: PrivateMsg):
        if data.user_id != 1692038362:
            return
        await self.sendPrivateMsg(data.user_id, '?')
        pass

    async def on_groupMsgEvent(self, data: GroupMsg):
        log.info(f"[群:{data.group_id}, QQ:{data.user_id}, 内容:{data.raw_message}]")

    async def on_friendRecallEvent(self, data: FriendRecall):
        log.info(f"[QQ:{data.user_id}, 撤回了一条消息]")

    async def on_groupRecallEvent(self, data: GroupRecall):
        log.info(f"[群:{data.group_id}, QQ:{data.user_id}, 撤回了一条消息]")

    async def on_touchEvent(self, data: GroupTouch):
        log.info(f"[群:{data.group_id}, QQ:{data.operator_id}, 触摸了:{data.target_id}]")
        if data.group_id not in groupWhiteList:
            return
        if data.target_id != 3446269404:
            return
        await self.sendGroupMsg(data.group_id, face(random.randint(0, 221)))


async def init(url: str):

    try:
        '''
        log.info('连接安卓模拟器中...')
        result = subprocess.run(f'adb connect {config["emulator"]}', shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            log.error('连接安卓模拟器失败')
            print(result.stdout)
            print(result.stderr)
            return ''
        
        log.info('映射端口中...')
        result = subprocess.run(f'adb forward tcp:{config["port"]} tcp:{config["port"]}', shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            log.error('映射端口失败')
            print(result.stdout)
            print(result.stderr)
            return ''
        '''
        log.info('正在尝试访问shamrock端...')
        ret = requests.post(f"{url}/get_login_info")
        print(ret.text)
        botqq = dict(ret.text)['user_id']
        log.info('shamrock访问正常')
        return ret.text
    except Exception as e:
        log.error(e)
        return ''

if __name__ == '__main__':
    log.info("test")
    log.warning("test")
    log.error("test")
    log.critical("test")
    log.debug("test")
    with open("../config.yaml", 'r') as f:
        config = yaml.safe_load(f)
        print(config)
    groupWhiteList = config['whitelist']
    admin = config['admin']
    user_id = 0
    # 创建事件循环对象
    loop = asyncio.get_event_loop()
    # 运行异步函数
    if loop.run_until_complete(init(config['url'])) == '':
        exit(-1)
    mybot = Mybot(config['url'])
