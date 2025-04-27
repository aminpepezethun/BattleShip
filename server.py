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
from collections import deque
from battleship import run_two_player_game_online

HOST = '127.0.0.1'
PORT = 6000

# Client queue for auto match-making
CLIENT_QUEUE = deque()


def match_making():
    while True:
        if len(CLIENT_QUEUE) >= 2:
            print("[INFO] 2 clients found. Starting game session")

            (conn1, addr1) = CLIENT_QUEUE.popleft()
            (conn2, addr2) = CLIENT_QUEUE.popleft()

            game_thread = threading.Thread(target=handle_game_session, args=(conn1, addr1, conn2, addr2), daemon=True)
            game_thread.start()
        else:
            time.sleep(0.1)


def handle_game_session(conn1, addr1, conn2, addr2):
    with conn1, conn2:
        print(f"[GAME START] Starting game between {addr1} and {addr2}")

        rfile1 = conn1.makefile('r')
        wfile1 = conn1.makefile('w')
        rfile2 = conn2.makefile('r')
        wfile2 = conn2.makefile('w')

        run_two_player_game_online(rfile1, wfile1, rfile2, wfile2)

        print(f"[GAME END] Game session ended")


def accept_connections():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        print(f"[INFO] Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            print(f"[INFO] Client connected from {addr}")

            CLIENT_QUEUE.append((conn, addr))


def main():
    threading.Thread(target=accept_connections, daemon=True).start()
    threading.Thread(target=match_making, daemon=True).start()

    while True:
        time.sleep(1)





# HINT: For multiple clients, you'd need to:
# 1. Accept connections in a loop
# 2. Handle each client in a separate thread
# 3. Import threading and create a handle_client function

if __name__ == "__main__":
    main()
