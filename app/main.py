import asyncio
from app.config import get_port, get_role, get_replica_host_port
from app.key_value_store import KeyValueStore
from app.client_handler import handle_client
from app.replication import Replication

async def replica_handshake(master_host, master_port, replica_port):
    """Handles the replica connecting to the master and sending PING"""
    try:
        # Connect to the master
        reader, writer = await asyncio.open_connection(master_host, master_port)

        # Send the PING command in RESP format
        ping_message = "*1\r\n$4\r\nPING\r\n"
        writer.write(ping_message.encode())
        await writer.drain()  # Ensure it's sent

        # Should Reveive PONG
        response = await reader.read(100)
        print(f"Received from master: {response.decode()}")

        # Step 2: Send the first REPLCONF command (listening-port)
        replconf_port_message = f"*3\r\n$8\r\nREPLCONF\r\n$14\r\nlistening-port\r\n${len(str(replica_port))}\r\n{replica_port}\r\n"
        writer.write(replconf_port_message.encode())
        await writer.drain()  # Ensure it's sent

        # Wait for the +OK response from the master
        response = await reader.read(100)
        print(f"Received from master: {response.decode()}")

        # Step 3: Send the second REPLCONF command (capa psync2)
        replconf_capa_message = "*3\r\n$8\r\nREPLCONF\r\n$4\r\ncapa\r\n$6\r\npsync2\r\n"
        writer.write(replconf_capa_message.encode())
        await writer.drain()  # Ensure it's sent

        # Wait for the +OK response from the master
        response = await reader.read(100)
        print(f"Received from master: {response.decode()}")

        # Step 4: Send the PSYNC command (PSYNC ? -1)
        psync_message = "*3\r\n$5\r\nPSYNC\r\n$1\r\n?\r\n$2\r\n-1\r\n"
        writer.write(psync_message.encode())
        await writer.drain()  # Ensure it's sent

        # Wait for the +FULLRESYNC response from the master
        response = await reader.read(100)
        print(f"Received from master: {response.decode()}")

        writer.close()
        await writer.wait_closed()
    except Exception as e:
        print(f"Failed to connect to master: {e}")

async def main():
    store = KeyValueStore()
    port = get_port()
    role = get_role()  # Determine if master or slave
    replication = Replication(role)

    # Check if running as replica (slave) or master
    if role == "slave":
        # Get master host and port from command line arguments
        master_host, master_port = get_replica_host_port()
        # Perform handshake (PING) with the master
        await replica_handshake(master_host, master_port, port)

    # Start the server regardless of the role
    server = await asyncio.start_server(
        lambda reader, writer: handle_client(reader, writer, store, replication), 
        'localhost', 
        port
    )
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
