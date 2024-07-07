import re
import requests
import base64
from bot import *
import subprocess
import random
from otto import HZYS
from libraries.maimaidx_music_info import *
from libraries.maimaidx_music import *
from libraries.tool import *
from PIL import Image, ImageSequence

class MirrorEvent:

    def __init__(self):
        self.qqid: int
        self.direction: int
async def download_pic(url:str,path:str):
    try:
        res = requests.get(url)
        if res.status_code==200:
            with open(path,'wb') as file:
                file.write(res.content)
        else:
            print('download failed',res)
            return -1
    except requests.exceptions.RequestException as e:
        print(e)
        return -1
    return 0

async def split_and_mirror_gif(gif_path, output_path, direction:int):
    # 读取原始GIF文件
    original_gif = Image.open(gif_path)
    frames = []
    durations = []
    width, height = original_gif.size
    middle_width = width // 2
    middle_height = height // 2
    # 遍历GIF的每一帧并进行镜像处理
    count = 0
    for frame in ImageSequence.Iterator(original_gif):
        new_frame = Image.new('RGBA', (width, height))
        if direction == 0:
            left_half = frame.crop((0, 0, middle_width, height))
            mirrored_half = left_half.transpose(Image.FLIP_LEFT_RIGHT)
            new_frame.paste(left_half, (0, 0))
            new_frame.paste(mirrored_half, (middle_width, 0))
        elif direction == 1:
            top_half = frame.crop((0, 0, width, middle_height))
            mirrored_half = top_half.transpose(Image.FLIP_TOP_BOTTOM)
            new_frame.paste(top_half, (0, 0))
            new_frame.paste(mirrored_half, (0, middle_height))
        elif direction == 2:
            right_half = frame.crop((middle_width, 0,width , height))
            mirrored_half = right_half.transpose(Image.FLIP_LEFT_RIGHT)
            new_frame.paste(mirrored_half, (0, 0))
            new_frame.paste(right_half, (middle_width, 0))
        elif direction == 3:
            top_half = frame.crop((0, middle_height, width, height))
            mirrored_half = top_half.transpose(Image.FLIP_TOP_BOTTOM)
            new_frame.paste(mirrored_half, (0, 0))
            new_frame.paste(top_half, (0, middle_height))

        frames.append(new_frame)
        if 'duration' in frame.info:
            durations.append(frame.info['duration'])
        count+=1

    if count!=1: frames[0].save(output_path, save_all=True, append_images=frames[1:], loop=0, duration=durations)
    else: frames[0].save(output_path, save_all=True, append_images=frames[1:], loop=0)
class MsgEventParser(interfaces):
    def __init__(self, url: str):
        super().__init__(url)
        self.user_waiting = []
        self.group_cmds = {
            r'禁言\[CQ:at,qq=(\d+)] (\                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        d+)': self.mute,
            r'膜拜\[CQ:at,qq=(\d+)]': self.worship,
            r'/指 (.*)': self.point,
            r'/兄弟 (.*)': self.bro,
            r'/活字印刷 (.*)': self.otto_speak,
            r'/(.*)镜像': self.pic_mirror,
            r'dust b50': self.b50,
            r'^[来随给]个((?:dx|sd|标准))?([绿黄红紫白]?)([0-9]+\+?)$': self.random_song,
            r'maitoday': self.day_mai,
            r'/查歌 (.*)': self.search_song,
            r'/开始猜歌': self.guess_song,
            r'/重置猜歌': self.reset_guess,
            r'/(.*)猜歌': self.guess_on_off,
            r'(.*)是什么歌': self.what_song,
            r'(.*)是啥歌': self.what_song,
            r'^(id)?\s?(.+)\s?有什么别[名称]$': self.what_alias,
            r'(.*)完成表':self.rating_table_pf,    # 待修改
            r'(.*)分数列表':self.rating_table_pf    # 待修改
        }
        self.developer_cmds = {
            r'test': self.test,
            r'updatemusic': self.update_music
        }

    async def groupParser(self, data: GroupMsg):
        for i in self.group_cmds.keys():
            match = re.compile(i).match(data.raw_message)
            if match:
                await self.group_cmds[i](data, match)
                return
        # 默认处理
        await self.on_message(data)

    async def developerParser(self, data: GroupMsg):
        if data.user_id != 1692038362:
            await self.on_message(data)
            return
        for i in self.developer_cmds.keys():
            match = re.compile(i).match(data.raw_message)
            if match:
                await self.developer_cmds[i](data, match)
                return
        # 默认处理
        # await self.on_message(data)

    async def update_music(self, data: GroupMsg, match):
        try:
            log.info('正在手动更新maimai歌曲数据与别名数据')
            music_data = await maiApi.music_data()
            await writefile(music_file, music_data)
        except asyncio.exceptions.TimeoutError:
            log.error('从diving-fish获取maimaiDX曲目数据超时，正在使用yuzuapi中转获取曲目数据')
            music_data = await maiApi.transfer_music()
            await writefile(music_file, music_data)
        except UnknownError:
            log.error('从diving-fish获取maimaiDX曲目数据失败，请检查网络环境')
        except Exception:
            log.error(f'Error: {traceback.format_exc()}')
            log.error('maimaiDX曲目数据获取失败，请检查网络环境')
        try:
            alias_data: Dict[str, Dict[str, Union[str, List[str]]]] = await maiApi.get_alias()
            await writefile(alias_file, alias_data)
        except ServerError as e:
            log.error(e)
        except UnknownError:
            log.error('获取所有曲目别名信息错误，请检查网络环境。已切换至本地暂存文件')
            alias_data = await openfile(alias_file)
            if not alias_data:
                log.error(
                    '本地暂存别名文件为空，请自行使用浏览器访问 "https://api.yuzuai.xyz/maimaidx/maimaidxalias" 获取别名数据并保存在 "static/all_alias.json" 文件中并重启bot')
                raise ValueError
        except Exception:
            log.error(f'Error: {traceback.format_exc()}')
            log.error('获取所有曲目别名信息错误，请检查网络环境。已切换至本地暂存文件')
            alias_data = await openfile(alias_file)
            if not alias_data:
                log.error(
                    '本地暂存别名文件为空，请自行使用浏览器访问 "https://api.yuzuai.xyz/maimaidx/maimaidxalias" 获取别名数据并保存在 "static/all_alias.json" 文件中并重启bot')
                raise ValueError
        log.info('更新完毕')

    async def test(self, data: GroupMsg, match):
        await self.sendGroupMsg(data.group_id, msg(json_card({})))

    async def on_message(self, data: GroupMsg):
        gid = str(data.group_id)
        if gid in guess.Group:
            ans: str = data.raw_message.strip().lower()
            if ans.lower() in guess.Group[gid].answer:
                guess.Group[gid].end = True
                answer = msg(at(str(data.user_id)), '猜对了，答案是：\n',
                             pic_url(await new_draw_music_info(guess.Group[gid].music)))
                guess.end(gid)
                await self.sendGroupMsg(data.group_id, answer)
        for i in self.user_waiting:
            if i.qqid == data.user_id:
                print("触发")
                if data.message[0]['type'] == 'image':
                    ret = await download_pic(data.message[0]['data']['url'], f'./funcs/mirror/{data.user_id}')
                    if ret == -1:
                        await self.sendGroupMsg(data.group_id,
                                                msg("下载图片时出错了（图库图片无法下载，请使用收藏的表情包，不包括商城下载的表情包）"))
                        self.user_waiting.remove(i)
                        return
                    await split_and_mirror_gif(f'./funcs/mirror/{data.user_id}', f'./funcs/mirror/{data.user_id}.gif',i.direction)
                    with open(f'./funcs/mirror/{data.user_id}.gif', 'rb') as file:
                        pic = file.read()
                        pic = base64.b64encode(pic).decode()
                        await self.sendGroupMsg(data.group_id, msg(pic_b64(pic)))
                    self.user_waiting.remove(i)
                    print(self.user_waiting)
                break

    async def mute(self, data: GroupMsg, match):
        print(f"禁言{match.group(1)}，{match.group(2)}秒")  # 注意这玩意从1开头
        ret = await self.setGroupBan(data.group_id, match.group(1), match.group(2))
        if ret['status'] == 'failed':
            await self.sendGroupMsg(data.group_id, '禁言失败，请先将bot设置为管理员')
            return
        await self.sendGroupMsg(data.group_id, f'禁言{match.group(1)}成功')
        return

    async def worship(self, data: GroupMsg, match):
        path = ".\\funcs\\tkk\\"
        random_name = str(int(random.random() * 100000000))
        avatar_name = 'avatar_' + random_name
        base_name = 'base_' + random_name
        mp4_name = 'mp4_' + random_name
        gif_name = 'gif_' + random_name

        commands = [
            f'curl "http://q.qlogo.cn/headimg_dl?dst_uin={match.group(1)}&spec=640&img_type=jpg" --output {path}{avatar_name}.jpg',
            f'magick composite {path}{avatar_name}.jpg {path}mask.jpg -geometry 600x600+106+0 {path}{base_name}.jpg',
            f'ffmpeg -i {path}{base_name}.jpg -i {path}tkk.mp4 -filter_complex "[1:v]chromakey=0x00ff00:0.3:0.0[fg_keyed];[0:v][fg_keyed]overlay[out]" -map "[out]" -map 1:a -c:v libx264 -c:a aac -y {path}{mp4_name}.mp4',
            f'ffmpeg -i {path}{mp4_name}.mp4 -vf "scale=320:-1" -y {path}{gif_name}.gif',
            f'adb push {path}{gif_name}.gif /sdcard/shamrock/pics/{gif_name}.gif',
            f'del {path}{mp4_name}.mp4',
            f'del {path}{base_name}.jpg',
            f'del {path}{avatar_name}.jpg',
            f'del {path}{gif_name}.gif'
        ]
        # 使用 subprocess 运行命令
        for i in commands:
            result = subprocess.run(i, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print("出错了")
                print(result.stdout)
                print(result.stderr)
                await self.sendGroupMsg(data.group_id, '膜拜失败')
                return
        await self.sendGroupMsg(data.group_id, msg(pic(f'/sdcard/shamrock/pics/{gif_name}.gif')))
        return

    async def point(self, data: GroupMsg, match):
        if len(match.group(1)) >= 10:
            print('太长了')
            await self.sendGroupMsg(data.group_id, '太长了')
            return
        random_name = str(int(random.random() * 100000000))
        jpg_name = 'jpg_' + random_name
        path = ".\\funcs\\point\\"
        commands = [
            f'magick convert {path}base.jpg -font {path}msyh.ttc -fill black -pointsize 24 -gravity center -annotate +0+80 "{match.group(1)}" {path}{jpg_name}.jpg',
            f'adb push {path}{jpg_name}.jpg /sdcard/shamrock/pics/{jpg_name}.jpg'
        ]
        # 使用 subprocess 运行命令
        for i in commands:
            result = subprocess.run(i, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                log.error("出错了")
                print(result.stdout)
                print(result.stderr)
                await self.sendGroupMsg(data.group_id, '指人失败')
                return
        await self.sendGroupMsg(data.group_id, msg(pic(f'/sdcard/shamrock/pics/{jpg_name}.jpg')))
        return

    async def bro(self, data: GroupMsg, match):
        if len(match.group(1)) >= 10:
            await self.sendGroupMsg(data.group_id, '太长了')
            return
        random_name = str(int(random.random() * 100000000))
        jpg_name = 'jpg_' + random_name
        path = ".\\funcs\\bro\\"
        commands = [
            f'magick convert {path}base.jpg -font {path}msyh.ttc -fill black -pointsize 30 -gravity center -annotate +0-100 "{match.group(1)}" {path}{jpg_name}.jpg',
            f'adb push {path}{jpg_name}.jpg /sdcard/shamrock/pics/{jpg_name}.jpg'
        ]
        # 使用 subprocess 运行命令
        for i in commands:
            result = subprocess.run(i, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                log.error("出错了")
                print(result.stdout)
                print(result.stderr)
                await self.sendGroupMsg(data.group_id, '兄弟失败')
                return
        await self.sendGroupMsg(data.group_id, msg(pic(f'/sdcard/shamrock/pics/{jpg_name}.jpg')))
        return

    async def otto_speak(self, data: GroupMsg, match):
        if len(match.group(1)) >= 50:
            print('太长了')
            await self.sendGroupMsg(data.group_id, '太长了')
            return
        random_name = str(int(random.random() * 100000000))
        wav_name = 'wav_' + random_name
        HZYS.export(match.group(1), wav_name)
        path = "./funcs/otto/"
        commands = [
            f'ffmpeg -i {path}{wav_name}.wav {path}{wav_name}.mp3',
        ]
        # 使用 subprocess 运行命令
        for i in commands:
            result = subprocess.run(i, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print("出错了")
                print(result.stdout)
                print(result.stderr)
                await self.sendGroupMsg(data.group_id, '活字印刷失败')
                return
        await self.sendGroupMsg(data.group_id, msg(audio(f'/data/data/com.termux/files/home/Mybot/funcs/otto/{wav_name}.mp3')))
        return
    async def pic_mirror(self,data:GroupMsg,match):
        print(f'镜像：{data.user_id}')
        tmp = MirrorEvent()
        tmp.qqid = data.user_id
        direction = match.group(1)
        print(direction)
        if direction == '左':
            tmp.direction=0
        elif direction == '上':
            tmp.direction=1
        elif direction == '右':
            tmp.direction=2
        elif direction == '下':
            tmp.direction=3
        else:
            return
        self.user_waiting.append(tmp)
        await self.sendGroupMsg(data.group_id,'请发送图片')
        print(self.user_waiting)
    async def b50(self, data: GroupMsg, match):
        img_base64 = await generate(data.user_id, 'Dustwind')
        await self.sendGroupMsg(data.group_id, msg(pic_url(img_base64)))

    async def random_song(self, data: GroupMsg, match):
        try:
            diff = match.group(1)
            if diff == 'dx':
                tp = ['DX']
            elif diff == 'sd' or diff == '标准':
                tp = ['SD']
            else:
                tp = ['SD', 'DX']
            level = match.group(3)
            if match.group(2) == '':
                music_data = mai.total_list.filter(level=level, type=tp)
            else:
                music_data = mai.total_list.filter(level=level, diff=['绿黄红紫白'.index(match.group(2))], type=tp)
            if len(music_data) == 0:
                ret = '没有这样的乐曲哦。'
            else:
                ret = await new_draw_music_info(music_data.random())
            await self.sendGroupMsg(data.group_id, msg(pic_url(ret)))
        except:
            await self.sendGroupMsg(data.group_id, msg('随机命令错误，请检查语法'))

    async def day_mai(self, data: GroupMsg, match):
        wm_list = ['拼机', '推分', '越级', '下埋', '夜勤', '练底力', '练手法', '打旧框', '干饭', '抓绝赞', '收歌']
        h = hash(data.user_id)
        rp = h % 100
        wm_value = []
        for i in range(11):
            wm_value.append(h & 3)
            h >>= 2
        ret = f'\n今日人品值：{rp}\n'
        for i in range(11):
            if wm_value[i] == 3:
                ret += f'宜 {wm_list[i]}\n'
            elif wm_value[i] == 0:
                ret += f'忌 {wm_list[i]}\n'
        ret += f'{BOTNAME} Bot提醒您：打机时不要大力拍打或滑动哦\n今日推荐歌曲：'
        music = mai.total_list[h % len(mai.total_list)]
        await self.sendGroupMsg(data.group_id, msg(at(str(data.user_id)), ret, pic_url(await draw_music_info(music))))

    async def search_song(self, data: GroupMsg, match):
        name: str = match.group(1)
        if not name:
            return
        result = mai.total_list.filter(title_search=name)
        if len(result) == 0:
            await self.sendGroupMsg(data.group_id, '没有找到这样的乐曲。')
        elif len(result) == 1:
            ret = await new_draw_music_info(result.random())
            await self.sendGroupMsg(data.group_id, msg(pic_url(ret)))
        elif len(result) < 50:
            search_result = ''
            for music in sorted(result, key=lambda i: int(i.id)):
                search_result += f'{music.id}. {music.title}\n'
            await self.sendGroupMsg(data.group_id, msg(search_result.strip()))
        else:
            await self.sendGroupMsg(data.group_id, msg(f'结果过多（{len(result)} 条），请缩小查询范围。'))

    async def guess_song(self, data: GroupMsg, match):
        gid = str(data.group_id)
        if data.group_id not in guess.config['enable']:
            await self.sendGroupMsg(data.group_id, msg('该群已关闭猜歌功能，开启请输入 /开启猜歌'))
            return
        if gid in guess.Group:
            await self.sendGroupMsg(data.group_id, msg('该群已有正在进行的猜歌'))
            return
        await guess.start(gid)
        await self.sendGroupMsg(data.group_id,
                                msg('我将从热门乐曲中选择一首歌，每隔8秒描述它的特征，请输入歌曲的 id 标题 或 别名（需bot支持，无需大小写） 进行猜歌（DX乐谱和标准乐谱视为两首歌）'))
        await asyncio.sleep(4)
        for cycle in range(7):
            if data.group_id not in guess.config['enable'] or gid not in guess.Group or guess.Group[gid].end:
                break
            if cycle < 6:
                await self.sendGroupMsg(data.group_id, msg(f'{cycle + 1}/7 这首歌{guess.Group[gid].options[cycle]}'))
                await asyncio.sleep(8)
            else:
                await self.sendGroupMsg(data.group_id,
                                        msg(f'7/7 这首歌封面的一部分是：\n', pic_url(guess.Group[gid].img),
                                            '答案将在30秒后揭晓'))
                for _ in range(30):
                    await asyncio.sleep(1)
                    if gid in guess.Group:
                        if data.group_id not in guess.config['enable'] or guess.Group[gid].end:
                            return
                    else:
                        return
                guess.Group[gid].end = True
                answer = msg('答案是：\n', pic_url(await new_draw_music_info(guess.Group[gid].music)))
                guess.end(gid)
                await self.sendGroupMsg(data.group_id, answer)

    async def reset_guess(self, data: GroupMsg, match):
        gid = str(data.group_id)
        # if not priv.check_priv(ev, priv.ADMIN):
        #    msg = '仅允许管理员开启'
        #    return
        if gid in guess.Group:
            ret = '已重置该群猜歌'
            guess.end(gid)
        else:
            ret = '该群未处在猜歌状态'
        await self.sendGroupMsg(data.group_id, ret)

    async def guess_on_off(self, data: GroupMsg, match):
        # if not priv.check_priv(ev, priv.ADMIN):
        #    msg = '仅允许管理员开启'
        gid = data.group_id
        arg = match.group(1)
        if arg == '开启':
            ret = await guess.on(gid)
        elif arg == '关闭':
            ret = await guess.off(gid)
        else:
            ret = '指令错误'

        await self.sendGroupMsg(data.group_id, ret)

    async def what_song(self,data:GroupMsg,match):
        name: str = match.group(1)
        ret = mai.total_alias_list.by_alias(name)
        if not ret:
            await self.sendGroupMsg(data.group_id,msg(at(str(data.user_id)),'未找到此歌曲\n可以使用 添加别名 指令给该乐曲添加别名'))
            return
        if len(ret) != 1:
            string = f'找到{len(ret)}个相同别名的曲目：\n'
            for songs in ret:
                string += f'{songs.ID}：{songs.Name}\n'
            await self.sendGroupMsg(data.group_id,msg(at(str(data.user_id)),string))
            return
        music = mai.total_list.by_id(str(ret[0].ID))
        await self.sendGroupMsg(data.group_id, msg(at(str(data.user_id)), '您要找的是不是：' ,pic_url(await new_draw_music_info(music))))
        return

    async def what_alias(self,data:GroupMsg,match):
        findid = bool(match.group(1))
        name = match.group(2)
        if findid and name.isdigit():
            alias_id = mai.total_alias_list.by_id(name)
            if not alias_id:
                await self.sendGroupMsg(data.group_id, msg(at(str(data.user_id)),
                                                           '未找到此歌曲\n可以使用 添加别名 指令给该乐曲添加别名'))
                return
            else:
                alias = alias_id
        else:
            alias = mai.total_alias_list.by_alias(name)
            if not alias:
                if name.isdigit():
                    alias_id = mai.total_alias_list.by_id(name)
                    if not alias_id:
                        await self.sendGroupMsg(data.group_id, msg(at(str(data.user_id)),
                                                                   '未找到此歌曲\n可以使用 添加别名 指令给该乐曲添加别名'))
                        return
                    else:
                        alias = alias_id
                else:
                    await self.sendGroupMsg(data.group_id, msg(at(str(data.user_id)),
                                                               '未找到此歌曲\n可以使用 添加别名 指令给该乐曲添加别名'))
                    return
        if len(alias) != 1:
            string = []
            for songs in alias:
                alias_list = '\n'.join(songs.Alias)
                string.append(f'ID：{songs.ID}\n{alias_list}')
            await self.sendGroupMsg(data.group_id,msg(at(str(data.user_id)),f'找到{len(alias)}个相同别名的曲目：\n' + '\n======\n'.join(string)))
            return

        if len(alias[0].Alias) == 1:
            await self.sendGroupMsg(data.group_id, msg(at(str(data.user_id)),
                                                       '该曲目没有别名'))
            return

        string = f'该曲目有以下别名：\nID：{alias[0].ID}\n'
        string += '\n'.join(alias[0].Alias)
        await self.sendGroupMsg(data.group_id, msg(at(str(data.user_id)),string))
        return

    async def rating_table_pf(self,data:GroupMsg,match):
        qqid = data.user_id
        rating = match.group(1)
        if rating in levelList[:5]:
            await self.sendGroupMsg(data.group_id,msg(at(str(data.user_id)),'只支持查询lv6-15的完成表'))
        elif rating in levelList[5:]:
            img = await rating_table_draw(qqid, rating)
            await self.sendGroupMsg(data.group_id, msg(at(str(data.user_id)),pic_url(img)))

