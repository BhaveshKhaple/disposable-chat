from flask import Flask, send_from_directory
import asyncio
import websockets
import json
import threading

app = Flask(__name__, static_folder='.')
clients = {}  # Store connected clients by channel

async def chat(websocket): # Removed path argument
    channel_name = None
    username = None
    print(f"New connection: {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"Received: {message}")
            try:
                data = json.loads(message)
                action = data.get('action')
                channel = data.get('channel')
                user = data.get('username')
                password = data.get('password')
                text = data.get('text')

                if action == 'join':
                    if channel and user:
                        if channel not in clients:
                            clients[channel] = {'users': {}, 'history': [], 'password': None}
                        if clients[channel]['password'] and clients[channel]['password'] != password:
                            await websocket.send(json.dumps({'type': 'error', 'message': 'Incorrect password'}))
                            continue
                        clients[channel]['users'][websocket] = user
                        await websocket.send(json.dumps({'type': 'joined', 'channel': channel}))
                        await broadcast(channel, f'{user} joined the chat.')
                    else:
                        await websocket.send(json.dumps({'type': 'error', 'message': 'Channel and username required.'}))

                elif action == 'create':
                    if channel and user:
                        if channel in clients:
                            await websocket.send(json.dumps({'type': 'error', 'message': 'Channel already exists.'}))
                            continue
                        clients[channel] = {'users': {}, 'history': [], 'password': password if password else None}
                        clients[channel]['users'][websocket] = user
                        await websocket.send(json.dumps({'type': 'created', 'channel': channel}))
                        await broadcast(channel, f'{user} created the channel.')
                    else:
                        await websocket.send(json.dumps({'type': 'error', 'message': 'Channel and username required.'}))

                elif action == 'message' and channel and user and text:
                    await broadcast(channel, f'{user}: {text}')
                    clients[channel]['history'].append({'user': user, 'text': text})
                else:
                    await websocket.send(json.dumps({'type': 'error', 'message': 'Invalid action or data.'}))

            except json.JSONDecodeError:
                await websocket.send(json.dumps({'type': 'error', 'message': 'Invalid JSON.'}))
            except Exception as e:
                print(f"Error processing message: {e}")

    except websockets.exceptions.ConnectionClosedError:
        print(f"Connection closed abruptly: {websocket.remote_address}")
    except websockets.exceptions.ConnectionClosedOK:
        print(f"Connection closed normally: {websocket.remote_address}")
    finally:
        for channel, data in list(clients.items()):
            if websocket in data['users']:
                username_leaving = data['users'].pop(websocket)
                await broadcast(channel, f'{username_leaving} left the chat.')
                if not data['users']:
                    del clients[channel]
                    print(f"Channel '{channel}' deleted.")
                break

async def broadcast(channel, message):
    if channel in clients:
        for client in clients[channel]['users']:
            try:
                await client.send(json.dumps({'type': 'message', 'user': 'System', 'text': message}))
            except websockets.exceptions.ConnectionClosedError:
                print(f"Error broadcasting to a closed connection.")
            except Exception as e:
                print(f"Broadcast error: {e}")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

def run_websocket_server():
    async def main():
        async with websockets.serve(chat, "localhost", 5000): # Changed port to 5000
            print("WebSocket server started at ws://localhost:5000")
            await asyncio.Future()  # Run forever
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.get_event_loop().run_until_complete(main())

if __name__ == '__main__':
    websocket_thread = threading.Thread(target=run_websocket_server)
    websocket_thread.daemon = True
    websocket_thread.start()

    app.run(debug=False, port=5000, use_reloader=False) # Flask runs on 5000