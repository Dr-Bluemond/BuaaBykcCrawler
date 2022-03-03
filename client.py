import json
import time
from typing import Optional

import requests

import patterns
from config import root, ua
from sso import SsoApi
from crypto import *
from pprint import pprint


class Client:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session: Optional[requests.Session] = None
        self.token: Optional[str] = None

    def login(self):
        self.session = requests.Session()
        url = root + "/casLogin"
        ticket_url = SsoApi(self.session, self.username, self.password).login_sso(url)
        resp = self.session.get(ticket_url, allow_redirects=False)
        url1 = resp.headers['Location']
        resp = self.session.get(url1, allow_redirects=False)
        url2 = resp.headers['Location']
        self.token = patterns.token.search(url2).group(1)

    def logout(self):
        self.session.close()

    def _call_api(self, api_name: str, data: dict):
        url = root + '/' + api_name
        data_str = json.dumps(data).encode()
        aes_key = generate_aes_key()
        ak = rsa_encrypt(aes_key)
        data_sign = sign(data_str)
        sk = rsa_encrypt(data_sign)
        ts = str(int(time.time() * 1000))

        data_encrypted = aes_encrypt(data_str, aes_key)
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'User-Agent': ua,
            'auth_token': self.token,
            'ak': ak.decode(),
            'sk': sk.decode(),
            'ts': ts,
        }

        resp = self.session.post(url, data=data_encrypted, headers=headers)
        text = resp.content
        api_resp = json.loads(aes_decrypt(base64.b64decode(text), aes_key))
        return api_resp

    def query_selectable_course(self):
        result = self._call_api('querySelectableCourse', {})
        pprint(result)

    def query_chosen_course(self):
        result = self._call_api('queryChosenCourse', {})
        pprint(result)

    def query_fore_course(self):
        result = self._call_api('queryForeCourse', {})
        pprint(result)

    def chose_course(self, course_id: int):
        result = self._call_api('choseCourse', {'courseId': course_id})
        pprint(result)

    def del_chosen_course(self, course_id: int):
        result = self._call_api('delChosenCourse', {'id': course_id})
        pprint(result)


