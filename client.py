import binascii
import json
import time
from typing import Optional

import requests

import patterns
from config import root, ua
from exceptions import ApiError, LoginError, AlreadyChosen, FailedToChoose, FailedToDelChosen
from sso import SsoApi
from crypto import *
from pprint import pprint


class Client:
    def __init__(self, config):
        self.config = config
        self.session: Optional[requests.Session] = None
        self.token: Optional[str] = None

    def soft_login(self):
        if self.config.token:
            self.token = self.config.token
            if self.session is None:
                self.session = requests.Session()
            try:
                result = self.get_user_profile()
                if result['employeeId'] == self.config.username:
                    print("soft login success")
                    return True
            except Exception:
                pass
        return self.login()

    def login(self):
        if self.session is None:
            self.session = requests.Session()
        url = root + "/casLogin"
        ticket_url = SsoApi(self.session, self.config.username, self.config.password).login_sso(url)
        resp = self.session.get(ticket_url, allow_redirects=False)
        url1 = resp.headers['Location']
        resp = self.session.get(url1, allow_redirects=False)
        url2 = resp.headers['Location']
        self.token = patterns.token.search(url2).group(1)
        if self.token:
            print('login success')
        self.config.token = self.token

    def logout(self):
        self.session.close()
        self.session = None

    def _call_api(self, api_name: str, data: dict):
        if self.session is None:
            raise LoginError("you must call `login` or `soft_login` before calling other apis")
        url = root + '/' + api_name
        data_str = json.dumps(data).encode()
        aes_key = generate_aes_key()
        ak = rsa_encrypt(aes_key)
        data_sign = sign(data_str)
        sk = rsa_encrypt(data_sign)
        ts = str(int(time.time() * 1000))

        data_encrypted = base64.b64encode(aes_encrypt(data_str, aes_key))
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
        if resp.status_code != 200:
            raise ApiError(f"server panics with http status code: {resp.status_code}")
        try:
            message_decode_b64 = base64.b64decode(text)
        except binascii.Error:
            raise ApiError(f"unable to parse response: {text}")

        try:
            api_resp = json.loads(aes_decrypt(message_decode_b64, aes_key))
        except ValueError:
            raise LoginError("failed to decrypt response, it's usually because your login has expired")

        if api_resp['status'] != '0':
            if api_resp['errmsg'].find('已报名过该课程，请不要重复报名') >= 0:
                raise AlreadyChosen
            if api_resp['errmsg'].find('选课失败，该课程不可选择') >= 0:
                raise FailedToChoose
            if api_resp['errmsg'].find('退选失败，未找到退选课程或已超过退选时间') >= 0:
                raise FailedToDelChosen
            print(api_resp)
            raise ApiError(f"server returns a non zero api status code: {api_resp['status']}")
        return api_resp['data']

    def get_user_profile(self):
        result = self._call_api('getUserProfile', {})
        return result

    def query_selectable_course(self):
        result = self._call_api('querySelectableCourse', {})
        pprint(result)
        return result

    def query_chosen_course(self):
        result = self._call_api('queryChosenCourse', {})
        pprint(result)
        return result

    def query_fore_course(self):
        result = self._call_api('queryForeCourse', {})
        pprint(result)
        return result

    def chose_course(self, course_id: int):
        result = self._call_api('choseCourse', {'courseId': course_id})
        return result

    def del_chosen_course(self, course_id: int):
        result = self._call_api('delChosenCourse', {'id': course_id})
        return result
