from client import Client


def test():
    from config import config
    client = Client(config)
    client.soft_login()
    client.query_fore_course()
    client.query_selectable_course()
    client.query_chosen_course()
    client.del_chosen_course(3232)
    client.chose_course(3232)
    client.logout()


if __name__ == '__main__':
    test()
