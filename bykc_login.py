# -*- coding: utf-8 -*-
import requests
import re

from config import config

ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) ' \
     'Chrome/86.0.4240.75 Safari/537.36'


class Robot:
    def __init__(self):
        self.session = requests.session()
        self.session.headers['User-Agent'] = ua

    def get_login_form(self):
        return {
            "username": config.username,
            "password": config.password,
            "submit": "登录",
            "type": "username_password",
            "execution": self.get_execution(),
            "_eventId": "submit",
        }

    def get_execution(self):
        resp = self.session.get('https://sso.buaa.edu.cn/login?TARGET=http%3A%2F%2Fbykc.buaa.edu.cn%2Fsscv%2FcasLogin')
        pattern = '<input name="execution" value="(.*?)"/>'
        result = re.search(pattern, resp.content.decode())
        if not result:
            raise Exception
        return result.group(1)

    def login_sso(self):
        resp = self.session.post(
            'https://sso.buaa.edu.cn/login?TARGET=http%3A%2F%2Fbykc.buaa.edu.cn%2Fsscv%2FcasLogin',
            data=self.get_login_form(), allow_redirects=False)
        if resp.status_code != 302:
            raise Exception
        location1 = resp.headers['Location']
        resp1 = self.session.get(location1, allow_redirects=False)
        if resp1.status_code != 302:
            raise Exception
        location2 = resp1.headers['Location']
        resp2 = self.session.get(location2, allow_redirects=False)
        location3 = resp2.headers['Location']
        result = re.search('token=(.*)', location3)
        if not result:
            raise Exception
        token = result.group(1)
        if not token:
            raise Exception
        return token


if __name__ == '__main__':
    r = Robot()
    print(r.login_sso())
