# -*- encoding: utf-8 -*-
'''
@file      :爬卧龙小说.py
@Time      :2021-07-21 01:11:43
@Author    :Karcyril
@Software  :Visual Studio Code
'''

from typing import Container
import requests
from bs4 import BeautifulSoup
import re
import os
import time
import sys

head = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Mobile Safari/537.36"}

path = sys.argv[0]
filePath = os.path.split(os.path.realpath(__file__))[0]


def main():

    baseUrl = input('请输入卧龙小说（www.paper027.com）的章节列表：\n')
    getBaseData(baseUrl)


def getBaseData(baseUrl):
    ret = requests.request(url=baseUrl, headers=head, method='GET')
    soup = BeautifulSoup(ret.text, 'html.parser')
    container = soup.select('.container')[2]
    tagA = container.select('.chapters span.chapterTitle a')
    pLink = re.compile('href="(.*?)"')
    pTitle = re.compile('title="(.*?)"')

    bookTitle = container.select('div:nth-child(1) a:nth-child(5)')[0].text

    with open(filePath+'\\'+bookTitle+'.txt', 'a+')as fp:
        fp.write('spider by Karcyril.\n\n')

    for link in reversed(tagA):
        linkUrl = re.search(pLink, str(link)).group(1)
        linkTitle = re.search(pTitle, str(link)).group(1)
        getLinkData(linkUrl, linkTitle, bookTitle)

    print('完成...')
    os.system('pause')


def getLinkData(link, title, bookTitle):
    ret = requests.request(url=link, headers=head, method='GET')
    soup = BeautifulSoup(ret.text, 'html.parser')
    tagPs = soup.select('#contentsource p')

    # 添加章节标题
    with open(filePath+'\\'+bookTitle+'.txt', 'a+')as fp:
        fp.write(title+'\n')

    for tagP in tagPs:
        # pText = re.search('<p>(.*?)</p>', str(tagP)).group(0)
        with open(filePath+'\\'+bookTitle+'.txt', 'a+')as fp:
            fp.write(tagP.text+'\n')

    print('已写入章节%s' % (title))
    time.sleep(1)


if __name__ == "__main__":
    main()
