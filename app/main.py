import asyncio
from app.config import get_port
from app.key_value_store import KeyValueStore
from app.client_handler import handle_client

async def main():
    store = KeyValueStore()
    port = get_port()
    server = await asyncio.start_server(lambda reader, writer: handle_client(reader, writer, store), 'localhost', port)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
