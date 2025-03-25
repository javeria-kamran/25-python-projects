import math
import time
from colorama import Fore, Style, init
from player import HumanPlayer, RandomComputerPlayer, SmartComputerPlayer

# Initialize colorama
init(autoreset=True)

class TicTacToe():
    def __init__(self):
        self.board = self.make_board()
        self.current_winner = None

    @staticmethod
    def make_board():
        return [' ' for _ in range(9)]

    def print_board(self):
        print(Fore.YELLOW + "\nCurrent Board:")
        for i, row in enumerate([self.board[i*3:(i+1)*3] for i in range(3)]):
            colored_row = []
            for cell in row:
                if cell == 'X':
                    colored_row.append(Fore.RED + cell)
                elif cell == 'O':
                    colored_row.append(Fore.BLUE + cell)
                else:
                    colored_row.append(Fore.WHITE + cell)
            print(Fore.YELLOW + '| ' + ' | '.join(colored_row) + ' |')
            if i < 2:
                print(Fore.YELLOW + '|---|---|---|')

    @staticmethod
    def print_board_nums():
        print(Fore.CYAN + "\nBoard Positions:")
        for i, row in enumerate([[str(j) for j in range(i*3, (i+1)*3)] for i in range(3)]):
            print(Fore.CYAN + '| ' + ' | '.join(row) + ' |')
            if i < 2:
                print(Fore.CYAN + '|---|---|---|')

    def make_move(self, square, letter):
        if self.board[square] == ' ':
            self.board[square] = letter
            if self.winner(square, letter):
                self.current_winner = letter
            return True
        return False

    def winner(self, square, letter):
        # Check row
        row_ind = math.floor(square / 3)
        row = self.board[row_ind*3:(row_ind+1)*3]
        if all([s == letter for s in row]):
            return True
        
        # Check column
        col_ind = square % 3
        column = [self.board[col_ind+i*3] for i in range(3)]
        if all([s == letter for s in column]):
            return True
        
        # Check diagonals
        if square % 2 == 0:
            diagonal1 = [self.board[i] for i in [0, 4, 8]]
            if all([s == letter for s in diagonal1]):
                return True
            diagonal2 = [self.board[i] for i in [2, 4, 6]]
            if all([s == letter for s in diagonal2]):
                return True
        return False

    def empty_squares(self):
        return ' ' in self.board

    def num_empty_squares(self):
        return self.board.count(' ')

    def available_moves(self):
        return [i for i, x in enumerate(self.board) if x == " "]

def play(game, x_player, o_player, print_game=True):
    if print_game:
        print(Fore.GREEN + "\n" + "═" * 40)
        print(Fore.YELLOW + "  Welcome to Tic-Tac-Toe!")
        print(Fore.GREEN + "═" * 40)
        game.print_board_nums()

    letter = 'X'
    while game.empty_squares():
        if letter == 'O':
            square = o_player.get_move(game)
        else:
            square = x_player.get_move(game)
            
        if game.make_move(square, letter):
            if print_game:
                print(Fore.MAGENTA + f"\n{letter} makes a move to square {square}")
                game.print_board()
                print('')

            if game.current_winner:
                if print_game:
                    print(Fore.GREEN + "═" * 40)
                    print(Fore.YELLOW + f"  {letter} wins! Congratulations!")
                    print(Fore.GREEN + "═" * 40)
                return letter

            letter = 'O' if letter == 'X' else 'X'

        time.sleep(0.5)

    if print_game:
        print(Fore.GREEN + "═" * 40)
        print(Fore.YELLOW + "  It's a tie!")
        print(Fore.GREEN + "═" * 40)

if __name__ == '__main__':
    print(Fore.CYAN + "\nSelect Game Mode:")
    print(Fore.WHITE + "1. Human vs Human")
    print(Fore.WHITE + "2. Human vs Computer (Easy)")
    print(Fore.WHITE + "3. Human vs Computer (Hard)")
    
    while True:
        try:
            choice = int(input(Fore.CYAN + "\nEnter your choice (1-3): "))
            if 1 <= choice <= 3:
                break
            print(Fore.RED + "Please enter between 1 and 3")
        except ValueError:
            print(Fore.RED + "Please enter a valid number")

    if choice == 1:
        x_player = HumanPlayer('X')
        o_player = HumanPlayer('O')
    elif choice == 2:
        x_player = HumanPlayer('X')
        o_player = RandomComputerPlayer('O')
    else:
        x_player = HumanPlayer('X')
        o_player = SmartComputerPlayer('O')

    while True:
        t = TicTacToe()
        play(t, x_player, o_player, print_game=True)
        
        if input(Fore.MAGENTA + "\nPlay again? (y/n): ").lower() != 'y':
            print(Fore.YELLOW + "\nThanks for playing! Goodbye!\n")
            break