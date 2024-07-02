import asyncio
class KeyValueStore:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key, b"")
    
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
                store.set(args[0], args[1])
                response = b"+OK\r\n"
            elif command == "GET":
                value = store.get(args[0])
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

async def main():
    store = KeyValueStore()
    server = await asyncio.start_server(lambda reader, writer: handle_client(reader, writer, store), 'localhost', 6379)
    async with server:
        await server.serve_forever()

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
    
    


if __name__ == "__main__":
    asyncio.run(main())
