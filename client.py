import json
import time
from typing import Optional

import aiohttp

import patterns
from config import root, ua
from sso import SsoApi
from crypto import *
from pprint import pprint


class Client:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session: Optional[aiohttp.ClientSession] = None
        self.token: Optional[str] = None

    async def login(self):
        self.session = aiohttp.ClientSession()
        url = root + "/casLogin"
        ticket_url = await SsoApi(self.session, self.username, self.password).login_sso(url)
        async with self.session.get(ticket_url, allow_redirects=False) as resp:
            url1 = resp.headers['Location']
        async with self.session.get(url1, allow_redirects=False) as resp:
            url2 = resp.headers['Location']
        self.token = patterns.token.search(url2).group(1)

    async def logout(self):
        if self.session is not None and not self.session.closed:
            await self.session.close()

    async def _call_api(self, api_name: str, data: dict):
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

        async with self.session.post(url, data=data_encrypted, headers=headers) as resp:
            text = await resp.read()
        api_resp = json.loads(aes_decrypt(base64.b64decode(text), aes_key))
        return api_resp

    async def query_selectable_course(self):
        result = await self._call_api('querySelectableCourse', {})
        pprint(result)

    async def query_chosen_course(self):
        result = await self._call_api('queryChosenCourse', {})
        pprint(result)

    async def query_fore_course(self):
        result = await self._call_api('queryForeCourse', {})
        pprint(result)

    async def chose_course(self, course_id: int):
        result = await self._call_api('choseCourse', {'courseId': course_id})
        pprint(result)

    async def del_chosen_course(self, course_id: int):
        result = await self._call_api('delChosenCourse', {'id': course_id})
        pprint(result)


