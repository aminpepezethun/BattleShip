"""
battleship.py

Contains core data structures and logic for Battleship, including:
 - Board class for storing ship positions, hits, misses
 - Utility function parse_coordinate for translating e.g. 'B5' -> (row, col)
 - A test harness run_single_player_game() to demonstrate the logic in a local, single-player mode

"""

import random as rd

BOARD_SIZE = 10
SHIPS = [
    ("Carrier", 5),
    ("Battleship", 4),
    ("Cruiser", 3),
    ("Submarine", 3),
    ("Destroyer", 2)
]

INSTRUCTIONS = """
    dpub: print public board
    dpriv: print private board (your ship placement)
    quit: exit the game
"""


# class Player:
#     player_id = ""
#     in_game_status = False
#     game_id = ""
#
#     def __init__(self, player_id, in_game_status, game_id):
#         self.player_id = player_id
#         self.in_game_status = in_game_status
#         self.game_id = game_id


class Board:
    """
    Represents a single Battleship board with hidden ships.
    We store:
      - self.hidden_grid: tracks real positions of ships ('S'), hits ('X'), misses ('o')
      - self.display_grid: the version we show to the player ('.' for unknown, 'X' for hits, 'o' for misses)
      - self.placed_ships: a list of dicts, each dict with:
          {
             'name': <ship_name>,
             'positions': set of (r, c),
          }
        used to determine when a specific ship has been fully sunk.

    In a full 2-player networked game:
      - Each player has their own Board instance.
      - When a player fires at their opponent, the server calls
        opponent_board.fire_at(...) and sends back the result.
    """

    def __init__(self, size=BOARD_SIZE):
        self.size = size
        # '.' for empty water
        self.hidden_grid = [['.' for _ in range(size)] for _ in range(size)]
        # display_grid is what the player or an observer sees (no 'S')
        self.display_grid = [['.' for _ in range(size)] for _ in range(size)]
        self.placed_ships = []  # e.g. [{'name': 'Destroyer', 'positions': {(r, c), ...}}, ...] - list of dict [{}]

    def place_ships_randomly(self, ships=SHIPS):
        """
        Randomly place each ship in 'ships' on the hidden_grid, storing positions for each ship.
        In a networked version, you might parse explicit placements from a player's commands
        (e.g. "PLACE A1 H BATTLESHIP") or prompt the user for board coordinates and placement orientations; 
        the self.place_ships_manually() can be used as a guide.
        """
        for ship_name, ship_size in ships:
            placed = False
            while not placed:
                orientation = random.randint(0, 1)  # 0 => horizontal, 1 => vertical
                row = random.randint(0, self.size - 1)
                col = random.randint(0, self.size - 1)

                if self.can_place_ship(row, col, ship_size, orientation):
                    occupied_positions = self.do_place_ship(row, col, ship_size, orientation)
                    self.placed_ships.append({
                        'name': ship_name,
                        'positions': occupied_positions
                    })
                    placed = True

    def place_ships_manually_two_player(self, rfile, wfile, ships=SHIPS):
        """
        Prompt the user for each ship's starting coordinate and orientation (H or V).
        Validates the placement; if invalid, re-prompts.
        """

        def send(msg):
            wfile.write(msg + "\n")
            wfile.flush()

        def recv():
            return rfile.readline().strip()

        def validate_coord(coord):
            try:
                parse_coordinate(coord)
                return True
            except ValueError:
                return False

        def validate_orientation(orientation):
            return orientation.upper() in ['H', 'V']

        send("\n[INFO] Please place your ships manually on the board.")

        for ship_name, ship_size in ships:
            while True:
                self.print_display_grid(wfile, show_hidden_board=True)
                send(f"\nPlacing your {ship_name} (size {ship_size}).")

                send("  [INFO] Enter starting coordinate (e.g. A1): ")
                coord_str = recv().strip().upper()
                if not validate_coord(coord_str):
                    send("[  INFO] Invalid coordinate. Please enter valid coordinate.")
                    continue

                send("  [INFO] Orientation? Enter 'H' (horizontal) or 'V' (vertical): ")
                orientation_str = recv().strip().upper()
                if not validate_orientation(orientation_str):
                    send("  [INFO] Invalid orientation. Please enter valid orientation.")
                    continue

                try:
                    row, col = parse_coordinate(coord_str)
                except ValueError as e:
                    send(f"  [!] Invalid coordinate: {e}")
                    continue

                # Convert orientation_str to 0 (horizontal) or 1 (vertical)
                if orientation_str == 'H':
                    orientation = 0
                elif orientation_str == 'V':
                    orientation = 1
                else:
                    send("  [!] Invalid orientation. Please enter 'H' or 'V'.")
                    continue

                # Check if we can place the ship
                if self.can_place_ship(row, col, ship_size, orientation):
                    occupied_positions = self.do_place_ship(row, col, ship_size, orientation)
                    self.placed_ships.append({
                        'name': ship_name,
                        'positions': occupied_positions
                    })
                    send(f"  [!] Place {ship_name} at {coord_str} (orietation={orientation_str}.")
                    break
                else:
                    send(f"  [!] Cannot place {ship_name} at {coord_str} (orientation={orientation_str}). Try again.")

    def place_ships_manually(self, ships=SHIPS):
        """
        Prompt the user for each ship's starting coordinate and orientation (H or V).
        Validates the placement; if invalid, re-prompts.
        """
        print("\nPlease place your ships manually on the board.")
        for ship_name, ship_size in ships:
            while True:
                self.print_display_grid(show_hidden_board=True)
                print(f"\nPlacing your {ship_name} (size {ship_size}).")
                coord_str = input("  Enter starting coordinate (e.g. A1): ").strip()
                orientation_str = input("  Orientation? Enter 'H' (horizontal) or 'V' (vertical): ").strip().upper()

                try:
                    row, col = parse_coordinate(coord_str)
                except ValueError as e:
                    print(f"  [!] Invalid coordinate: {e}")
                    continue

                # Convert orientation_str to 0 (horizontal) or 1 (vertical)
                if orientation_str == 'H':
                    orientation = 0
                elif orientation_str == 'V':
                    orientation = 1
                else:
                    print("  [!] Invalid orientation. Please enter 'H' or 'V'.")
                    continue

                # Check if we can place the ship
                if self.can_place_ship(row, col, ship_size, orientation):
                    occupied_positions = self.do_place_ship(row, col, ship_size, orientation)
                    self.placed_ships.append({
                        'name': ship_name,
                        'positions': occupied_positions
                    })
                    break
                else:
                    print(f"  [!] Cannot place {ship_name} at {coord_str} (orientation={orientation_str}). Try again.")

    def can_place_ship(self, row, col, ship_size, orientation):
        """
        Check if we can place a ship of length 'ship_size' at (row, col)
        with the given orientation (0 => horizontal, 1 => vertical).
        Returns True if the space is free, False otherwise.
        """
        if orientation == 0:  # Horizontal
            if col + ship_size > self.size:
                return False
            for c in range(col, col + ship_size):
                if self.hidden_grid[row][c] != '.':
                    return False
        else:  # Vertical
            if row + ship_size > self.size:
                return False
            for r in range(row, row + ship_size):
                if self.hidden_grid[r][col] != '.':
                    return False
        return True

    def do_place_ship(self, row, col, ship_size, orientation):
        """
        Place the ship on hidden_grid by marking 'S', and return the set of occupied positions.
        """
        occupied = set()
        if orientation == 0:  # Horizontal
            for c in range(col, col + ship_size):
                self.hidden_grid[row][c] = 'S'
                occupied.add((row, c))
        else:  # Vertical
            for r in range(row, row + ship_size):
                self.hidden_grid[r][col] = 'S'
                occupied.add((r, col))
        return occupied

    def fire_at(self, row, col):
        """
        Fire at (row, col). Return a tuple (result, sunk_ship_name).
        Possible outcomes:
          - ('hit', None)          if it's a hit but not sunk
          - ('hit', <ship_name>)   if that shot causes the entire ship to sink
          - ('miss', None)         if no ship was there
          - ('already_shot', None) if that cell was already revealed as 'X' or 'o'

        The server can use this result to inform the firing player.
        """
        cell = self.hidden_grid[row][col]
        if cell == 'S':
            # Mark a hit
            self.hidden_grid[row][col] = 'X'
            self.display_grid[row][col] = 'X'
            # Check if that hit sank a ship
            sunk_ship_name = self._mark_hit_and_check_sunk(row, col)
            if sunk_ship_name:
                return ('hit', sunk_ship_name)  # A ship has just been sunk
            else:
                return ('hit', None)
        elif cell == '.':
            # Mark a miss
            self.hidden_grid[row][col] = 'o'
            self.display_grid[row][col] = 'o'
            return ('miss', None)
        elif cell == 'X' or cell == 'o':
            return ('already_shot', None)
        else:
            # In principle, this branch shouldn't happen if 'S', '.', 'X', 'o' are all possibilities
            return ('already_shot', None)

    def _mark_hit_and_check_sunk(self, row, col):
        """
        Remove (row, col) from the relevant ship's positions.
        If that ship's positions become empty, return the ship name (it's sunk).
        Otherwise return None.
        """
        for ship in self.placed_ships:
            if (row, col) in ship['positions']:
                ship['positions'].remove((row, col))
                if len(ship['positions']) == 0:
                    return ship['name']
                break
        return None

    def all_ships_sunk(self):
        """
        Check if all ships are sunk (i.e. every ship's positions are empty).
        """
        for ship in self.placed_ships:
            if len(ship['positions']) > 0:
                return False
        return True

    def print_display_grid_two_player(self, wfile, show_hidden_board=False):
        """
        Print the board as a 2D grid.
        
        If show_hidden_board is False (default), it prints the 'attacker' or 'observer' view:
        - '.' for unknown cells,
        - 'X' for known hits,
        - 'o' for known misses.
        
        If show_hidden_board is True, it prints the entire hidden grid:
        - 'S' for ships,
        - 'X' for hits,
        - 'o' for misses,
        - '.' for empty water.
        """
        # Decide which grid to print
        grid_to_print = self.hidden_grid if show_hidden_board else self.display_grid

        # Column headers (1 .. N)
        wfile.write("  " + "".join(str(i + 1).rjust(2) for i in range(self.size)))
        # Each row labeled with A, B, C, ...
        for r in range(self.size):
            row_label = chr(ord('A') + r)
            row_str = " ".join(grid_to_print[r][c] for c in range(self.size))
            wfile.write(f"{row_label:2} {row_str}\n")
        wfile.write('\n')
        wfile.flush()




def run_two_player_game_online(p1_rfile, p1_wfile, p2_rfile, p2_wfile):
    def send(wfile, msg):
        wfile.write(msg + '\n')
        wfile.flush()

    def send_board(wfile, board):
        wfile.write("GRID\n")
        wfile.write("  " + " ".join(str(i + 1).rjust(2) for i in range(board.size)) + '\n')
        for r in range(board.size):
            row_label = chr(ord('A') + r)
            row_str = " ".join(board.display_grid[r][c] for c in range(board.size))
            wfile.write(f"{row_label:2} {row_str}\n")
        wfile.write('\n')
        wfile.flush()

    def recv(rfile):
        return rfile.readline().strip()

    def place_ships_thread(rfile, wfile, board):
        send(wfile, "Place ships manually (M) or randomly (R)? [M/R]: ")
        send(wfile, "[INFO] 30 seconds before randomly assigned")
        choice = recv(rfile).strip().upper()
        if choice == 'M':
            board.place_ships_manually_two_player(rfile, wfile)
        elif choice == 'R':
            board.place_ships_randomly()
        else:
            # write some message to inform user invalid and required them to send again.
            send(wfile, "Invalid arguments. Please enter M (manually) or R (randomly)")
            # ask for them again


    # Boards for each player
    board1 = Board(BOARD_SIZE)
    board2 = Board(BOARD_SIZE)

    # # Send both request for player for ship placement concurrently
    # send(p1_wfile, "Waiting for ship placement")
    # send(p2_wfile, "Waiting for ship placement")
    #
    # # Ask for their ship placement
    # # The prompt will last for 30 seconds and if the user does not choose one, automatically choose random()
    # send(p1_wfile, "Place ships manually (M) or randomly (R)? [M/R]: ")
    # choice1 = recv(p1_rfile).strip().upper()
    # if choice1 == 'M':
    #     board1.place_ships_manually_two_player(p1_rfile, p1_wfile)
    # else:
    #     board1.place_ships_randomly()
    #
    # send(p2_wfile, "Place ships manually (M) or randomly (R)? [M/R]: ")
    # choice2 = recv(p2_rfile).strip().upper()
    # if choice2 == 'M':
    #     board2.place_ships_manually_two_player(p2_rfile, p2_wfile)
    # else:
    #     board2.place_ships_randomly()

    send(p1_wfile, "[INFO] Player 1: Place your ships randomly.")
    board1.place_ships_randomly()
    send(p2_wfile, "[INFO] Player 2: Place your ships randomly.")
    board2.place_ships_randomly()

    # If the 2 players had already set up their ship, start the game
    # When player hit/miss, report to both players what just happened
    current_turn = rd.randint(0,1)
    moves_1 = 0
    moves_2 = 0
    while True:
        if current_turn == 1:
            send(p2_wfile, "[INFO] Opponent is taking their turn.")
            send(p1_wfile, "\nYour turn! Enter coordinate to fire (e.g. b5): ")
            send_board(p1_wfile, board2)  # show opponent's public board

            guess = recv(p1_rfile)

            if guess.lower() == 'quit':
                send(p1_wfile, "Thanks for playing. Goodbye.")
                send(p2_wfile, "[INFO] Opponent quit. Game over")
                return
            elif guess.lower() == 'dpriv':
                send_board(p1_wfile, board1.hidden_grid)
                continue
            elif guess.lower() == 'dpub':
                send_board(p1_wfile, board1)
                continue
            elif guess.lower() == 'help':
                send(p1_wfile, INSTRUCTIONS)
                continue

            try:
                parsed = parse_coordinate(p1_wfile, guess)
                if parsed is None:
                    continue

                row, col = parsed
                result, sunk_name = board2.fire_at(row, col)
                moves_1 += 1

                if result == 'hit':
                    if sunk_name:
                        send(p1_wfile, f"HIT! You sank their {sunk_name}!")
                        send_board(p1_wfile, board2)
                        send(p2_wfile, f"[INFO] OPPONENT HIT AT: {parsed} ! They sank your {sunk_name}!")
                    else:
                        send(p1_wfile, "HIT!")
                        send_board(p1_wfile, board2)
                        send(p2_wfile, f"HIT! OPPONENT HIT AT: {parsed} !")
                    if board2.all_ships_sunk():
                        send_board(p1_wfile, board2)
                        send_board(p1_wfile, board2)
                        send(p1_wfile, f"Congratulations! You sank all ships in {moves_1} moves.")
                        send(p2_wfile, f"YOU LOST! DON'T GIVE UP!")
                        break
                elif result == 'miss':
                    send(p1_wfile, "MISS!")
                    send_board(p1_wfile, board2)
                    send(p2_wfile, f"MISS! OPPONENT HIT AT: {parsed}!")
                elif result == 'already_shot':
                    send(p1_wfile, "You've already fired at that location.")
                    send_board(p1_wfile, board2)
                    continue
            except ValueError as e:
                send(p1_wfile, f"Invalid input: {e}")

            # switch turn
            current_turn = 2
        else:
            send(p1_wfile, "[INFO] Opponent is taking their turn.")
            send(p2_wfile, "\nYour turn! Enter coordinate to fire (e.g. b5): ")
            send_board(p2_wfile, board1)  # show opponent public board

            guess = recv(p2_rfile)

            if guess.lower() == 'quit':
                send(p2_wfile, "Thanks for playing. Goodbye.")
                send(p1_wfile, "[INFO] Opponent quit. Waiting 60 seconds before exiting the match")
                return
            elif guess.lower() == 'help':
                send(p2_wfile, INSTRUCTIONS)
                continue

            try:
                parsed = parse_coordinate(p2_wfile, guess)
                if parsed is None:
                    continue

                row, col = parsed
                result, sunk_name = board1.fire_at(row, col)
                moves_2 += 1

                if result == 'hit':
                    if sunk_name:
                        send(p2_wfile, f"HIT! You sank their {sunk_name}!")
                        send_board(p1_wfile, board2)
                        send(p1_wfile, f"[INFO] OPPONENT HIT AT: {parsed} ! They sank your {sunk_name}!")
                    else:
                        send(p2_wfile, "HIT!")
                        send_board(p2_wfile, board1)
                        send(p1_wfile, f"HIT! OPPONENT HIT AT: {parsed} !")
                    if board1.all_ships_sunk():
                        send_board(p2_wfile, board1)
                        send(p2_wfile, f"Congratulations! You sank all ships in {moves_2} moves.")
                        send(p1_wfile, f"YOU LOST! DON'T GIVE UP!")
                        return
                elif result == 'miss':
                    send(p2_wfile, "MISS!")
                    send_board(p2_wfile, board1)
                    send(p1_wfile, f"MISS! OPPONENT HIT AT: {parsed} !")
                elif result == 'already_shot':
                    send(p2_wfile, "You've already fired at that location.")
                    send_board(p2_wfile, board1)
                    continue
            except ValueError as e:
                send(p2_wfile, f"Invalid input: {e}")

            # switch turn
            current_turn = 1


def parse_coordinate(wfile, coord_str):
    def send(wfile, msg):
        wfile.write(msg + '\n')
        wfile.flush()

    """
    Convert something like 'B5' into zero-based (row, col).
    Example: 'A1' => (0, 0), 'C10' => (2, 9)
    ✅
    - Check length
    - Check cols digit for integer type
    - Check bounds for row and col
    
    Return row, col if valid, else return None
    """
    # Check length
    if len(coord_str) < 2:
        send(wfile, "[INFO] Coordinate too short. Please enter a valid coordinate (e.g. b5)\n")

    coord_str = coord_str.strip().upper()
    row_letter = coord_str[0]
    col_digits = coord_str[1:].strip()

    if not row_letter.isalpha() or not ('A' <= row_letter <= 'K'):
        send(wfile, "[INFO] Row must be a letter from A-K. Please enter a valid coordinate (e.g. B5)\n")
        return None
    if not col_digits.isdigit():
        send(wfile, "[INFO] Column must be a digit from 0-10. Please enter a valid coordinate (e.g. B5)\n")
        return None

    col = int(col_digits)
    if not (1 <= col <= 11):
        send(wfile, "[INFO] Column must be a number from 1 to 11. Please enter a valid coordinate (e.g. b5)\n")
        return None

    row = ord(row_letter) - ord('A')
    col = int(col_digits) - 1  # zero-based

    return row, col


# def run_single_player_game_locally():
#     """
#     A test harness for local single-player mode, demonstrating two approaches:
#      1) place_ships_manually()
#      2) place_ships_randomly()
#
#     Then the player tries to sink them by firing coordinates.
#     """
#     board = Board(BOARD_SIZE)
#
#     # Ask user how they'd like to place ships
#     choice = input("Place ships manually (M) or randomly (R)? [M/R]: ").strip().upper()
#     if choice == 'M':
#         board.place_ships_manually(SHIPS)
#     else:
#         board.place_ships_randomly(SHIPS)
#
#     print("\nNow try to sink all the ships!")
#     moves = 0
#     while True:
#         board.print_display_grid()
#         guess = input("\nEnter coordinate to fire at (or 'quit'): ").strip()
#         if guess.lower() == 'quit':
#             print("Thanks for playing. Exiting...")
#             return
#
#         try:
#             parsed = parse_coordinate(guess)
#             if parsed is None:
#                 continue
#             row, col = parsed
#             result, sunk_name = board.fire_at(row, col)
#             moves += 1
#
#             if result == 'hit':
#                 if sunk_name:
#                     print(f"  >> HIT! You sank the {sunk_name}!")
#                 else:
#                     print("  >> HIT!")
#                 if board.all_ships_sunk():
#                     board.print_display_grid()
#                     print(f"\nCongratulations! You sank all ships in {moves} moves.")
#                     break
#             elif result == 'miss':
#                 print("  >> MISS!")
#             elif result == 'already_shot':
#                 print("  >> You've already fired at that location. Try different location.")
#
#         except ValueError as e:
#             print("  >> Invalid input: ", e)


def run_single_player_game_online(rfile, wfile):
    """
    A test harness for running the single-player game with I/O redirected to socket file objects.
    Expects:
      - rfile: file-like object to .readline() from client
      - wfile: file-like object to .write() back to client
    """

    def send(msg):
        wfile.write(msg + '\n')
        wfile.flush()

    def send_board(board):
        wfile.write("GRID\n")
        wfile.write("  " + " ".join(str(i + 1).rjust(2) for i in range(board.size)) + '\n')
        for r in range(board.size):
            row_label = chr(ord('A') + r)
            row_str = " ".join(board.display_grid[r][c] for c in range(board.size))
            wfile.write(f"{row_label:2} {row_str}\n")
        wfile.write('\n')
        wfile.flush()

    def recv():
        return rfile.readline().strip()

    board = Board(BOARD_SIZE)
    board.place_ships_randomly(SHIPS)

    send("Welcome to Online Single-Player Battleship! Try to sink all the ships. Type 'quit' to exit.")

    moves = 0
    while True:
        send_board(board)
        send("Enter coordinate to fire at (e.g. B5):")
        guess = recv()
        if guess.lower() == 'quit':
            send("Thanks for playing. Goodbye.")
            return
        elif guess.lower() == 'help':
            send(INSTRUCTIONS)
            continue

        try:
            parsed = parse_coordinate(wfile, guess)
            if parsed is None:
                continue
            row, col = parsed
            result, sunk_name = board.fire_at(row, col)
            moves += 1

            if result == 'hit':
                if sunk_name:
                    send(f"HIT! You sank the {sunk_name}!")
                else:
                    send("HIT!")
                if board.all_ships_sunk():
                    send_board(board)
                    send(f"Congratulations! You sank all ships in {moves} moves.")
                    return
            elif result == 'miss':
                send("MISS!")
            elif result == 'already_shot':
                send("You've already fired at that location.")
        except ValueError as e:
            send(f"Invalid input: {e}")

# if __name__ == "__main__":
#     # Optional: run this file as a script to test single-player mode
#     run_single_player_game_locally()
