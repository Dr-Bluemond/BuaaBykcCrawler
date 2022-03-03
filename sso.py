# -*- coding: utf-8 -*-
# SSO统一认证登录接口
import logging

import requests

import patterns

ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) ' \
     'Chrome/86.0.4240.75 Safari/537.36'


class SsoApi:

    def __init__(self, session: requests.Session, username, password):
        self._session = session
        self._username = username
        self._password = password
        self._session.headers['User-Agent'] = ua
        self._url = ''

    def _get_execution(self):
        resp = self._session.get(self._url)
        result = patterns.execution.search(resp.text)
        assert result, 'unexpected behavior: execution code not retrieved'
        return result.group(1)

    def _get_login_form(self):
        return {
            'username': self._username,
            'password': self._password,
            'submit': '登录',
            'type': 'username_password',
            'execution': self._get_execution(),
            '_eventId': 'submit',
        }

    def login_sso(self, url):
        """
        北航统一认证接口
        :param url: 不同网站向sso发送自己的域名，此时sso即了解是那个网站和应该返回何种token
        :return: token的返回形式为一个带有ticket的url，一般访问这个url即可在cookies中或者storages中储存凭证
        不同的网站有不同的处理形式
        """
        self._url = url
        self._session.cookies.clear()
        resp = self._session.post('https://sso.buaa.edu.cn/login', data=self._get_login_form(), allow_redirects=False)
        assert resp.status_code == 302, 'maybe your username or password is invalid'
        location = resp.headers['Location']
        logging.info('location: ' + location)
        return location


def test():
    from config import config
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
    session = requests.session()
    sso = SsoApi(session, config.username, config.password)
    location = sso.login_sso('http://jwxt.buaa.edu.cn:8080/ieas2.1/welcome?falg=1')
    print(location)


if __name__ == '__main__':
    test()
