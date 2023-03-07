import binascii
import datetime
import json
import time
import warnings
from typing import Optional, overload

import requests

import patterns
from config import root, ua, Config
from exceptions import ApiError, LoginError, AlreadyChosen, FailedToChoose, FailedToDelChosen
from sso import SsoApi
from crypto import *


class Client:
    def __init__(self, config: Config):
        self.config: Config = config
        self.session: Optional[requests.Session] = None
        self.token: Optional[str] = None

    def soft_login(self):
        """
        first try to login with token that is stored in config file, if failed, login with username and password
        """
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
        """
        login through sso
        """
        if self.session is None:
            self.session = requests.Session()
        url = root + "/casLogin"
        ticket_url = SsoApi(self.session, self.config.username, self.config.password).login_sso(url)
        url = ticket_url
        while True:
            resp = self.session.get(url, allow_redirects=False)  # manually redirect
            searching_token = patterns.token.search(url)
            if searching_token:
                self.token = searching_token.group(1)
                print('login success')
                self.config.token = self.token
                break
            elif resp.status_code in [301, 302]:
                url = resp.headers['Location']
                continue
            else:
                raise LoginError

    def logout(self):
        """
        clear session and logout
        """
        self.session.close()
        self.token = None
        self.session = None

    def _call_api(self, api_name: str, data: dict):
        """
        an intermediate method to call api which deals with crypto and auth
        :param api_name: could be found in `app.js`. To find this file, open the network tab in devtools, refresh the page
        :param data: could also be found in `app.js`
        :return: raw data returned by the api
        """
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
            'authtoken': self.token,
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
                raise AlreadyChosen("已报名过该课程，请不要重复报名")
            if api_resp['errmsg'].find('选课失败，该课程不可选择') >= 0:
                raise FailedToChoose('选课失败，该课程不可选择')
            if api_resp['errmsg'].find('报名失败，该课程人数已满！') >= 0:
                raise FailedToChoose("报名失败，该课程人数已满！")
            if api_resp['errmsg'].find('退选失败，未找到退选课程或已超过退选时间') >= 0:
                raise FailedToDelChosen("退选失败，未找到退选课程或已超过退选时间")
            print(api_resp)
            raise ApiError(f"server returns a non zero api status code: {api_resp['status']}")
        return api_resp['data']

    def get_user_profile(self):
        """
        get your profile
        :return: an object contains your profile
        """
        result = self._call_api('getUserProfile', {})
        return result

    def query_student_semester_course_by_page(self, page_number: int, page_size: int):
        """
        query all recent courses
        :param page_number: page number
        :param page_size: page size
        :return: an object contains a list of courses and a total count
        """
        result = self._call_api('queryStudentSemesterCourseByPage', {'pageNumber': page_number, 'pageSize': page_size})
        return result

    def query_fore_course(self):
        warnings.warn('this api is not officially supported by bykc system, \n'
                      'use query_student_semester_course_by_page instead', DeprecationWarning)
        result = self._call_api('queryForeCourse', {})
        return result

    def query_selectable_course(self):
        warnings.warn('this api is not officially supported by bykc system, \n'
                      'use query_student_semester_course_by_page instead', DeprecationWarning)
        result = self._call_api('querySelectableCourse', {})
        return result

    def get_all_config(self):
        """
        :return: all config contains campus, college, role, semester, term
        """
        result = self._call_api('getAllConfig', {})
        return result

    @overload
    def query_chosen_course(self):
        """
        :return: the chosen courses of current semester
        """
        ...

    @overload
    def query_chosen_course(self, semester_id: int):
        """
        :param semester_id: the semester id, could be obtained from `get_all_config`
        :return: the chosen courses of the semester
        """
        ...

    @overload
    def query_chosen_course(self, start_date: datetime.datetime, end_date: datetime.datetime):
        """
        :param start_date: the start date to query
        :param end_date: the end date to query
        :return: the chosen courses in the period
        """
        ...

    def query_chosen_course(self, arg0=None, arg1=None):  # get chosen courses in the specified time range
        if arg0 is None:
            all_config = self.get_all_config()
            semester_start_date = all_config['semester'][0]['semesterStartDate']
            semester_end_date = all_config['semester'][0]['semesterEndDate']
            data = {
                "startDate": semester_start_date,
                "endDate": semester_end_date,
            }
        elif isinstance(arg0, int):
            all_config = self.get_all_config()
            semester = None
            for s in all_config['semester']:
                if s['id'] == arg0:
                    semester = s
                    break
            if semester is None:
                raise ValueError(f"no such semester: {arg0}")
            semester_start_date = semester['semesterStartDate']
            semester_end_date = semester['semesterEndDate']
            data = {
                "startDate": semester_start_date,
                "endDate": semester_end_date,
            }
        else:
            data = {
                "startDate": arg0.strftime("%Y-%m-%d %H:%M:%S"),
                "endDate": arg1.strftime("%Y-%m-%d %H:%M:%S")
            }
        result = self._call_api('queryChosenCourse', data)
        return result

    def chose_course(self, course_id: int):
        """
        choose a course
        :param course_id: the course id, could be obtained from `query_student_semester_course_by_page`
        :return: some useless data if success
        :raise AlreadyChosen: if the course has already been chosen
        :raise FailedToChoose: if failed to choose the course
        """
        result = self._call_api('choseCourse', {'courseId': course_id})
        return result

    def del_chosen_course(self, course_id: int):
        """
        delete a chosen course
        :param course_id: the course id, could be obtained from `query_chosen_course`
        :return: some useless data if success
        :raise FailedToDelChosen: if failed to delete the chosen course
        """
        result = self._call_api('delChosenCourse', {'id': course_id})
        return result
