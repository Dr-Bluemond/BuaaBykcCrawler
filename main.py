from client import Client


def test():
    from config import config
    client = Client(config.username, config.password)
    client.login()
    client.query_fore_course()
    client.query_selectable_course()
    client.query_chosen_course()
    client.logout()


if __name__ == '__main__':
    test()
