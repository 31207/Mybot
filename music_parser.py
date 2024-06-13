# -*- coding: utf-8 -*-
import mysql
from main import config
from bot import *
import time
import threading
from lxml import etree
import re
import requests

# 重要数据表名配置
music_table = config["music_table"]
userinfo_table = config["userinfo_table"]
usersong_table = config["usersong_table"]
flag_table = config["flag_table"]

allcount = config["allcount"]
list_count = config["list_count"]
channel_id = config["channel_id"]
autoflag = True


def to_int(string):
    for i in string:
        if ord(i) > 57 or ord(i) < 48:
            return -1
    return int(string)
def lessthan(elem):
    return elem["time"]

def get_xpath(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    with open('data.html', 'a+', encoding='utf-8') as file:
        file.write(response.text)
    return etree.HTML(response.text)
def parse_songinfo_wyy(url):    # 网易云音乐网页解析
    exp = "//meta[@name='description']/@content"  # lxml的用法详见https://www.w3cschool.cn/lxml/_lxml-v4n63fjs.html
    html = get_xpath(url)
    res = html.xpath(exp)
    text = res[0]
    name = re.findall(r"歌曲名《(.+?)》，", text)
    artist = re.findall(r"由 (.+?) 演唱", text)
    return name + artist
def parse_songinfo_qq(url):    # QQ音乐网页解析
    exp = "//meta[@name='description']/@content"  # lxml的用法详见https://www.w3cschool.cn/lxml/_lxml-v4n63fjs.html
    html = get_xpath(url)
    res = html.xpath(exp)
    text = res[0]
    name = re.findall(r"歌曲：(.+?)，", text)
    artist = re.findall(r"歌手：(.+?)。", text)
    return name + artist
def parse_songinfo_kugou(url):    # 酷狗音乐网页解析
    exp = "//meta[@name='keywords']/@content"  # lxml的用法详见https://www.w3cschool.cn/lxml/_lxml-v4n63fjs.html
    html = get_xpath(url)
    res = html.xpath(exp)
    print(res)
    text = res[0].split(",")
    return text[0:2]
def parse_songinfo_kuwo(url):    # 酷我音乐网页解析，其实和酷狗是一样的
    exp = "//meta[@name='keywords']/@content"  # lxml的用法详见https://www.w3cschool.cn/lxml/_lxml-v4n63fjs.html
    html = get_xpath(url)
    res = html.xpath(exp)
    print(res)
    text = res[0].split(",")
    return text[0:2]
class autoclear(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        mc = mysql.MysqlDb(host=config["host"],
                           port=config["port"],
                           user=config["user"],
                           passwd=config["pwd"],
                           db=config["databaseName"])
        while autoflag:
            time.sleep(1)
            if mc.get_loop_flag(flag_table):

                time_now = time.localtime(time.time())
                if time_now.tm_mday == 1 and mc.get_autoclear_flag(flag_table) == False:
                    mc.set_autoclear_flag(flag_table, True)
                    mc.modify_alluser_count(userinfo_table)
                    log.info("提示：今天是1号，已自动清空点歌次数。")
                if time_now.tm_mday != 1 and mc.get_autoclear_flag(flag_table) == True:
                    mc.set_autoclear_flag(flag_table, False)
    def __del__(self):
        del self