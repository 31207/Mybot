from cmds import *
from bot import *
import requests
import yaml
import json
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
        print(data.message)
        if data.group_id not in groupWhiteList:
            return
        await msgparser.groupParser(data)  # 人人都能用的指令
        await msgparser.developerParser(data)

    async def on_friendRecallEvent(self, data: FriendRecall):
        log.info(f"[QQ:{data.user_id}, 撤回了一条消息]")

    async def on_groupRecallEvent(self, data: GroupRecall):
        log.info(f"[群:{data.group_id}, QQ:{data.user_id}, 撤回了一条消息]")

    async def on_touchEvent(self, data: GroupTouch):
        log.info(f"[群:{data.group_id}, QQ:{data.operator_id}, 触摸了:{data.target_id}]")
        if data.group_id not in groupWhiteList:
            return
        if data.target_id != 3579148268:
            return
        await self.sendGroupMsg(data.group_id, face(random.randint(0, 221)))


async def init(url: str):

    log.info('正在获取maimai所有曲目信息')
    await mai.get_music()
    log.info('正在获取maimai所有曲目别名信息')
    await mai.get_music_alias()
    log.info('maimai数据获取完成')
    mai.guess()

    try:
        log.info('正在尝试访问shamrock端...')
        ret = requests.post(f"{url}/get_login_info")
        print(ret.text)
        botid = json.loads(ret.text)['data']['user_id']
        log.info('shamrock访问正常')
        return botid
    except Exception as e:
        log.error(e)
        return ''



if __name__ == '__main__':
    log.info("\ttest")
    log.warning("\ttest")
    log.error("\ttest")
    log.critical("\ttest")
    log.debug("\ttest")
    with open("../config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    groupWhiteList = config['whitelist']
    admin = config['admin']
    # 创建事件循环对象
    loop = asyncio.get_event_loop()
    # 运行异步函数
    botid = loop.run_until_complete(init(config['url']))
    if botid == '':
        exit(-1)
    log.critical(f'白名单：{groupWhiteList}')
    log.critical(f'管理员：{admin}')
    log.critical(f'BotQQ：{botid}')
    msgparser = MsgEventParser(config['url'])
    instance = Mybot(config['url'])
