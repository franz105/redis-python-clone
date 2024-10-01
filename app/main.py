import asyncio
from app.config import get_port, get_role
from app.key_value_store import KeyValueStore
from app.client_handler import handle_client
from app.replication import Replication

async def main():
    store = KeyValueStore()
    port = get_port()
    role = get_role()  # Get whether the server is master or slave
    replication = Replication(role)  # Create the Replication object

    server = await asyncio.start_server(lambda reader, writer: handle_client(reader, writer, store, replication), 'localhost', port)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())