import sys
import time
from colorama import Fore, Style, init, Back
from pprint import pprint
import random

# Initialize colorama
init(autoreset=True)

class SudokuSolver:
    def __init__(self):
        self.puzzle = [[-1 for _ in range(9)] for _ in range(9)]
        self.original_puzzle = None
        self.solving = False
        self.start_time = 0
        self.solve_time = 0
        self.steps = 0

    def print_banner(self):
        print(Fore.CYAN + r"""
   _____           _       _        
  / ____|         | |     | |       
 | (___  _   _  __| | ___ | | _____ 
  \___ \| | | |/ _` |/ _ \| |/ / __|
  ____) | |_| | (_| | (_) |   <\__ \
 |_____/ \__,_|\__,_|\___/|_|\_\___/
        """)
        print(Fore.YELLOW + "The Ultimate Sudoku Solver")
        print(Fore.GREEN + "="*50)

    def find_next_empty(self, puzzle):
        for r in range(9):
            for c in range(9):
                if puzzle[r][c] == -1:
                    return r, c
        return None, None

    def is_valid(self, puzzle, guess, row, col):
        # Check row
        if guess in puzzle[row]:
            return False

        # Check column
        if guess in [puzzle[i][col] for i in range(9)]:
            return False

        # Check 3x3 box
        row_start = (row // 3) * 3
        col_start = (col // 3) * 3
        for r in range(row_start, row_start + 3):
            for c in range(col_start, col_start + 3):
                if puzzle[r][c] == guess:
                    return False
        return True

    def solve_sudoku(self, puzzle):
        self.steps += 1
        row, col = self.find_next_empty(puzzle)

        if row is None:
            return True

        for guess in range(1, 10):
            if self.is_valid(puzzle, guess, row, col):
                puzzle[row][col] = guess
                if self.solve_sudoku(puzzle):
                    return True
                puzzle[row][col] = -1

        return False

    def generate_puzzle(self, difficulty='medium'):
        # Start with empty puzzle
        self.puzzle = [[-1 for _ in range(9)] for _ in range(9)]
        
        # Fill diagonal 3x3 boxes first (they are independent)
        for box in range(0, 9, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            for i in range(3):
                for j in range(3):
                    self.puzzle[box+i][box+j] = nums.pop()

        # Solve the complete puzzle
        self.solve_sudoku(self.puzzle)
        
        # Now remove numbers based on difficulty
        cells_to_keep = {
            'easy': random.randint(36, 45),
            'medium': random.randint(27, 35),
            'hard': random.randint(17, 26)
        }.get(difficulty, 27)

        all_cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(all_cells)
        
        for i in range(81 - cells_to_keep):
            r, c = all_cells[i]
            self.puzzle[r][c] = -1

        self.original_puzzle = [row[:] for row in self.puzzle]

    def print_puzzle(self, highlight=None):
        clear_screen()
        self.print_banner()
        
        if self.solving:
            print(Fore.MAGENTA + f"\nSolving... Steps: {self.steps} | Time: {time.time() - self.start_time:.2f}s")
        else:
            print(Fore.CYAN + "\nCurrent Puzzle:")

        print(Fore.WHITE + "    " + "   ".join([f"{i}" for i in range(9)]))
        print("  ╔═══╦═══╦═══╦═══╦═══╦═══╦═══╦═══╦═══╗")
        
        for i, row in enumerate(self.puzzle):
            row_str = f"{i} ║"
            for j, num in enumerate(row):
                if num == -1:
                    cell = " "
                else:
                    if self.original_puzzle and self.original_puzzle[i][j] == -1 and num != -1:
                        cell = Fore.GREEN + str(num)  # User-filled cells in green
                    else:
                        cell = Fore.WHITE + str(num)  # Original clues in white
                
                if highlight and highlight == (i, j):
                    cell = Back.YELLOW + Fore.BLACK + cell
                
                row_str += f" {cell} ║"
            
            print(row_str)
            if i < 8:
                if (i + 1) % 3 == 0:
                    print("  ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣")
                else:
                    print("  ║───║───║───║───║───║───║───║───║───║")
        
        print("  ╚═══╩═══╩═══╩═══╩═══╩═══╩═══╩═══╩═══╝")

    def interactive_solve(self):
        self.solving = True
        self.start_time = time.time()
        self.steps = 0
        
        temp_puzzle = [row[:] for row in self.puzzle]
        solved = self.solve_sudoku(temp_puzzle)
        
        self.solve_time = time.time() - self.start_time
        self.solving = False
        
        if solved:
            self.puzzle = temp_puzzle
            self.print_puzzle()
            print(Fore.GREEN + f"\nSolved in {self.steps} steps!")
            print(Fore.GREEN + f"Time taken: {self.solve_time:.2f} seconds")
        else:
            print(Fore.RED + "\nNo solution exists for this puzzle!")

    def manual_fill(self):
        while True:
            self.print_puzzle()
            print(Fore.CYAN + "\nEnter 'solve' to solve, 'new' for new puzzle, or 'quit' to exit")
            print(Fore.CYAN + "Enter cell as row,col,value (e.g. 2,3,5)")
            
            user_input = input(Fore.YELLOW + "> ").strip().lower()
            
            if user_input == 'solve':
                self.interactive_solve()
                input("\nPress Enter to continue...")
                break
            elif user_input == 'new':
                self.select_difficulty()
                break
            elif user_input == 'quit':
                sys.exit()
            else:
                try:
                    parts = user_input.split(',')
                    if len(parts) != 3:
                        raise ValueError
                    row, col, val = map(int, parts)
                    if not (0 <= row <= 8 and 0 <= col <= 8 and 1 <= val <= 9):
                        raise ValueError
                    if self.original_puzzle[row][col] != -1:
                        print(Fore.RED + "Cannot modify original clues!")
                        time.sleep(1)
                        continue
                    self.puzzle[row][col] = val
                except ValueError:
                    print(Fore.RED + "Invalid input. Format as row,col,value (0-8,0-8,1-9)")
                    time.sleep(1)

    def select_difficulty(self):
        while True:
            clear_screen()
            self.print_banner()
            print(Fore.CYAN + "\nSelect Difficulty:")
            print(Fore.WHITE + "1. Easy")
            print(Fore.WHITE + "2. Medium")
            print(Fore.WHITE + "3. Hard")
            print(Fore.WHITE + "4. Custom")
            print(Fore.WHITE + "5. Exit")
            
            choice = input(Fore.YELLOW + "> ").strip()
            
            if choice == '1':
                self.generate_puzzle('easy')
                break
            elif choice == '2':
                self.generate_puzzle('medium')
                break
            elif choice == '3':
                self.generate_puzzle('hard')
                break
            elif choice == '4':
                self.generate_custom_puzzle()
                break
            elif choice == '5':
                sys.exit()
            else:
                print(Fore.RED + "Invalid choice. Please enter 1-5")
                time.sleep(1)

    def generate_custom_puzzle(self):
        while True:
            try:
                clear_screen()
                self.print_banner()
                clues = int(input(Fore.CYAN + "\nEnter number of clues (17-45): "))
                if 17 <= clues <= 45:
                    break
                print(Fore.RED + "Must be between 17 and 45")
                time.sleep(1)
            except ValueError:
                print(Fore.RED + "Please enter a number")
                time.sleep(1)
        
        difficulty = 'easy' if clues > 35 else 'medium' if clues > 26 else 'hard'
        self.generate_puzzle(difficulty)

def clear_screen():
    print("\033c", end="")

def main():
    solver = SudokuSolver()
    
    while True:
        solver.select_difficulty()
        solver.manual_fill()
        
        if input(Fore.CYAN + "\nContinue to next puzzle? (y/n): ").lower() != 'y':
            print(Fore.YELLOW + "\nThanks for using the Sudoku Solver!")
            break

if __name__ == '__main__':
    main()