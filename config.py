# -*- coding: utf-8 -*-
import json
import os


class Config:
    path = 'config.json'
    __slots__ = '_username', '_password', '_token'

    def __init__(self):
        self._username = ''
        self._password = ''
        self._token = ''
        if not os.path.exists(self.path):
            self._save()
            print("please fill config.json with username and password")
            exit(0)
        self._load()
        if not self._username or not self._password:
            print("please fill config.json with username and password")
            exit(0)

    def _save(self):
        c = {
            'username': self._username,
            'password': self._password,
            'token': self._token,
        }
        with open(self.path, 'w') as f:
            json.dump(c, f, indent=4)

    def _load(self):
        with open(self.path, 'r') as f:
            j = json.load(f)
            self._username = j['username']
            self._password = j['password']
            self._token = j['token']

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value
        self._save()

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value
        self._save()

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value
        self._save()


config = Config()

root = "https://bykc.buaa.edu.cn/sscv"

ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36"
