import socket
import threading
import time
from datetime import datetime

class TicTacToeServer:
    def __init__(self):
        self.board = [" " for _ in range(9)]
        self.current_player = "X"
        self.clients = []
        self.lock = threading.Lock()
        self.player_names = {}
        self.game_active = False
        self.server_socket = None

    def reset_game(self):
        """Reset the game board and state"""
        with self.lock:
            self.board = [" " for _ in range(9)]
            self.current_player = "X"
            if len(self.clients) == 2:
                self.broadcast_state()

    def handle_client(self, client_socket, player):
        """Handle client connection and game moves"""
        try:
            # Get player name with timeout
            client_socket.settimeout(10)
            name = client_socket.recv(1024).decode().strip()
            self.player_names[player] = name if name else f"Player {player}"
            print(f"{self.player_names[player]} joined as {player}")

            # Notify players when both have connected
            if len(self.clients) == 2:
                self.game_active = True
                self.broadcast_message(f"Game starting! {self.player_names['X']} (X) vs {self.player_names['O']} (O)")
                self.broadcast_state()

            while self.game_active:
                try:
                    move = client_socket.recv(1024).decode().strip()
                    if not move:
                        break

                    if move.lower() == "quit":
                        self.handle_disconnect(client_socket, player)
                        break

                    with self.lock:
                        if self.validate_move(move, player):
                            self.process_move(int(move), player)
                            if self.check_win():
                                self.broadcast_message(f"{self.player_names[player]} wins!")
                                self.game_active = False
                                time.sleep(2)
                                self.reset_game()
                                self.game_active = True
                            elif self.check_draw():
                                self.broadcast_message("It's a draw!")
                                self.game_active = False
                                time.sleep(2)
                                self.reset_game()
                                self.game_active = True

                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error handling move: {e}")
                    break

        except Exception as e:
            print(f"Client error: {e}")
        finally:
            self.handle_disconnect(client_socket, player)

    def validate_move(self, move, player):
        """Validate the received move"""
        try:
            pos = int(move)
            return (0 <= pos < 9 and 
                    self.board[pos] == " " and 
                    self.current_player == player)
        except ValueError:
            return False

    def process_move(self, pos, player):
        """Process a valid move"""
        self.board[pos] = player
        self.current_player = "O" if player == "X" else "X"
        self.broadcast_state()

    def broadcast_state(self):
        """Send current board state to all clients"""
        state = ",".join(self.board)
        for client in self.clients:
            try:
                client.send(state.encode())
            except:
                self.handle_disconnect(client)

    def broadcast_message(self, message):
        """Send a message to all clients"""
        for client in self.clients:
            try:
                client.send(message.encode())
            except:
                self.handle_disconnect(client)

    def check_win(self):
        """Check if current player has won"""
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        for condition in win_conditions:
            if self.board[condition[0]] == self.board[condition[1]] == self.board[condition[2]] != " ":
                return True
        return False

    def check_draw(self):
        """Check if game is a draw"""
        return " " not in self.board

    def handle_disconnect(self, client_socket, player=None):
        """Handle client disconnection"""
        if client_socket in self.clients:
            name = self.player_names.get(player, "A player")
            print(f"{name} disconnected")
            self.clients.remove(client_socket)
            client_socket.close()
            
            if player in self.player_names:
                del self.player_names[player]
                
            if len(self.clients) == 1:
                remaining = self.clients[0]
                try:
                    remaining.send("Opponent disconnected".encode())
                except:
                    self.handle_disconnect(remaining)
            self.game_active = False
            self.reset_game()

    def start_server(self):
        """Start the game server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind(("0.0.0.0", 5555))
            self.server_socket.listen(2)
            print("Server started on port 5555. Waiting for players...")

            while True:
                client_socket, addr = self.server_socket.accept()
                print(f"Connection from {addr}")

                if len(self.clients) < 2:
                    player = "X" if len(self.clients) == 0 else "O"
                    self.clients.append(client_socket)
                    client_socket.send(player.encode())
                    
                    threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, player),
                        daemon=True
                    ).start()
                else:
                    client_socket.send("Server full".encode())
                    client_socket.close()

        except KeyboardInterrupt:
            print("\nShutting down server...")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            for client in self.clients:
                client.close()
            if self.server_socket:
                self.server_socket.close()

if __name__ == "__main__":
    server = TicTacToeServer()
    server.start_server()