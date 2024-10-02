import asyncio
from app.resp_utils import handle_input, make_bulk_string

# List of supported commands
commands = set(["ECHO", "PING", "SET", "GET", "INFO"])

async def handle_client(reader, writer, store, replication):
    print("New connection")
    try:
        while data := await reader.read(1024):
            command, *args = await handle_input(data)
            command = command.upper()

            if command not in commands:
                response = b"-Error: Command not found\r\n"
            else:
                response = await dispatch_command(command, args, store, replication)

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

async def dispatch_command(command, args, store, replication):
    """Dispatch command to the correct handler."""
    if command == "PING":
        return await ping_handler()
    elif command == "ECHO":
        return await echo_handler(args)
    elif command == "SET":
        return await set_handler(args, store)
    elif command == "GET":
        return await get_handler(args, store)
    elif command == "INFO":
        return await info_handler(args[0], replication)
    else:
        return b"-Error: Unknown command\r\n"

### Individual command handlers ###

async def ping_handler():
    """Handles the PING command."""
    return b"+PONG\r\n"

async def echo_handler(args):
    """Handles the ECHO command."""
    return await make_bulk_string(args[0])

async def set_handler(args, store):
    """Handles the SET command."""
    key, value, *other = args
    px = int(other[1]) if len(other) == 2 and other[0].upper() == "PX" else None
    await store.set(key, value, px)
    return b"+OK\r\n"

async def get_handler(args, store):
    """Handles the GET command."""
    value = store.get(args[0])
    if not value:
        return b"$-1\r\n"
    else:
        return await make_bulk_string(value)

async def info_handler(param, replication):
    """Handles the INFO command."""
    result_string = ""
    
    if param == "replication":
        result_string += "# Replication\r\n"
        result_string += f"role:{replication.get_role()}\r\n"
        result_string += f"master_replid:{replication.get_replication_id()}\r\n"
        result_string += f"master_repl_offset:{replication.get_replication_offset()}\r\n"

    return await make_bulk_string(result_string)
