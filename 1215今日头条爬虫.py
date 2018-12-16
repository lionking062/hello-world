import json
from urllib.parse import urlencode

import os
import pymongo
import re
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import requests
from config1215 import *
from hashlib import md5
from multiprocessing import Pool


# client = pymongo.MongoClient(MONGO_URL, connect=False)
# db = client[MONGO_DB]

def get_page_index(offset, keyword):     #1 获取索引页信息
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': 1,
        'from': 'search_tab',
        'pd': 'synthesis'
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        responce = requests.get(url)
        if responce.status_code == 200:
            return responce.text
        return '失败1'
    except RequestException:
        print('请求索引页失败')
        return '失败2'

def parse_page_index(html):         #2  解析索引页信息
    data = json.loads(html)
    print(data, '\n')
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')    #  获取索引页 article_url


def get_page_detail(url):          #5   获取详情页信息
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
        }
        responce = requests.get(url, headers=headers)
        # print(responce.text)
        if responce.status_code == 200:
            return responce.text
        return '失败3'
    except RequestException:
        print('请求详情页失败', url)
        return '失败4'


def parse_page_detail(html, url):       #6    解析详情页信息
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')
    print(title)
    images_pattern = re.compile('gallery: JSON.parse\("(.*?)"\)', re.S)
    result = re.search(images_pattern, html)
    if result:
        data = json.loads(result.group(1).replace('\\', ''))
        print(result.group(1))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]    #获取详情页中图片链接
            for image in images:
                download_image(image)
            return {
                'title': title,
                'url': url,
                'images':images
            }

# def save_to_mongo(result):       #7  保存到数据库mongodb
#     if db[MONGO_TABLE].insert(result):
#         print('存储到mongodb成功', result)
#         return True
#     return False


def download_image(url):       #8  下载图片
    print('正在下载', url)
    try:
        responce = requests.get(url)
        if responce.status_code == 200:
            save_image(responce.content)
        return '失败5'
    except RequestException:
        print('请求图片失败')
        return '失败6'

def save_image(content):    #9  保存图片
    file_path = '{0}/{1}/{2}.{3}'.format(os.getcwd(),'今日头条图片测试1216', md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def main(offset):         #3   main函数
    keyword = '街拍'
    html = get_page_index(offset, keyword)         # 获取索引页信息
    for url in parse_page_index(html):         #  获取索引页 article_url后，循环
        if url:
            print(url)
            html = get_page_detail(url)       # 获取详情页信息
            if html:
                result = parse_page_detail(html, url)     #获取详情页中图片链接
                print(result)
                # if result:
                #     save_to_mongo(result)


if __name__ == '__main__':      #4   调用main函数
    # main(0)   #最简测试

    for i in range(5):     #for循环爬取
        offset = i*20
        main(offset)

    # pool = Pool()     #多线程爬取
    # pool.map(main, [i*20 for i in range(5)])
    # pool.close()
    # pool.join()




# pool = Pool()
#     groups = ([x * 20 for x in range(GROUP_START, GROUP_END + 1)])
#     pool.map(main, groups)
#     pool.close()
#     pool.join()


# pool = Pool()
#     pool.map(main, [i*10 for i in range(10)])



'''
http://toutiao.com/group/6324654046566416641/
[<title>街拍：紧身运动裤美女，身材没话说</title>]
None

http://toutiao.com/group/6601276460789400078/
[<title>街拍：重庆街头清爽美女时尚街拍</title>]
{\"count\":3,\"sub_images\":[{\"url\":\"http:\\/\\/p3.pstatp.com\\/origin\\/pgc-image\\/1536979381408c23812bc82\",\"width\":690,\"url_list\":[{\"url\":\"http:\\/\\/p3.pstatp.com\\/origin\\/pgc-image\\/1536979381408c23812bc82\"},{\"url\":\"http:\\/\\/pb9.pstatp.com\\/origin\\/pgc-image\\/1536979381408c23812bc82\"},{\"url\":\"http:\\/\\/pb1.pstatp.com\\/origin\\/pgc-image\\/1536979381408c23812bc82\"}],\"uri\":\"origin\\/pgc-image\\/1536979381408c23812bc82\",\"height\":1087},{\"url\":\"http:\\/\\/p99.pstatp.com\\/origin\\/pgc-image\\/1536979381443e3c07b2df1\",\"width\":690,\"url_list\":[{\"url\":\"http:\\/\\/p99.pstatp.com\\/origin\\/pgc-image\\/1536979381443e3c07b2df1\"},{\"url\":\"http:\\/\\/pb3.pstatp.com\\/origin\\/pgc-image\\/1536979381443e3c07b2df1\"},{\"url\":\"http:\\/\\/pb1.pstatp.com\\/origin\\/pgc-image\\/1536979381443e3c07b2df1\"}],\"uri\":\"origin\\/pgc-image\\/1536979381443e3c07b2df1\",\"height\":1087},{\"url\":\"http:\\/\\/p9.pstatp.com\\/origin\\/pgc-image\\/15369793814965594433f87\",\"width\":690,\"url_list\":[{\"url\":\"http:\\/\\/p9.pstatp.com\\/origin\\/pgc-image\\/15369793814965594433f87\"},{\"url\":\"http:\\/\\/pb1.pstatp.com\\/origin\\/pgc-image\\/15369793814965594433f87\"},{\"url\":\"http:\\/\\/pb3.pstatp.com\\/origin\\/pgc-image\\/15369793814965594433f87\"}],\"uri\":\"origin\\/pgc-image\\/15369793814965594433f87\",\"height\":1090}],\"max_img_width\":690,\"labels\":[\"\\u7f8e\\u5973\",\"\\u65f6\\u5c1a\",\"\\u6444\\u5f71\"],\"sub_abstracts\":[\"\\u8857\\u62cd\\uff1a\\u91cd\\u5e86\\u8857\\u5934\\u6e05\\u723d\\u7f8e\\u5973\\u65f6\\u5c1a\\u8857\\u62cd\",\" \",\" \"],\"sub_titles\":[\"\\u8857\\u62cd\\uff1a\\u91cd\\u5e86\\u8857\\u5934\\u6e05\\u723d\\u7f8e\\u5973\\u65f6\\u5c1a\\u8857\\u62cd\",\"\\u8857\\u62cd\\uff1a\\u91cd\\u5e86\\u8857\\u5934\\u6e05\\u723d\\u7f8e\\u5973\\u65f6\\u5c1a\\u8857\\u62cd\",\"\\u8857\\u62cd\\uff1a\\u91cd\\u5e86\\u8857\\u5934\\u6e05\\u723d\\u7f8e\\u5973\\u65f6\\u5c1a\\u8857\\u62cd\"]}
{'title': [<title>街拍：重庆街头清爽美女时尚街拍</title>], 'url': 'http://toutiao.com/group/6601276460789400078/', 'images': ['http://p3.pstatp.com/origin/pgc-image/1536979381408c23812bc82', 'http://p99.pstatp.com/origin/pgc-image/1536979381443e3c07b2df1', 'http://p9.pstatp.com/origin/pgc-image/15369793814965594433f87']}
'''