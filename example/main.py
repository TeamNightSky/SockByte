import asyncio
import client, server


loop = asyncio.get_event_loop()


if __name__ == '__main__':
    import os
    import atexit
    if os.path.exists("server.lock"):
        loop.run_until_complete(client.client())
    else:
        def closelock():
            os.remove("server.lock")
        with open("server.lock", "w") as f:
            pass
        atexit.register(closelock)
        loop.run_until_complete(server.server())



