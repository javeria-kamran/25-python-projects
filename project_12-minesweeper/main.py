import random
import re
from colorama import Fore, Style, init
import os
import time

# Initialize colorama
init(autoreset=True)

class Board:
    def __init__(self, dim_size, num_bombs):
        self.dim_size = dim_size
        self.num_bombs = num_bombs
        self.board = self.make_new_board()
        self.assign_values_to_board()
        self.dug = set()
        self.flags = set()
        self.game_over = False

    def make_new_board(self):
        board = [[None for _ in range(self.dim_size)] for _ in range(self.dim_size)]
        bombs_planted = 0
        
        while bombs_planted < self.num_bombs:
            loc = random.randint(0, self.dim_size**2 - 1)
            row = loc // self.dim_size
            col = loc % self.dim_size

            if board[row][col] == '*':
                continue

            board[row][col] = '*'
            bombs_planted += 1

        return board

    def assign_values_to_board(self):
        for r in range(self.dim_size):
            for c in range(self.dim_size):
                if self.board[r][c] == '*':
                    continue
                self.board[r][c] = self.get_num_neighboring_bombs(r, c)

    def get_num_neighboring_bombs(self, row, col):
        num_neighboring_bombs = 0
        for r in range(max(0, row-1), min(self.dim_size-1, row+1)+1):
            for c in range(max(0, col-1), min(self.dim_size-1, col+1)+1):
                if r == row and c == col:
                    continue
                if self.board[r][c] == '*':
                    num_neighboring_bombs += 1
        return num_neighboring_bombs

    def dig(self, row, col):
        if (row, col) in self.flags:
            return True
            
        self.dug.add((row, col))
        
        if self.board[row][col] == '*':
            self.game_over = True
            return False
        elif self.board[row][col] > 0:
            return True

        for r in range(max(0, row-1), min(self.dim_size-1, row+1)+1):
            for c in range(max(0, col-1), min(self.dim_size-1, col+1)+1):
                if (r, c) in self.dug:
                    continue
                self.dig(r, c)
        return True

    def toggle_flag(self, row, col):
        if (row, col) in self.dug:
            return False
        if (row, col) in self.flags:
            self.flags.remove((row, col))
        else:
            self.flags.add((row, col))
        return True

    def __str__(self):
        visible_board = [[None for _ in range(self.dim_size)] for _ in range(self.dim_size)]
        
        for row in range(self.dim_size):
            for col in range(self.dim_size):
                if (row, col) in self.dug:
                    cell_value = self.board[row][col]
                    if cell_value == '*':
                        visible_board[row][col] = Fore.RED + '💣' + Style.RESET_ALL
                    elif cell_value == 0:
                        visible_board[row][col] = ' '
                    else:
                        colors = [Fore.BLUE, Fore.GREEN, Fore.RED, Fore.MAGENTA, 
                                 Fore.YELLOW, Fore.CYAN, Fore.BLACK, Fore.WHITE]
                        visible_board[row][col] = colors[cell_value-1] + str(cell_value) + Style.RESET_ALL
                elif (row, col) in self.flags:
                    visible_board[row][col] = Fore.YELLOW + '⚑' + Style.RESET_ALL
                else:
                    visible_board[row][col] = Fore.WHITE + '■' + Style.RESET_ALL

        # Build the board string
        board_str = "\n"
        board_str += "    " + "   ".join([f"{col}" for col in range(self.dim_size)]) + "\n"
        board_str += "  ╔" + "═══╦" * (self.dim_size-1) + "═══╗\n"
        
        for i, row in enumerate(visible_board):
            row_str = f"{i} ║"
            for cell in row:
                row_str += f" {cell} ║"
            board_str += row_str + "\n"
            if i < self.dim_size - 1:
                board_str += "  ╠" + "═══╬" * (self.dim_size-1) + "═══╣\n"
        
        board_str += "  ╚" + "═══╩" * (self.dim_size-1) + "═══╝\n"
        return board_str

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_intro():
    print(Fore.CYAN + r"""
  __  __ _                            
 |  \/  (_)_ __   ___  ___ _ __ ___  
 | |\/| | | '_ \ / _ \/ __| '_ ` _ \ 
 | |  | | | | | |  __/\__ \ | | | | |
 |_|  |_|_|_| |_|\___||___/_| |_| |_|
    """)
    print(Fore.YELLOW + "Welcome to Minesweeper!")
    print(Fore.GREEN + "="*50)
    print(Fore.WHITE + "Instructions:")
    print("- Enter coordinates as row,col (e.g. 2,3)")
    print("- Type 'f' before coordinates to place/remove flag (e.g. f2,3)")
    print("- Flag all bombs to win or uncover all safe squares")
    print(Fore.GREEN + "="*50)

def play():
    clear_screen()
    print_intro()
    
    # Game setup
    while True:
        try:
            difficulty = input(Fore.CYAN + "\nSelect difficulty (1-Easy, 2-Medium, 3-Hard, 4-Custom): ")
            if difficulty == '1':
                dim_size, num_bombs = 8, 10
                break
            elif difficulty == '2':
                dim_size, num_bombs = 10, 20
                break
            elif difficulty == '3':
                dim_size, num_bombs = 12, 40
                break
            elif difficulty == '4':
                dim_size = int(input("Enter board size (5-15): "))
                dim_size = max(5, min(15, dim_size))
                max_bombs = dim_size**2 - 1
                num_bombs = int(input(f"Enter number of bombs (1-{max_bombs}): "))
                num_bombs = max(1, min(max_bombs, num_bombs))
                break
            else:
                print(Fore.RED + "Please enter 1, 2, 3, or 4")
        except ValueError:
            print(Fore.RED + "Please enter a valid number")

    board = Board(dim_size, num_bombs)
    start_time = time.time()
    
    while True:
        clear_screen()
        print_intro()
        print(Fore.MAGENTA + f"\nBoard: {dim_size}x{dim_size} | Bombs: {num_bombs} | Flags: {len(board.flags)}/{num_bombs}")
        print(board)
        
        if board.game_over or len(board.dug) == board.dim_size ** 2 - num_bombs:
            break
            
        user_input = input("\nEnter your move (row,col or frow,col): ").strip().lower()
        
        # Parse input
        flag = False
        if user_input.startswith('f'):
            flag = True
            user_input = user_input[1:]
            
        coords = re.split(',(\\s)*', user_input)
        try:
            row, col = int(coords[0]), int(coords[-1])
            if row < 0 or row >= board.dim_size or col < 0 or col >= board.dim_size:
                print(Fore.RED + "Invalid location. Try again.")
                time.sleep(1)
                continue
        except (ValueError, IndexError):
            print(Fore.RED + "Invalid input. Format as row,col (e.g. 2,3)")
            time.sleep(1)
            continue
            
        if flag:
            board.toggle_flag(row, col)
        else:
            if not board.dig(row, col):
                break  # Game over
                
    # Game ended
    clear_screen()
    print_intro()
    print(board)
    
    if board.game_over:
        print(Fore.RED + "BOOM! You hit a bomb!")
    else:
        print(Fore.GREEN + "CONGRATULATIONS! You cleared the minefield!")
    
    elapsed_time = time.time() - start_time
    print(Fore.CYAN + f"\nGame time: {elapsed_time:.1f} seconds")
    
    if input(Fore.MAGENTA + "\nPlay again? (y/n): ").lower() == 'y':
        play()
    else:
        print(Fore.YELLOW + "\nThanks for playing! Goodbye!")

if __name__ == '__main__':
    play()