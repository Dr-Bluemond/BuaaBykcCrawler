import format_tool
from client import Client


def test():
    from config import config
    client = Client(config)
    client.soft_login()
    format_tool.format_print_course(client.query_student_semester_course_by_page(1, 100))
    client.chose_course(1)
    client.logout()


if __name__ == '__main__':
    test()
