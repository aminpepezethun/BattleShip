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

# Store games, keys by game ID
GAMES = {}

# def handle_client(conn):
#     while conn:
#         rfile = conn.makefile('r')
#         wfile = conn.makefile('w')
#

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        print(f"[INFO] Server listening on {HOST}:{PORT}")

        print("[INFO] Waiting for player 1 to connect")
        conn1, addr1 = s.accept()
        print(f"[INFO] Player 1 connected from {addr1}")

        print("[INFO] Waiting for player 2 to connect")
        conn2, addr2 = s.accept()
        print(f"[INFO] Player 2 connected from {addr2}")

        with conn1, conn2:
            rfile1 = conn1.makefile('r')
            wfile1 = conn1.makefile('w')
            rfile2 = conn2.makefile('r')
            wfile2 = conn2.makefile('w')

            run_two_player_game_online(rfile1, wfile1, rfile2, wfile2)
            print("[INFO] Game finished. Closing connections.")

    while True:
        time.sleep(1)



# HINT: For multiple clients, you'd need to:
# 1. Accept connections in a loop
# 2. Handle each client in a separate thread
# 3. Import threading and create a handle_client function

if __name__ == "__main__":
    main()
