"""
client.py

Connects to a Battleship server which runs the single-player game.
Simply pipes user input to the server, and prints all server responses.

TODO: Fix the message synchronization issue using concurrency (Tier 1, item 1).
"""

import socket
import threading

HOST = '127.0.0.1'
PORT = 6000



clientNumber = 0

# HINT: The current problem is that the client is reading from the socket,
# then waiting for user input, then reading again. This causes server
# messages to appear out of order.
#
# Consider using Python's threading module to separate the concerns:
# - One thread continuously reads from the socket and displays messages
# - The main thread handles user input and sends it to the server
#
# import threading

def receive_messages(rfile):
    """Continuously receive and display messages from the server"""
    while True:
        try:
            line = rfile.readline()
            if not line:
                print("[INFO] Server disconnected.")
                break

            line = line.strip()
            # Process and display message
            if line == "GRID":
                print("\n[Board]")
                while True:
                    board_line = rfile.readline()
                    if not board_line or board_line.strip() == "":
                        break
                    print(board_line.strip())
            else:
                print(line)
        except Exception as e:
            print(f"[ERROR] Error receiving message: {e}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        rfile = s.makefile('r')
        wfile = s.makefile('w')

        # One thread for receiving message
        receiver_thread = threading.Thread(target=receive_messages, args=(rfile,))
        receiver_thread.start()

        # Main thread handles user input
        try:
            while True:
                user_input = input(">> ").strip()
                if user_input == "":
                    continue
                elif user_input == "quit":
                    print("Thanks for playing. Goodbye")
                    running = False
                    break
                wfile.write(user_input + '\n')
                wfile.flush()

        except KeyboardInterrupt:
            print("\n[INFO] Client exiting.")
        except Exception as e:
            if running:
                print(f"\n[INFO] Client disconnect: {e}")
        finally:
            s.close()


# HINT: A better approach would be something like:
#
# def receive_messages(rfile):
#     """Continuously receive and display messages from the server"""
#     while running:
#         line = rfile.readline()
#         if not line:
#             print("[INFO] Server disconnected.")
#             break
#         # Process and display the message
#
# def main():
#     # Set up connection
#     # Start a thread for receiving messages
#     # Main thread handles sending user input

if __name__ == "__main__":
    main()