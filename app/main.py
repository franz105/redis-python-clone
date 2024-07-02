import asyncio
import sys 

class KeyValueStore:
    def __init__(self):
        self.data = {}
        self.loop = asyncio.get_running_loop()

    async def set(self, key, value, px = None):
        self.data[key] = value
        if px:
            self.loop.call_later(px/1000, self.expire, key)

    def get(self, key):
        return self.data.get(key, b"")
    
    def expire(self, key): 
        self.data.pop(key, None)
    
async def handle_client(reader, writer, store):
    print("New connection")
    try:
        while data := await reader.read(1024):
            command, args = await handle_input(data)
            response = b""

            if command == "PING":
                response = b"+PONG\r\n"

            elif command == "ECHO":
                response = b"$" + str(len(args[0])).encode() + b"\r\n" + args[0].encode() + b"\r\n"

            elif command == "SET":
                key, value, *other = args
                px = int(other[1]) if len(other) == 2 and other[0].upper() == "PX" else None
                await store.set(key, value, px)
                response = b"+OK\r\n"

            elif command == "GET":
                value = store.get(args[0])
                print(value if value else "None")
                if not value:
                    response = b"$-1\r\n"
                else:
                    response = b"$" + str(len(value)).encode() + b"\r\n" + value.encode() + b"\r\n"

            writer.write(response)
            await writer.drain()  # Ensure response is sent
        print("Closing connection")
    except asyncio.CancelledError:
        print("Connection cancelled")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

# Return a tuple of (command, args), where command is a string and args is an array
async def handle_input(data):
    aggregate = set("$*!=%~>")
    simple = set("+-:_#,(")
    commands = set(["ECHO", "PING", "SET", "GET"])
    command = ""
    args = []

    message = data.decode()
    lst = message.split("\r\n")
    if lst[2].upper() in commands:
        command = lst[2].upper()
    else:
        raise Exception(f"Command {lst[2]} not found")
    i = 3
    while i < len(lst):
        if lst[i] and lst[i][0] not in aggregate:
            args.append(lst[i])
        i += 1

    return command, args

def get_port():
    port = 6379
    i = 0
    while i < len(sys.argv) and sys.argv[i] != "--port":
        i += 1
    
    if i + 1 < len(sys.argv):
        port = int(sys.argv[i+1])
    
    return port
    
async def main():
    store = KeyValueStore()
    port = get_port()
    server = await asyncio.start_server(lambda reader, writer: handle_client(reader, writer, store), 'localhost', port)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
