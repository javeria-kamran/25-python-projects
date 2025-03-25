import socket
import sys
from colorama import init, Fore, Style

init(autoreset=True)  # Initialize colorama

class TicTacToeClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player = None
        self.opponent_name = None
        self.player_name = self.get_player_name()
        self.colors = {
            "X": Fore.GREEN,
            "O": Fore.RED,
            "board": Fore.BLUE,
            "error": Fore.RED,
            "info": Fore.CYAN,
            "prompt": Fore.YELLOW
        }

    def get_player_name(self):
        """Get player name with input validation"""
        while True:
            name = input(f"{Fore.CYAN}Enter your name: {Style.RESET_ALL}").strip()
            if name:
                return name
            print(f"{Fore.RED}Name cannot be empty. Please try again.{Style.RESET_ALL}")

    def connect_to_server(self):
        """Establish connection to server with error handling"""
        try:
            print(f"{self.colors['info']}Connecting to server...{Style.RESET_ALL}")
            self.client_socket.settimeout(10)
            self.client_socket.connect(("127.0.0.1", 5555))
            
            # Get player symbol (X/O)
            self.player = self.client_socket.recv(1024).decode()
            self.client_socket.send(self.player_name.encode())
            
            print(f"\n{self.colors['info']}Connected as {self.colors[self.player]}Player {self.player}{Style.RESET_ALL}")
            return True
            
        except socket.timeout:
            print(f"{self.colors['error']}Connection timed out. Server may not be running.{Style.RESET_ALL}")
        except ConnectionRefusedError:
            print(f"{self.colors['error']}Connection refused. Please start the server first.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{self.colors['error']}Connection error: {e}{Style.RESET_ALL}")
        return False

    def display_board(self, board):
        """Display the game board with colors and position numbers"""
        # Display position reference
        print(f"\n{self.colors['board']}Position Reference:")
        print(" 0 | 1 | 2 ")
        print("-----------")
        print(" 3 | 4 | 5 ")
        print("-----------")
        print(" 6 | 7 | 8 ")
        print(f"{Style.RESET_ALL}")

        # Display current board state
        print("Current Game:")
        display = []
        for i, cell in enumerate(board):
            if cell == self.player:
                display.append(f"{self.colors[self.player]}{cell}{Style.RESET_ALL}")
            elif cell != " ":
                display.append(f"{self.colors['O' if self.player == 'X' else 'X']}{cell}{Style.RESET_ALL}")
            else:
                display.append(f"{cell}")
        
        print(f" {display[0]} | {display[1]} | {display[2]} ")
        print("-----------")
        print(f" {display[3]} | {display[4]} | {display[5]} ")
        print("-----------")
        print(f" {display[6]} | {display[7]} | {display[8]} \n")

    def get_player_move(self):
        """Get valid move input from player"""
        while True:
            try:
                move = input(f"{self.colors['prompt']}Your move (0-8) or 'quit': {Style.RESET_ALL}").strip().lower()
                
                if move == "quit":
                    self.client_socket.send("quit".encode())
                    return None
                
                move_int = int(move)
                if 0 <= move_int <= 8:
                    return move
                print(f"{self.colors['error']}Please enter a number between 0-8{Style.RESET_ALL}")
                
            except ValueError:
                print(f"{self.colors['error']}Invalid input. Please enter a number 0-8{Style.RESET_ALL}")

    def play_game(self):
        """Main game loop"""
        try:
            while True:
                try:
                    data = self.client_socket.recv(1024).decode()
                    if not data:
                        print(f"{self.colors['error']}Server disconnected{Style.RESET_ALL}")
                        break

                    if data.startswith("Opponent joined:"):
                        self.opponent_name = data.split(":")[1].strip()
                        print(f"\n{self.colors['info']}Opponent: {self.opponent_name}{Style.RESET_ALL}")
                        continue
                    elif "Game starting!" in data:
                        print(f"\n{self.colors['info']}{data}{Style.RESET_ALL}")
                        continue
                    elif "disconnected" in data:
                        print(f"\n{self.colors['error']}{data}{Style.RESET_ALL}")
                        break
                    elif "wins" in data or "draw" in data:
                        print(f"\n{Fore.MAGENTA}{data}{Style.RESET_ALL}")
                        print(f"{self.colors['info']}Game over. Waiting for new game...{Style.RESET_ALL}")
                        continue

                    self.display_board(data.split(","))

                    if self.player in data or " " not in data:
                        continue

                    move = self.get_player_move()
                    if move is None:  # Player quit
                        break
                    self.client_socket.send(move.encode())

                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"{self.colors['error']}Game error: {e}{Style.RESET_ALL}")
                    break

        except KeyboardInterrupt:
            print(f"\n{self.colors['info']}Quitting game...{Style.RESET_ALL}")
        finally:
            self.client_socket.close()

if __name__ == "__main__":
    print(f"{Fore.CYAN}=== Tic-Tac-Toe Client ==={Style.RESET_ALL}")
    client = TicTacToeClient()
    if client.connect_to_server():
        client.play_game()