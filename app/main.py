import asyncio
from app.config import get_port, get_role, get_replica_host_port
from app.key_value_store import KeyValueStore
from app.client_handler import handle_client
from app.replication import Replication

async def replica_handshake(master_host, master_port):
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

        # Do parts 2 and 3 of the handshake

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
        await replica_handshake(master_host, master_port)

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
