# -*- coding: UTF-8 -*-
# 鬼畜音源的活字印刷
# 作者：DSP_8192
import time
import re
from pydub import AudioSegment
from pypinyin import lazy_pinyin
import csv
from pathlib import Path


# 文件路径转文件夹路径
def _fileName2FolderName(fileName):
    for i in range(len(fileName) - 1, -1, -1):
        if fileName[i] == '\\' or fileName[i] == '/':
            return fileName[0:i + 1]


class huoZiYinShua:
    def __init__(self, voicePath, dictionaryPath, originPath):
        self.__voicePath = voicePath
        self.__dictionary = dict(csv.reader(open(dictionaryPath)))
        self.__origin = dict(csv.reader(open(originPath)))
        print(self.__dictionary)
        print(self.__origin)

    # 直接导出
    def export(self, rawData, wavname):
        self.__execute(rawData)
        filePath = f'./funcs/otto/{wavname}.wav'
        self.__export(filePath)
        print("已导出" + filePath)
        print("原文:" + rawData)

    # 生成中间文件
    def __execute(self, rawData):
        missingPinyin = []
        self.__concatenated = AudioSegment.empty()

        # 预处理，转为小写
        rawData = rawData.lower()
        sentence = ""
        # 处理每一个符号
        for ch in rawData:
            if ch in self.__dictionary:
                # 词典中存在匹配，转换
                sentence += self.__dictionary[ch] + " "
            else:
                # 保持不变
                sentence += ch + ' '
        # 将汉字转换成拼音
        pinyinTexts = lazy_pinyin(sentence)
        # 拆成单独的字
        pinyinText = ""
        for i in pinyinTexts:
            pinyinText += i

        for key,value in self.__origin.items():
            pinyinText = pinyinText.replace(key,value)
        print(pinyinText)
        res = re.split(r'(\s+)',pinyinText)
        pinyinTexts = [i for i in res if i]
        for text in pinyinTexts:
            for word in text.split():
                # 拼接每一个字
                try:
                    self.__concatenated += AudioSegment.from_file(self.__voicePath + word + ".wav", format="wav")
                    self.__concatenated += AudioSegment.silent(duration=30)
                except:
                    if word not in missingPinyin:
                        missingPinyin.append(word)
                    self.__concatenated += AudioSegment.silent(duration=250)
        self.__concatenated += AudioSegment.silent(duration=400)
        # 如果缺失拼音，则发出警告
        if len(missingPinyin) != 0:
            print("警告：缺失{}".format(missingPinyin))
    # 导出wav文件
    def __export(self, filePath):
        folderPath = _fileName2FolderName(filePath)
        if not Path(folderPath).exists():
            Path(folderPath).mkdir()
        self.__concatenated.export(filePath, format="wav")


HZYS = huoZiYinShua("./funcs/otto/sources/", "./funcs/otto/dictionary.csv", "./funcs/otto/origin.csv")
