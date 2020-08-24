"""
@File       :   spider_comic.py
@Time       :   2020/8/18 14:10
@Author     :   Wang
@Version    :   1.0
@Description:   爬虫实战-爬取动漫之家漫画:《妖神记》
"""
import requests
from bs4 import BeautifulSoup
import re
import sys
import os


SERVER_URL = "https://images.dmzj.com/img/chapterpic"
MENU_URL = "https://www.dmzj.com/info/yaoshenji.html"
LOCAL_PATH = "E:\\Python Files\\Spider_files\\comic"
TITLE_LIST = []
URL_LIST = []


def prepare_env():
    """
    环境准备
    :return: 无
    """
    # 获取章节目录页面
    resp = requests.get(url=MENU_URL, timeout=10)
    # 解析HTML
    soup = BeautifulSoup(resp.text, "lxml")
    # 寻找指定标签构造章节名和URL列表
    menu = soup.find("ul", class_="list_con_li autoHeight")
    for chapter in menu.find_all("a"):
        TITLE_LIST.insert(0, chapter.get('title'))
        URL_LIST.insert(0, chapter.get('href'))
    # 章节数有误退出程序
    if len(TITLE_LIST) == 0:
        print("待下载的漫画不存在")
        sys.exit()


def get_chapter():
    """
    获取待操作章节
    :return: 章节编号
    """
    chapter = input(f"漫画共有{len(TITLE_LIST)}章, 请输入要下载的章节:")
    try:
        chapter = int(chapter)
    except ValueError:
        print("请输入数字章节")
        sys.exit()
    else:
        if chapter not in range(1, len(TITLE_LIST) + 1):
            print(f"请输入有效的数字章节(1 - {len(TITLE_LIST)})")
            sys.exit()
        return chapter


def download_chapter(chapter):
    """
    下载单一章节
    :param chapter: 章节编号
    :return: 无
    """
    # 获取单章节漫画页面
    resp = requests.get(url=URL_LIST[chapter - 1], timeout=10)
    # 解析HTML
    soup = BeautifulSoup(resp.text, "lxml")
    # 查找JS脚本获取单张图片URL
    script = soup.find_all("script")
    left = re.findall(r"\|(\d{4})\|", str(script[0]))
    middle = re.findall(r"\|(\d{5})\|", str(script[0]))
    right = re.findall(r"\d{13,14}", str(script[0]))
    url_list = []
    for a in right:
        url_list.append(SERVER_URL + "/" + left[0] + "/" + middle[0] + "/" + a + ".jpg")
    # 保持图片顺序
    url_list = sorted(url_list)
    # 开始下载
    title = re.findall(r"(.*) \d{4}-\d{2}-\d{2}$", TITLE_LIST[chapter - 1])[0]
    print("待下载章节:", title)
    print("待下载章节图片数:", len(url_list))
    count = 1
    for a in url_list:
        print(f"\r{'=' * count} {round(count * (100 / len(url_list)), 2)}%", end=" ")
        download_pic(a, title + "_" + str(count), os.path.join(LOCAL_PATH, title))
        count += 1
    print("\n" + "下载完成")


def download_pic(pic_url, pic_name, target_path):
    """
    下载单张图片
    :param pic_url: 网页源图片地址
    :param pic_name: 本地保存图片名称
    :param target_path: 本地保存图片目录
    :return: 无
    """
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    elif not os.path.isdir(target_path):
        print("本地保存图片目录格式有误")
        sys.exit()
    # 请求头加入Referer解决目标网址防盗链技术
    headers = {
        'Referer': MENU_URL
    }
    # 获取单张图片资源页面
    resp = requests.get(url=pic_url, headers=headers, timeout=10)
    if resp.status_code == 200:
        # 下载至本地
        with open(os.path.join(target_path, pic_name + ".jpg"), "wb") as fd:
            fd.write(resp.content)
    else:
        resp.raise_for_status()


if __name__ == "__main__":
    prepare_env()
    download_chapter(get_chapter())
