# -*- encoding: utf-8 -*-
'''
@file      :N站爬虫.py
@Time      :2022-11-06 22:07:45
@Author    :Karcyril
@Software  :Visual Studio Code
'''

import re
from bs4 import BeautifulSoup
import requests
import os
import shutil
from multiprocessing import Pool
from myUtils import askUrl as askUrl
# import myUtils
import time


from requests.exceptions import Timeout

# Your source directory
basePath = 'D:/absolution/spider'

# Destination
destDir = 'D:/absolution/电影/漫画/2d'

# 代理
proxies = {
    'http': 'http://127.0.0.1:7890/',
    'https': 'http://127.0.0.1:7890/'
}  # 你的科学上网工具提供的端口

# askUrl = myUtils.AskUrl()


def main():
    # 用于打印彩色字体
    if os.name == 'nt':
        os.system('')

    while(getCartoon(checkUrl(input('\033[1;36;40m请输入喵绅士漫画网址(输入q退出，save保存并添加封面):\033[0m')))):
        pass


def getCartoon(articleUrl):

    # pTitle = re.compile(r'''<div id="info">.*?<h1>(.*?)</h1>''', re.S)
    # pool = Pool(processes=5)

    if(articleUrl.upper() == "Q"):
        return False

    if(articleUrl.upper() == "SAVE"):
        moveDir()
        return True
    if(articleUrl.upper() == "S"):
        moveDir()
        return True

    if(articleUrl.upper() == "RM"):
        removeTree()
        return True

    imgInfos = []

    # 使用代理获取漫画页面文本
    resp = askUrl.request(url=articleUrl, proxies=proxies)

    # 获取h1标签的文本
    soup = BeautifulSoup(resp.text, 'html.parser')
    titleElem = soup.select('div#info h2')
    # 标题可能为空，此时取英文标题
    if(titleElem):
        title = titleElem[0].get_text()
    else:
        title = soup.select('div#info h1.title')[0].get_text()
    # title = pTitle.findall(resp.text)[0]
    # 替换文件夹敏感字符
    title = title.replace('<', '-').replace('>', '-').replace('?', '-').replace(':', '-').replace(
        '|', '-').replace('/', '-').replace('\\', '-').replace('"', '-').replace('*', '-')
    mPath = basePath+'/'+title
    createDir(mPath)

    # 图片列表就再当前页面
    pageUrl = articleUrl

    soup = BeautifulSoup(askUrl.request(url=pageUrl).text, 'html.parser')

    imgs = soup.select('div.thumbs div.thumb-container img.lazyload')

    print('\033[1;33;40m当前漫画：%s,\n等待3秒后下载...\033[0m' % (title))
    time.sleep(3)

    resp2 = askUrl.request(url=str(pageUrl)+'/1/', proxies=proxies)
    soup2 = BeautifulSoup(resp2.text, 'html.parser')

    downImg = soup2.select('div#content section#image-container img')

    downUrl = re.search('src="(.+//.+/.+/.+/).*"', str(downImg)).group(1)

    for img in imgs:

        thumbUrl = re.search('src="(.*?)"', str(img)).group(1)
        # 缩略图的文件名
        tempName = thumbUrl.split('/')[-1]
        # 文件后缀
        suffix = tempName.split('.')[-1]
        # 文件索引
        count = re.search('(\d+)*.*', str(tempName)).group(1)

        imgFileName = str(count)+'.'+str(suffix)

        imgUrl = str(downUrl)+str(count)+'.'+str(suffix)
        imgInfo = {}
        imgInfo['url'] = imgUrl
        imgInfo['fileName'] = imgFileName
        imgInfo['mPath'] = mPath
        imgInfos.append(imgInfo)

        # 获取单张漫画
        multiGetImg(imgInfo)

    # # 开5个进程
    # pool.map(multiGetImg, imgInfos)
    # pool.close()
    # pool.join()
    print('\033[1;32;40m下载完成...\033[0m\a')

    return True


def multiGetImg(imgInfo):
    imgUrl = imgInfo['url']
    imgFileName = imgInfo['fileName']
    mPath = imgInfo['mPath']
    # img = imgInfo['img']
    print('下载中：%s' % (imgFileName))
    resp = askUrl.request(url=imgUrl)

    # # 处理404错误
    # if(resp.status_code == 404):
    #     imgUrl = re.search(
    #         'onerror="javascript:this.src=\'(.*?)\'.*?"', str(img)).group(1)
    #     resp = askUrl.request(url=imgUrl)
    #     if(resp.status_code == 404):
    #         # 如果依然返回404则直接跳过
    #         return

    imgData = resp.content

    # 以二进制模式创建文件
    with open(mPath+'/'+imgFileName, 'wb+') as fp:
        fp.write(imgData)
        print('下载成功:'+mPath+'/'+imgFileName)


def createDir(mPath):
    if not os.path.exists(mPath):
        # 递归创建文件夹
        os.makedirs(mPath)


def checkUrl(articleUrl):
    if(articleUrl[-1] == '/'):
        articleUrl = articleUrl[:-1]
    return articleUrl


def moveDir():

    path = basePath
    listDir = os.listdir(path)
    haveDup = False

    for dir in listDir:
        subDir = path+'/'+dir+'/'
        # 获取文件名
        files = os.listdir(subDir)

        haveFolder = False

        # for jpg in files:
        #     if(re.match('Folder\.[a-zA-Z]+', jpg)):
        #         os.remove(subDir+jpg)

        # 循环查找2次，先确认
        for jpg in files:
            if(re.match('Folder.[a-zA-Z]+', jpg)):
                haveFolder = True
                print('\033[1;31;40m%s文件夹下已经有封面文件了...\033[0m' % (subDir))
                break

        # 没有封面时则创建，防止重复创建封面文件
        if(haveFolder == False):
            for jpg in files:
                # 找到第一张图片文件
                if(re.match('\w+\.(?:[jp][pn]g|webp)', jpg, re.I)):
                    firstImg = subDir+jpg
                    # 获取cover后缀
                    coverImg = subDir+'Folder.'+jpg.split('.')[-1]

                    with open(firstImg, 'rb+') as oFp, open(coverImg, 'wb+') as nFp:
                        imgData = oFp.read(-1)
                        # 复制文件
                        nFp.write(imgData)

                    break

        # saving to destination
        if(not isDupDir(dir, destDir)):
            shutil.move(subDir, destDir)
            print('\033[1;32;40m已保存：<%s>\033[0m' % (dir))
        else:
            print(
                '\033[1;31;40m\n********************\n警告！此文件夹已存在：<%s>\n********************\n\033[0m' % (dir))
            haveDup = True
    if not haveDup:
        removeTree()


def isDupDir(src, dest):
    dirs = os.listdir(dest)

    for dir in dirs:
        if(src == dir):
            return True

    return False


def removeTree():
    shutil.rmtree(basePath)
    print('\033[1;32;40m清理完毕！！！\033[0m')


if __name__ == "__main__":
    main()
