"""
@File       :   spider_video.py
@Time       :   2020/8/19 13:17
@Author     :   Wang
@Version    :   1.0
@Description:   爬虫实战-爬取OK资源网视频
"""
import requests
from bs4 import BeautifulSoup
import sys


SERVER = "http://www.jisudhw.com"
KEYWORD = "越狱"


def search():
    """
    发起搜索请求
    :return: 所需搜索结果URL
    """
    url = SERVER + "/index.php"
    params = {
        "m": "vod-search"
    }
    data = {
        "wd": KEYWORD,
        "submit": "search"
    }
    resp = requests.post(url=url, params=params, data=data, timeout=10)
    soup = BeautifulSoup(resp.text, "lxml")
    results = soup.find("div", class_="xing_vb").find_all("a")

    if len(results) == 0:
        print(f"没有搜索到关于{KEYWORD}的搜索结果")
        sys.exit()

    print(f"共有{len(results)}条关于{KEYWORD}的搜索结果\n")
    for num, result in enumerate(results):
        print(f"{num+1}----->资源名:{result.string}\tURL:{SERVER + result.get('href')}")

    while True:
        choice = int(input("\n请输入需要的搜索结果(按0退出):"))
        if choice == 0:
            print("再见")
            sys.exit()
        if choice in range(1, len(results)+1):
            return SERVER + results[choice - 1].get("href")


def parse_url(url):
    """
    进入搜索结果URL
    :param url: 搜索结果URL
    :return: 所需单集视频URL
    """
    resp = requests.get(url=url, timeout=10)
    soup = BeautifulSoup(resp.text, "lxml")
    results = [a for a in soup.find_all("input") if "m3u8" in a.get("value")]

    for num, inp in enumerate(results):
        print(f"第{num + 1}集链接:\t{inp.get('value')}")

    while True:
        choice = int(input("\n请输入需要的搜索结果(按0退出):"))
        if choice == 0:
            print("再见")
            sys.exit()
        if choice in range(1, len(results)+1):
            return results[choice - 1].get("value")


def download(url):
    """
    下载单集视频
    :param url: 单集视频URL(m3u8格式需要特定软件FFmpeg解析)
    :return: 无
    """
    resp = requests.get(url=url, timeout=10)

    if resp.status_code == 200:
        print("开始下载")
        with open("E:\\Python Files\\Spider_files\\video\\aaa.m3u8", "wb") as fd:
            fd.write(resp.content)
        print("下载完成")
    else:
        resp.raise_for_status()


if __name__ == "__main__":
    download(parse_url(search()))
