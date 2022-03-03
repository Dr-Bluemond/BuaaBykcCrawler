from client import Client


async def test():
    from config import config
    client = Client(config.username, config.password)
    await client.login()
    await client.query_fore_course()
    await client.query_selectable_course()
    await client.query_chosen_course()
    await client.logout()


if __name__ == '__main__':
    import asyncio

    asyncio.run(test())
