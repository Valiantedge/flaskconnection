# agent.py

import asyncio
import websockets
import socket  # For TCP connection to private server

PRIVATE_SERVER_HOST = 'private.server.local'
PRIVATE_SERVER_PORT = 12345

async def bridge():
    uri = "ws://public.websocket.server:8765"  # Public WebSocket server endpoint

    async with websockets.connect(uri) as websocket:
        # Connect to private server over TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as private_sock:
            private_sock.connect((PRIVATE_SERVER_HOST, PRIVATE_SERVER_PORT))

            async def websocket_to_private():
                async for message in websocket:
                    print(f"WS->Private: {message}")
                    private_sock.sendall(message.encode())

            async def private_to_websocket():
                while True:
                    data = private_sock.recv(1024)
                    if not data:
                        break
                    await websocket.send(data.decode())
                    print(f"Private->WS: {data}")

            # Run both directions concurrently
            await asyncio.gather(websocket_to_private(), private_to_websocket())

if __name__ == "__main__":
    asyncio.run(bridge())
