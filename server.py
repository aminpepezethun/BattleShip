"""
server.py

Serves a single-player Battleship session to one connected client.
Game logic is handled entirely on the server using battleship.py.
Client sends FIRE commands, and receives game feedback.

TODO: For Tier 1, item 1, you don't need to modify this file much. 
The core issue is in how the client handles incoming messages.
However, if you want to support multiple clients (i.e. progress through further Tiers), you'll need concurrency here too.
"""

import socket
from battleship import run_single_player_game_online
import threading

HOST = '127.0.0.1'
PORT = 6000

def handle_client(conn, addr):
    print(f"[INFO] Handling client from {addr}")

    with conn:
        rfile = conn.makefile('r')
        wfile = conn.makefile('w')

        run_single_player_game_online(rfile, wfile)
    print(f"[INFO] Client {addr} disconnected from server.")


def main():
    print(f"[INFO] Server listening on {HOST}:{PORT}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((HOST, PORT))
    except socket.error as e:
        str(e)

    s.listen(2)

    while True:
        conn, addr = s.accept()
        player_thread = threading.Thread(target=handle_client, args=(conn, addr))
        player_thread.start()

# HINT: For multiple clients, you'd need to:
# 1. Accept connections in a loop
# 2. Handle each client in a separate thread
# 3. Import threading and create a handle_client function

if __name__ == "__main__":
    main()