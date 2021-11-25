# -*- coding: utf-8 -*-
import requests
import time
from pprint import pprint
from config import config
import bykc_login

ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) ' \
     'Chrome/86.0.4240.75 Safari/537.36'


class Robot:

    def login(self):
        robot = bykc_login.Robot()
        token = robot.login_sso()
        config.token = token
        print("登录成功")

    def query_selectable(self):
        # print("querying selectable. {time: %s}" % time.asctime())
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
                self.login()
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

        return j

    def query_chosen_course(self):
        url = 'http://bykc.buaa.edu.cn/sscv/queryChosenCourse'
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'User-Agent': ua,
            'auth_token': config.token
        }

        resp = requests.post(url, data='{}', headers=headers)
        return resp.json()

    def chose(self, id):
        url = 'http://bykc.buaa.edu.cn/sscv/choseCourse'
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'User-Agent': ua,
            'auth_token': config.token
        }

        resp = requests.post(url, data='{"courseId":%d}' % id, headers=headers)
        return resp.json()

    def del_chosen(self, id):
        url = 'http://bykc.buaa.edu.cn/sscv/delChosenCourse'
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'User-Agent': ua,
            'auth_token': config.token
        }

        resp = requests.post(url, data='{"id":%d} ' % id, headers=headers)
        return resp.json()


class Terminal:
    help_info = """
可用命令: 
query_selectable    (or qs)    查看可选课程
query_chosen_course (or qc)    查看已选课程
chose id            (or c id)  选课
del_chosen id       (or dc id) 退课

# 其中id的值可以通过前两个命令查询得到
    """

    def __init__(self):
        self.switch_table = {
            'query_selectable': self.query_selectable,
            'qs': self.query_selectable,
            'query_chosen_courseq': self.query_chosen_course,
            'qc': self.query_chosen_course,
            'chose': self.chose,
            'c': self.chose,
            'del_chosen': self.del_chosen,
            'dc': self.del_chosen,
        }

    def run(self):
        self.r = Robot()
        print("正在登录")
        self.r.login()
        print(self.help_info)
        while True:
            command = input("> ")
            args = command.split()
            if args[0] in self.switch_table:
                self.switch_table[args[0]](args[1:])
            elif args[0] in {'quit', 'exit', ''}:
                return
            else:
                print("指令不存在")

    def query_selectable(self, args):
        j = self.r.query_selectable()
        print("缺少信息，暂时不能转换为可读格式，原数据：")
        pprint(j)

    def query_chosen_course(self, args):
        j = self.r.query_chosen_course()
        assert j['errmsg'] == '请求成功' and j['status'] == '0'
        course_list = j['data']['courseList']
        for course in course_list:
            course_info = course['courseInfo']
            checkin = "通过" if course['checkin'] == 1 else "待录入或缺席"
            print(f"id: {course_info['id']}, 考勤: {checkin}, 名称: {course_info['courseName']}")

    def chose(self, args):
        try:
            i = int(args[0])
            j = self.r.chose(i)
            print("结果：")
            pprint(j)
        except (ValueError, IndexError):
            print("请输入数字的id")

    def del_chosen(self, args):
        try:
            i = int(args[0])
            j = self.r.del_chosen(i)
            print("结果：")
            pprint(j)
        except (ValueError, IndexError):
            print("请输入数字的id")


if __name__ == '__main__':
    Terminal().run()
