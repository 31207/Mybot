import time
from io import BytesIO
from typing import Dict, Union

import aiofiles
from PIL import Image, ImageDraw

from .image import DrawText, draw_gradient
from .maimai_best_50 import *
from .maimaidx_api_data import *
from .maimaidx_error import *
from .maimaidx_music import Music, RaMusic, download_music_pictrue, mai


async def draw_music_info(music: Music):
    """
    旧的谱面详情
    """
    im = Image.open(maimaidir / 'music_bg.png').convert('RGBA')
    genre = Image.open(maimaidir / f'music-{category[music.basic_info.genre]}.png')
    cover = Image.open(await download_music_pictrue(music.id)).resize((360, 360))
    ver = Image.open(maimaidir / f'{music.type}.png').resize((94, 35))
    line = Image.new('RGBA', (400, 2), (255, 255, 255, 255))

    im.alpha_composite(genre, (150, 170))
    im.alpha_composite(cover, (170, 260))
    im.alpha_composite(ver, (435, 585))
    im.alpha_composite(line, (150, 710))

    dr = ImageDraw.Draw(im)
    tb = DrawText(dr, TBFONT)
    sy = DrawText(dr, SIYUAN)

    tb.draw(200, 195, 24, music.id, anchor='mm')
    sy.draw(410, 195, 22, music.basic_info.genre, anchor='mm')
    title = music.title
    if coloumWidth(title) > 35:
        title = changeColumnWidth(title, 34) + '...'
    sy.draw_partial_opacity(350, 660, 30, title, 1, anchor='mm')
    sy.draw_partial_opacity(350, 690, 12, music.basic_info.artist, 1, anchor='mm')
    sy.draw_partial_opacity(150, 725, 15, f'Version: {music.basic_info.version}', 1, anchor='lm')
    sy.draw_partial_opacity(550, 725, 15, f'BPM: {music.basic_info.bpm}', 1, anchor='rm')
    for n, i in enumerate(list(map(str, music.ds))):
        if n == 4:
            color = (195, 70, 231, 255)
        else:
            color = (255, 255, 255, 255)
        tb.draw(160 + 95 * n, 814, 25, i, color, 'mm')
    sy.draw(350, 980, 14, f'Designed by Yuri-YuzuChaN | Generated by {BOTNAME} BOT', (255, 255, 255, 255), 'mm', 1, (159, 81, 220, 255))
    msg = image_to_base64(im)

    return msg


async def music_play_data(qqid: int, songs: str) -> Union[str,None]:
    """
    谱面游玩
    """
    try:
        version = list(set(_v for _v in plate_to_version.values()))
        data = await maiApi.query_user('plate', qqid=qqid, version=version)

        player_data: list[dict[str, Union[float, str, int]]] = []
        for i in data['verlist']:
            if i['id'] == int(songs):
                player_data.append(i)
        if not player_data:
            return '您未游玩该曲目'
        
        player_data.sort(key=lambda a: a['level_index'])
        music = mai.total_list.by_id(songs)

        im = Image.open(maimaidir / 'info_bg.png').convert('RGBA')
        
        dr = ImageDraw.Draw(im)
        tb = DrawText(dr, TBFONT)
        sy = DrawText(dr, SIYUAN)

        im.alpha_composite(Image.open(await download_music_pictrue(music.id)).resize((235, 235)), (65, 165))
        im.alpha_composite(Image.open(maimaidir / f'{music.basic_info.version}.png').resize((150, 72)), (690, 335))
        im.alpha_composite(Image.open(maimaidir / f'{music.type}.png').resize((80, 30)), (600, 368))

        color = (140, 44, 213, 255)
        title = music.title
        if coloumWidth(title) > 35:
            title = changeColumnWidth(title, 34) + '...'
        sy.draw(320, 185, 24, title, color, 'lm')
        sy.draw(320, 225, 18, music.basic_info.artist, color, 'lm')
        tb.draw(320, 310, 20, f'BPM: {music.basic_info.bpm}', color, 'lm')
        tb.draw(320, 380, 18, f'ID {music.id}', color, 'lm')
        sy.draw(500, 380, 16, music.basic_info.genre, color, 'mm')

        y = 120
        TEXT_COLOR = [(14, 117, 54, 255), (199, 69, 12, 255), (175, 0, 50, 255), (103, 20, 141, 255), (103, 20, 141, 255)]
        for _data in player_data:
            ds: float = music.ds[_data['level_index']]
            lv: int = _data['level_index']
            ra, rate = computeRa(ds, _data['achievements'], israte=True)

            rank = Image.open(maimaidir / f'UI_TTR_Rank_{rate}.png').resize((120, 57))
            im.alpha_composite(rank, (430, 515 + y * lv))
            if _data['fc']:
                fc = Image.open(maimaidir / f'UI_CHR_PlayBonus_{fcl[_data["fc"]]}.png').resize((76, 76))
                im.alpha_composite(fc, (575, 511 + y * lv))
            if _data['fs']:
                fs = Image.open(maimaidir / f'UI_CHR_PlayBonus_{fsl[_data["fs"]]}.png').resize((76, 76))
                im.alpha_composite(fs, (650, 511 + y * lv))

            p, s = f'{_data["achievements"]:.4f}'.split('.')
            r = tb.get_box(p, 36)
            tb.draw(90, 545 + y * lv, 30, ds, anchor='mm')
            tb.draw(200, 567 + y * lv, 36, p, TEXT_COLOR[lv], 'ld')
            tb.draw(200 + r[2], 565 + y * lv, 30, f'.{s}%', TEXT_COLOR[lv], 'ld')
            tb.draw(790, 545 + y * lv, 30, ra, TEXT_COLOR[lv], 'mm')

        sy.draw(450, 1180, 20, f'Designed by Yuri-YuzuChaN | Generated by {BOTNAME} BOT', (159, 81, 220, 255), 'mm', 2, (255, 255, 255, 255))
        msg = image_to_base64(im)
    except UserNotFoundError as e:
        msg = str(e)
    except UserDisabledQueryError as e:
        msg = str(e)
    except Exception as e:
        log.error(traceback.format_exc())
        msg = f'未知错误：{type(e)}\n请联系Bot管理员'
    return msg


async def music_play_data_dev(qqid: int, songs: str) -> Union[str,None]:
    """
    带Token的谱面游玩
    """
    try:
        data = await maiApi.query_user_dev(qqid=qqid)

        player_data: list[dict[str, Union[float, str, int]]] = []
        for i in data['records']:
            if i['song_id'] == int(songs):
                player_data.append(i)
        if not player_data:
            return '您未游玩该曲目'
        
        DXSTAR_DEST = [0, 540, 530, 520, 510, 500]

        player_data.sort(key=lambda a: a['level_index'])
        music = mai.total_list.by_id(songs)

        im = Image.open(maimaidir / 'info_bg_2.png').convert('RGBA')
        dxstar = [Image.open(maimaidir / f'UI_RSL_DXScore_Star_0{_ + 1}.png').resize((20, 20)) for _ in range(3)]

        dr = ImageDraw.Draw(im)
        tb = DrawText(dr, TBFONT)
        sy = DrawText(dr, SIYUAN)

        im.alpha_composite(Image.open(await download_music_pictrue(music.id)).resize((235, 235)), (65, 165))
        im.alpha_composite(Image.open(maimaidir / f'{music.basic_info.version}.png').resize((150, 72)), (690, 335))
        im.alpha_composite(Image.open(maimaidir / f'{music.type}.png').resize((80, 30)), (600, 368))

        color = (140, 44, 213, 255)
        title = music.title
        if coloumWidth(title) > 35:
            title = changeColumnWidth(title, 34) + '...'
        sy.draw(320, 185, 24, title, color, 'lm')
        sy.draw(320, 225, 18, music.basic_info.artist, color, 'lm')
        tb.draw(320, 310, 20, f'BPM: {music.basic_info.bpm}', color, 'lm')
        tb.draw(320, 380, 18, f'ID {music.id}', color, 'lm')
        sy.draw(500, 380, 16, music.basic_info.genre, color, 'mm')

        y = 120
        TEXT_COLOR = [(14, 117, 54, 255), (199, 69, 12, 255), (175, 0, 50, 255), (103, 20, 141, 255), (103, 20, 141, 255)]
        for _data in player_data:
            ds: float = _data['ds']
            lv: int = _data['level_index']
            dxscore = _data['dxScore']
            ra, rate = computeRa(ds, _data['achievements'], israte=True)

            rank = Image.open(maimaidir / f'UI_TTR_Rank_{rate}.png').resize((120, 57))
            im.alpha_composite(rank, (358, 518 + y * lv))

            _dxscore = sum(music.charts[lv].notes) * 3
            diff_sum_dx = dxscore / _dxscore * 100
            dxtype, dxnum = dxScore(diff_sum_dx)
            for _ in range(dxnum):
                im.alpha_composite(dxstar[dxtype], (DXSTAR_DEST[dxnum] + 20 * _, 550 + y * lv))

            if _data['fc']:
                fc = Image.open(maimaidir / f'UI_CHR_PlayBonus_{fcl[_data["fc"]]}.png').resize((76, 76))
                im.alpha_composite(fc, (605, 511 + y * lv))
            if _data['fs']:
                fs = Image.open(maimaidir / f'UI_CHR_PlayBonus_{fsl[_data["fs"]]}.png').resize((76, 76))
                im.alpha_composite(fs, (670, 511 + y * lv))

            p, s = f'{_data["achievements"]:.4f}'.split('.')
            r = tb.get_box(p, 36)
            tb.draw(90, 545 + y * lv, 30, ds, anchor='mm')
            tb.draw(175, 567 + y * lv, 36, p, TEXT_COLOR[lv], 'ld')
            tb.draw(175 + r[2], 565 + y * lv, 30, f'.{s}%', TEXT_COLOR[lv], 'ld')
            tb.draw(550, (535 if dxnum != 0 else 548) + y * lv, 20, f'{dxscore}/{_dxscore}', TEXT_COLOR[lv], 'mm')
            tb.draw(790, 545 + y * lv, 30, ra, TEXT_COLOR[lv], 'mm')

        sy.draw(450, 1180, 20, f'Designed by Yuri-YuzuChaN | Generated by {BOTNAME} BOT', (159, 81, 220, 255), 'mm', 2, (255, 255, 255, 255))
        msg = image_to_base64(im)

    except UserNotFoundError as e:
        msg = str(e)
    except UserDisabledQueryError as e:
        msg = str(e)
    except Exception as e:
        log.error(traceback.format_exc())
        msg = f'未知错误：{type(e)}\n请联系Bot管理员'
    return msg


async def new_draw_music_info(music: Music) -> str:
    """
    新的查看谱面
    """
    im = Image.open(maimaidir / 'song_bg.png').convert('RGBA')
    dr = ImageDraw.Draw(im)
    tb = DrawText(dr, TBFONT)
    sy = DrawText(dr, SIYUAN)
    
    default_color = (140, 44, 213, 255)
    
    im.alpha_composite(Image.open(await download_music_pictrue(music.id)), (205, 305))
    im.alpha_composite(Image.open(maimaidir / f'{music.basic_info.version}.png').resize((250, 120)), (1340, 590))
    im.alpha_composite(Image.open(maimaidir / f'{music.type}.png'), ((1150, 643)))
    
    title = music.title
    if coloumWidth(title) > 42:
        title = changeColumnWidth(title, 41) + '...'
    sy.draw(640, 350, 40, title, default_color, 'lm')
    sy.draw(640, 425, 30, music.basic_info.artist, default_color, 'lm')
    tb.draw(705, 548, 40, music.basic_info.bpm, default_color, 'lm')
    tb.draw(640, 665, 40, f'ID {music.id}', default_color, 'lm')
    sy.draw(970, 665, 30, music.basic_info.genre, default_color, 'mm')
    
    for num, _ in enumerate(music.level):
        if num == 4:
            color = default_color
        else:
            color = (255, 255, 255, 255)
        tb.draw(280, 955 + 110 * num, 30, f'{music.level[num]}({music.ds[num]})', color, 'mm')
        tb.draw(475, 945 + 110 * num, 40, f'{round(music.stats[num].fit_diff, 2):.2f}' if music.stats and music.stats[num] else '-', default_color, anchor='mm')
        if num > 1:
            sy.draw(585 + 414 * (num - 2), 1523, 22, music.charts[num].charter, color, 'mm')
        
        notes = list(music.charts[num].notes)
        tb.draw(658, 945 + 110 * num, 40, sum(notes), default_color, 'mm')
        if len(notes) == 4:
            notes.insert(3, 0)
        for n, c in enumerate(notes):
            tb.draw(834 + 175 * n, 945 + 110 * num, 40, c, default_color, 'mm')
    msg = image_to_base64(im)
    
    return msg


async def update_rating_table() -> str:
    """
    更新定数表
    """
    try:
        bg_color = [(111, 212, 61, 255), (248, 183, 9, 255), (255, 129, 141, 255), (159, 81, 220, 255), (219, 170, 255, 255)]
        dx = Image.open(maimaidir / 'DX.png').convert('RGBA').resize((44, 16))
        top = Image.open(maimaidir / 'top.png').convert('RGBA')
        bottom = Image.open(maimaidir / 'UI_CMN_TrackStart_MugenMap.png').convert('RGBA').resize((1500, 278))
        diff = [Image.new('RGBA', (75, 75), color) for color in bg_color]
        atime = 0
        for ra in levelList[5:]:
            _otime = time.time()
            musiclist = mai.total_list.lvList(True)
            
            if ra in levelList[-3:]:
                bg = ratingdir / '14.png'
                ralist = levelList[-3:]
            else:
                bg = ratingdir / f'{ra}.png'
                ralist = [ra]

            lvlist: Dict[str, List[RaMusic]] = {}
            for lvs in list(reversed(ralist)):
                for _ra in musiclist[lvs]:
                    lvlist[_ra] = musiclist[lvs][_ra]

            if ra in ['14', '14+', '15']:
                lvtext = 'Level.14 - 15   定数表'
            else:
                lvtext = f'Level.{ra}   定数表'
            
            lines = sum([(len(lvlist[_]) // 15) + 1 for _ in lvlist])
            
            width, height = 1500, 570 + 85 * lines
            im = draw_gradient(width, height)
            dr = ImageDraw.Draw(im)
            sy = DrawText(dr, SIYUAN)
            meiryo = DrawText(dr, MEIRYO)
            im.alpha_composite(top)
            im.alpha_composite(bottom, (0, height - bottom.size[1] + 10))
            sy.draw(750, 120, 65, lvtext, (0, 0, 0, 255), 'mm')
            meiryo.draw(750, height - 30, 25, f'Designed by Yuri-YuzuChaN & BlueDeer233 | Generated by {BOTNAME} BOT', (103, 20, 141, 255), 'mm', 3, (255, 255, 255, 255))
            y = 120
            for lv in lvlist:
                y += 10
                sy.draw(100, y + 120, 50, lv, (0, 0, 0, 255), 'mm')
                for num, music in enumerate(lvlist[lv]):
                    if num % 15 == 0:
                        x = 200
                        y += 85
                    else:
                        x += 85
                    cover = await download_music_pictrue(music.id)
                    if int(music.lv) != 3:
                        cover_bg = diff[int(music.lv)]
                        cover_bg.alpha_composite(Image.open(cover).convert('RGBA').resize((65, 65)), (5, 5))
                    else:
                        cover_bg = Image.open(cover).convert('RGBA').resize((75, 75))
                    im.alpha_composite(cover_bg, (x, y))
                    if music.type == 'DX':
                        im.alpha_composite(dx, (x + 31, y))
                if not lvlist[lv]:
                    y += 85
            
            by = BytesIO()
            im.save(by, 'PNG')
            async with aiofiles.open(bg, 'wb') as f:
                await f.write(by.getbuffer())
            _ntime = int(time.time() - _otime)
            atime += _ntime
            log.info(f'lv.{ra} 定数表更新完成，耗时：{_ntime}s')
        log.info(f'定数表更新完成，共耗时{atime}s')
        return f'定数表更新完成，共耗时{atime}s'
    except Exception as e:
        log.error(traceback.format_exc())
        return f'定数表更新失败，Error: {e}'


async def rating_table_draw(qqid: int, rating: str) -> str:
    try:
        version = list(set(_v for _v in plate_to_version.values()))
        data = await maiApi.query_user('plate', qqid=qqid, version=version)
        
        if rating in levelList[-3:]:
            bg = ratingdir / '14.png'
            ralist = levelList[-3:]
        else:
            bg = ratingdir / f'{rating}.png'
            ralist = [rating]
        
        fromid = {}
        for _data in data['verlist']:
            if _data['level'] in ralist:
                if (id := str(_data['id'])) not in fromid:
                    fromid[id] = {}
                fromid[id][str(_data['level_index'])] = {
                    'achievements': _data['achievements'],
                    'level': _data['level']
                }

        musiclist = mai.total_list.lvList(True)
        lvlist: Dict[str, List[RaMusic]] = {}
        for lv in list(reversed(ralist)):
            for _ra in musiclist[lv]:
                lvlist[_ra] = musiclist[lv][_ra]
        
        im = Image.open(bg).convert('RGBA')
        b2 = Image.new('RGBA', (75, 75), (0, 0, 0, 64))
        y = 138
        for ra in lvlist:
            y += 10
            for num, music in enumerate(lvlist[ra]):
                if num % 15 == 0:
                    x = 198
                    y += 85
                else:
                    x += 85
                if music.id in fromid and music.lv in fromid[music.id]:
                    ra, rate = computeRa(music.ds, fromid[music.id][music.lv]['achievements'], israte=True)
                    im.alpha_composite(b2, (x + 2, y - 18))
                    rank = Image.open(maimaidir / f'UI_TTR_Rank_{rate}.png').resize((78, 36))
                    im.alpha_composite(rank, (x, y))
        
        msg = image_to_base64(im)
        
    except UserNotFoundError as e:
        msg = str(e)
    except UserDisabledQueryError as e:
        msg = str(e)
    except Exception as e:
        log.error(traceback.format_exc())
        msg = f'未知错误：{type(e)}\n请联系Bot管理员'
    return msg