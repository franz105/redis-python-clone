import asyncio

async def handle_client(reader, writer):
    print("New connection")
    try:
        while data := await reader.read(1024):
            #TODO: parse input data
            response = b"+PONG\r\n"
            writer.write(response)
            await writer.drain()  # Ensure response is sent
        print("Closing connection")
    except asyncio.CancelledError:
        print("Connection cancelled")
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, 'localhost', 6379)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
