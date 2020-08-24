"""
@File       :   spider_novel.py
@Time       :   2020/8/17 14:19
@Author     :   Wang
@Version    :   2.0
@Description:   爬虫实战-爬取新笔趣阁小说
"""
import requests
from bs4 import BeautifulSoup
import sys
import tqdm
import re


SERVER_URL = "https://www.xsbiquge.com/"
KEYWORD = "龙王"
TITLE_LIST = []
URL_LIST = []
CHAPTER_SUM = 0
TARGET_PATH = "E://Python Files//Spider_files//novel//"


def prepare_env(url):
    resp = requests.get(url=url, timeout=10)
    # 修改编码
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")
    menu = soup.find("div", id="list")
    # 遍历目录获得章节名和链接
    for a in menu.find_all("a"):
        TITLE_LIST.append(a.string)
        URL_LIST.append(a.get('href'))
    global CHAPTER_SUM
    CHAPTER_SUM = len(TITLE_LIST)
    if CHAPTER_SUM == 0:
        print("待查看的小说不存在")
        sys.exit()


def search():
    """
    搜索小说
    :return: 小说URL
    """
    params = {
        "keyword": KEYWORD
    }
    resp = requests.get(url=SERVER_URL+"search.php", params=params)
    soup = BeautifulSoup(resp.text, "lxml")
    result_list = [a for a in soup.find("div", class_="result-list").find_all("a") if a.get("cpos") == "title"]
    if len(result_list) == 0:
        print(f"没有关于{KEYWORD}的小说")
        sys.exit()
    print("搜索结果:\n")
    for num, result in enumerate(result_list):
        print(f"{num + 1}----->\t标题:{result.find('span').string}\t\t\tURL:{result.get('href')}")
    num = int(input("\n请输入所需小说编号:"))
    if num in range(1, len(result_list)+1):
        return result_list[num - 1].get("href")
    else:
        print("输入编号有误")
        sys.exit()


def get_chapter():
    """
    获取待操作章节
    :return: 章节号
    """
    chapter = input(f"小说共有{CHAPTER_SUM}章请输入要查看/下载的章节:")
    try:
        chapter = int(chapter)
    except ValueError:
        print("请输入数字章节")
        sys.exit()
    else:
        if chapter not in range(1, CHAPTER_SUM + 1):
            print(f"请输入有效的数字章节(1 - {CHAPTER_SUM})")
            sys.exit()
        return chapter


def get_chapter_range():
    """
    获取待操作章节区间
    :return: 章节区间
    """
    start = input(f"小说共有{CHAPTER_SUM}章请输入要下载的章节区间(起始):")
    end = input(f"小说共有{CHAPTER_SUM}章请输入要下载的章节区间(终点):")
    try:
        start = int(start)
        end = int(end)
    except ValueError:
        print("请输入数字章节")
        sys.exit()
    else:
        if start > end:
            print("请输入合法的区间(终点 >= 起始)")
        elif start in range(1, CHAPTER_SUM + 1) and end in range(1, CHAPTER_SUM + 1):
            return range(start - 1, end)
        else:
            print(f"请输入有效的数字章节(1 - {CHAPTER_SUM})")
        sys.exit()


def show(chapter):
    """
    查看单章节内容
    :param chapter: 章节号
    :return: 无
    """
    url = SERVER_URL + URL_LIST[chapter-1]
    # get请求小说URL
    resp = requests.get(url=url, timeout=10)
    resp.encoding = "utf-8"
    # 不加处理的HTML响应代码
    html = resp.text
    # 使用BeautifulSoup格式化处理HTML响应代码
    soup = BeautifulSoup(html, "lxml")  # lxml为第三方解析库,也需要pip安装,否则使用html.parser
    # 按条件查找标签
    content = soup.find("div", id="content")
    # 输出标签内容
    print(TITLE_LIST[chapter-1], end="\n\n")
    print(content.get_text().strip().replace("\xa0"*4, "\n"))


def download(chapter):
    """
    下载单章节内容
    :param chapter: 章节号
    :return: 无
    """
    url = SERVER_URL + URL_LIST[chapter - 1]
    # get请求小说URL
    resp = requests.get(url=url, timeout=10)
    resp.encoding = "utf-8"
    # 不加处理的HTML响应代码
    html = resp.text
    # 使用BeautifulSoup格式化处理HTML响应代码
    soup = BeautifulSoup(html, "lxml")  # lxml为第三方解析库,也需要pip安装,否则使用html.parser
    # 按条件查找标签
    content = soup.find("div", id="content")
    # 下载标签内容
    title = TITLE_LIST[chapter - 1]
    target = TARGET_PATH + title + ".txt"
    with open(target, "wb") as fd:
        fd.write(content.get_text().strip().replace("\xa0"*4, "\n").encode())


def batch_download(chapter_range):
    """
    批量下载章节
    :param chapter_range: 章节区间
    :return: 无
    """
    length = len(chapter_range)
    print("待下载章节区间:", chapter_range)
    print("待下载的章节数:", length)
    count = 1

    # for i in chapter_range:
    #     print(f"\r{'=' * count} {round(count*(100/length), 2)}%", end=" ")
    #     download(i + 1)
    #     count += 1

    for i in tqdm.tqdm(chapter_range):
        download(i + 1)
        count += 1

    print("\n" + "下载完成, 下载路径", TARGET_PATH)


if __name__ == "__main__":
    prepare_env(search())
    # show(get_chapter())
    # download(get_chapter())
    batch_download(get_chapter_range())
