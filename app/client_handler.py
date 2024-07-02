import asyncio
from app.resp_utils import handle_input, make_bulk_string
from app.config import get_replication


commands = set(["ECHO", "PING", "SET", "GET", "INFO"])
    
async def handle_client(reader, writer, store):
    print("New connection")
    try:
        while data := await reader.read(1024):
            command, *args = await handle_input(data)
            response = b""
            command = command.upper()

            if command not in commands:
                raise Exception(f"Command: {command} not found")    

            if command == "PING":
                response = b"+PONG\r\n"

            elif command == "ECHO":
                response = await make_bulk_string(args[0])
                

            elif command == "SET":
                key, value, *other = args
                px = int(other[1]) if len(other) == 2 and other[0].upper() == "PX" else None
                await store.set(key, value, px)
                response = b"+OK\r\n"

            elif command == "GET":
                value = store.get(args[0])
                if not value:
                    response = b"$-1\r\n"
                else:
                    response = await make_bulk_string(value)
            
            elif command == "INFO":
                response = await info_handler(args[0])

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

async def info_handler(param):
    result_string = ""
    i = 0
    if param == "replication":
        result_string += "# Replication\r\n"
        if get_replication():
            result_string += "role:slave\r\n"
        else:
            result_string += "role:master\r\n"

    return await make_bulk_string(result_string)