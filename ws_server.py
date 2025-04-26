import asyncio
import websockets
import json

# Temporary storage for channels and users (in-memory)
channels = {}


async def echo(websocket, path):  # Added the 'path' argument
    channels = channels
    print(f"New connection from {websocket.remote_address}, path: {path}")  # Log the path
    try:
        async for message in websocket:
            print(f"Received: {message}")
            data = json.loads(message)
            action = data.get("action")

            if action == "join":
                channel_name = data.get("channel")
                username = data.get("username")
                password = data.get("password")

                if channel_name and username:
                    if channel_name not in channels:
                        channels[channel_name] = {"users": [], "history": [], "password": None}

                    if (
                        channels[channel_name]["password"]
                        and channels[channel_name]["password"] != password
                    ):
                        await websocket.send(
                            json.dumps({"type": "error", "message": "Incorrect password"})
                        )
                        continue  # Don't add the user if password is wrong

                    channels[channel_name]["users"].append(username)
                    print(f"Sending joined message for channel: {channel_name}")
                    await websocket.send(
                        json.dumps({"type": "joined", "channel": channel_name})
                    )
                    print(f"Sent joined message for channel: {channel_name}")
                else:
                    print("Channel and username required for join.")
                    await websocket.send(
                        json.dumps(
                            {"type": "error", "message": "Channel and username required"}
                        )
                    )

            elif action == "create":
                # Implement create logic later
                pass
            elif action == "message":
                # Implement message logic later
                pass

            else:
                print(f"Invalid action: {action}")
                await websocket.send(
                    json.dumps({"type": "error", "message": "Invalid action"})
                )

    except websockets.exceptions.ConnectionClosed as exc:
        print(f"Connection closed: {exc}")
    except websockets.exceptions.ConnectionClosedOK as exc:
        print(f"Connection closed normally: {exc}")
    except json.JSONDecodeError:
        print("Invalid JSON received")
    except Exception as e:
        print(f"Exception in echo: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print(f"Connection closed from server: {websocket.remote_address}")

async def main():
    async with websockets.serve(echo, "localhost", 8765):  # Use a different port (e.g., 8765)
        print("WebSocket server started at ws://localhost:8765")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())