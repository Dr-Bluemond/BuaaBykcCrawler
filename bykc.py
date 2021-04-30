# -*- coding: utf-8 -*-
import requests
import time
from config import config
import bykc_login

ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) ' \
     'Chrome/86.0.4240.75 Safari/537.36'


class Robot:

    def query_selectable(self):
        print("querying selectable. {time: %s}" % time.asctime())
        url = 'http://bykc.buaa.edu.cn/sscv/querySelectableCourse'
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'User-Agent': ua,
            'auth_token': config.token
        }

        resp = requests.post(url, data='{}', headers=headers)
        j = resp.json()
        if j['errmsg'] == '您的会话已失效,请重新登录后再试,谢谢!':
            print("博雅登录失效,尝试重新登录中. {time: %s}" % time.asctime())
            try:
                robot = bykc_login.Robot()
                token = robot.login_sso()
                config.token = token
            except:
                print("博雅未能重新登录. {time: %s}" % time.asctime())
                return
            print("博雅已重新登录. {time: %s}" % time.asctime())
            self.query_selectable()
            return
        if 'data' not in j:
            print("未知错误导致博雅课程查询失败，网页存入unknown_error.html. {time: %s}" % time.asctime())
            with open('unknown_error.html', 'w') as f:
                f.write(str(resp.json()))
            return

        print('query succeeded')
        print(j)

    def chose(self, id):
        url = 'http://bykc.buaa.edu.cn/sscv/choseCourse'
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'User-Agent': ua,
            'auth_token': config.token
        }

        resp = requests.post(url, data='{"courseId":%d}' % id, headers=headers)
        print(resp.json())

    def del_chosen(self, id):
        url = 'http://bykc.buaa.edu.cn/sscv/delChosenCourse'
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'User-Agent': ua,
            'auth_token': config.token
        }

        resp = requests.post(url, data='{"id":%d} ' % id, headers=headers)
        print(resp.json())


if __name__ == '__main__':
    r = Robot()
    r.query_selectable()
