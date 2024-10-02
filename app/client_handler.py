import asyncio
from app.resp_utils import handle_input, make_bulk_string

# List of supported commands
commands = set(["ECHO", "PING", "SET", "GET", "INFO", "REPLCONF", "PSYNC"])

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
    elif command == "REPLCONF":
        return await replconf_handler(args)
    elif command == "PSYNC":
        return await psync_handler(args, replication)
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

async def replconf_handler(args):
    """Handles the REPLCONF command."""
    return b"+OK\r\n"

EMPTY_RDB_HEX = "524544495330303131fa0972656469732d76657205372e322e30fa0a72656469732d62697473c040fa056374696d65c26d08bc65fa08757365642d6d656dc2b0c41000fa08616f662d62617365c000fff06e3bfec0ff5aa2"
def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

async def psync_handler(args, replication):
    """Handles the PSYNC command."""
    #args = [replication_id, replication_offset]
    if len(args) != 2:
        return b"-Error: Invalid PSYNC command\r\n"

    repl_id = replication.get_replication_id()
    # Respond with FULLRESYNC and the master's replication ID
    response = f"+FULLRESYNC {repl_id} 0\r\n".encode()

    # Send the empty RDB file in bulk string format
    rdb_bytes = hex_to_bytes(EMPTY_RDB_HEX)  # Convert hex RDB to bytes
    rdb_length = len(rdb_bytes)

    # Bulk string format for RDB: $<length_of_file>\r\n<contents_of_file>
    bstring = f"${rdb_length}\r\n".encode() + rdb_bytes

    # Return both the FULLRESYNC response and the bulk string
    return response + bstring
