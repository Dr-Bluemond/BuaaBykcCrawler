# -*- coding: utf-8 -*-
import json
import os


class Config:
    path = 'config.json'
    __slots__ = '_token', '_username', '_password'

    def __init__(self):
        self._token = ''
        self._username = ''
        self._password = ''
        if not os.path.exists(self.path):
            self._save()
            print("please fill config.json with username and password")
            exit(0)
        self._load()

    def _save(self):
        c = {
            'token': self._token,
            'username': self._username,
            'password': self._password
        }
        with open(self.path, 'w') as f:
            json.dump(c, f, indent=4)

    def _load(self):
        with open(self.path, 'r') as f:
            j = json.load(f)
            self._token = j['token']
            self._username = j['username']
            self._password = j['password']

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value
        self._save()

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


config = Config()
if __name__ == '__main__':
    print(config.password)
