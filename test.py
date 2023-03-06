import base64
import json
import unittest

from client import Client
from crypto import *


class TestCrypto(unittest.TestCase):

    def test_aes_encrypt(self):
        aes_key = b"WdpzcfRTJ8PJpmyn"
        request = aes_encrypt(b"{}", aes_key)
        self.assertEqual(base64.b64encode(request), b'DwQdpyQ5I9u/4O+E8VS2aQ==')

    def test_aes_decrypt(self):
        aes_key = b"WdpzcfRTJ8PJpmyn"
        raw_response = b"9SZmhpsx93bPTr1TUbya0Io5cjazQBYh+U26Ow7D+2Wxu8asLBHP1bwDL7Z8r0w3Dyc9YF2i8grJi+KQCl/KTA=="
        response = aes_decrypt(base64.b64decode(raw_response), aes_key)
        resp_obj = json.loads(response)
        self.assertEqual(resp_obj['status'], '0')
        self.assertEqual(resp_obj['data'], [])

    def test_sha1_sign(self):
        _sign = sign(b"{}")
        self.assertEqual(_sign, b'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f')


class TestApiCall(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls) -> None:
        from config import config
        cls.client = Client(config)
        cls.client.login()

    def test_get_user_profile(self):
        rtv = self.client.get_user_profile()
        self.assertGreater(rtv['id'], 0)

    def test_query_student_semester_course_by_page(self):
        rtv = self.client.query_student_semester_course_by_page(1, 10)
        self.assertEqual(rtv['size'], 10)


if __name__ == '__main__':
    unittest.main()
