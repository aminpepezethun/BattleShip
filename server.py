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
import threading
import time
import uuid
from collections import deque
from battleship import run_single_player_game_online, run_two_player_game_online

HOST = '127.0.0.1'
PORT = 6000

# Client queue for auto match-making
CLIENT_QUEUE = deque()

# Section protection
LOCK = threading.Lock()

# Store games, keys by game ID
GAMES = {}

def send(wfile, msg):
    wfile.write(msg + "\n")
    wfile.flush()

def handle_client(conn):
    client_id = str(uuid.uuid4())
    while conn:
        rfile = conn.makefile('r')
        wfile = conn.makefile('w')
        send(wfile, f"[INFO] Client {client_id} successfully connected to server. Waiting for other players to join")
        with LOCK:
            CLIENT_QUEUE.append((rfile, wfile, client_id))

# def match_making():
#     with LOCK:
#         if len(CLIENT_QUEUE) >= 2:
#             p1 = CLIENT_QUEUE.popleft()
#             p2 = CLIENT_QUEUE.popleft()
#
#             threading.Thread(target=run_two_player_game_online, args=(p1[0], p1[1], p2[0], p2[1]), daemon=True).start()
#
#             print(f"[GAME] Paired {p1[3]} and {p2[3]}")
#     time.sleep(1)

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(10)
        print(f"[INFO] Server listening on {HOST}:{PORT}")
        conn, addr = s.accept()

        while True:
            print(f"[INFO] New client connected from {addr}")
            client_thread = threading.Thread(
                target=handle_client,
                args=(conn,)
            )
            client_thread.start()


# HINT: For multiple clients, you'd need to:
# 1. Accept connections in a loop
# 2. Handle each client in a separate thread
# 3. Import threading and create a handle_client function

if __name__ == "__main__":
    main()
