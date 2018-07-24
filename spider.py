#encoding: utf-8
'''
author: sixseven
date: 2018-07-24
topic: 工商局加速乐反爬
contact: 2557692481@qq.com
desc: 
'''
import re
import execjs
import requests
from copy import deepcopy

session = requests.Session()
headers = {
    'Host': 'www.gsxt.gov.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
}
proxies = {
    'http': '127.0.0.1:3128'
}

def main(cookies={}):
    index_url = 'http://www.gsxt.gov.cn/index.html'
    index_headers = deepcopy(headers)
    if cookies:
        index_req = session.get(index_url, headers=index_headers, proxies=proxies, cookies=cookies)
    else:
        index_req = session.get(index_url, headers=index_headers, proxies=proxies)
    index_req.encoding = 'utf-8'
    if index_req.status_code == 521:
        print('第一次访问，状态码为521，获取动态js生成cookie')

        # 获取和替换动态js，生成cookie在此访问
        js_match = re.findall(r'<script>(.*?)</script>', index_req.text)
        if js_match:
            js = js_match[0]
            key_js = re.findall(r'eval\((.*?)\);', js)[0]
            replace = 'var cookie_js={};'.format(key_js)
            js = re.sub(r'eval\(.*?\);', replace, js)
            js = js.replace(
                'break', 'if(cookie_js.indexOf("document.cookie=\'__jsl_clearance=")!=-1){cookie_js = cookie_js.match(/document.cookie=(.*?)\+\';Expires/i)[1];break}')
            js = 'var cookie_js, window={};' + js + 'function get_cookie(){return eval(cookie_js);}'
            js = js.replace('', '')

            ctx = execjs.compile(js)
            cookie_value = ctx.call("get_cookie")
            cookies = {
                cookie_value.split('=')[0]: cookie_value.split('=')[1]
            }
            main(cookies)

        else:
            print('获取js失败')
            print(index_req.text)

    else:
        print('访问首页成功')
        print(index_req.text)


if __name__ == '__main__':
    main()
