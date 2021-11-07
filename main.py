import asyncio
from sockbyte import client, server


loop = asyncio.get_event_loop()


def server_main():
    loop.run_until_complete(server.server())

def client_main():
    loop.run_until_complete(client.client())


if __name__ == "__main__":
    from os.path import exists
    if not exists("server.lock"):
        import atexit
        import os

        def dellock():
            os.remove("server.lock")
            print("Server closed")
        
        atexit.register(dellock)

        with open("server.lock", "w") as lockf:
            lockf.write("")
        
        server_main()
    else:
        client_main()
