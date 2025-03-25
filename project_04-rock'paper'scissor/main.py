import random
import time
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def play_game():
    # Clear screen and display fancy header
    print("\033c", end="")
    print(Fore.CYAN + r"""
     ____            _        ___                 ____                  
    |  _ \ ___   ___| | __   / _ \ _ __   ___   / ___|_ __ ___  ___ ___ 
    | |_) / _ \ / __| |/ /  | | | | '_ \ / __| | |   | '__/ _ \/ __/ __|
    |  _ < (_) | (__|   <   | |_| | |_) | (__  | |___| | | (_) \__ \__ \
    |_| \_\___/ \___|_|\_\   \___/| .__/ \___|  \____|_|  \___/|___/___/
                                  |_|                                   
    """)
    time.sleep(0.5)

    # Game variables
    wins = 0
    losses = 0
    ties = 0
    round_count = 1
    choices = {'r': 'Rock', 'p': 'Paper', 's': 'Scissors'}
    emojis = {'r': '✊', 'p': '✋', 's': '✌️'}
    win_conditions = {'r': 's', 's': 'p', 'p': 'r'}

    print(Fore.YELLOW + "\nWelcome to Rock-Paper-Scissors!")
    print(Fore.LIGHTBLUE_EX + "First to 3 wins becomes the champion!\n")

    while wins < 3 and losses < 3:
        print(Fore.GREEN + f"\n--- Round {round_count} ---")
        print(Fore.CYAN + f"Score: You {wins} - {losses} Computer")
        
        # Get user input with validation
        while True:
            user = input(Fore.MAGENTA + "\nChoose: (R)ock ✊, (P)aper ✋, (S)cissors ✌️, or (Q)uit: ").lower()
            if user in ['r', 'p', 's', 'q']:
                break
            print(Fore.RED + "Invalid choice! Please enter R, P, S, or Q")

        if user == 'q':
            print(Fore.YELLOW + "\nThanks for playing!")
            return

        computer = random.choice(['r', 'p', 's'])

        # Display choices with emojis
        print(Fore.LIGHTBLUE_EX + f"\nYou chose: {choices[user]} {emojis[user]}")
        print(Fore.LIGHTRED_EX + f"Computer chose: {choices[computer]} {emojis[computer]}")

        # Determine winner
        if user == computer:
            print(Fore.YELLOW + "\nIt's a tie!")
            ties += 1
        elif win_conditions[user] == computer:
            print(Fore.GREEN + "\nYou win this round!")
            wins += 1
        else:
            print(Fore.RED + "\nComputer wins this round!")
            losses += 1

        round_count += 1
        time.sleep(1)

    # Game over message
    print(Fore.GREEN + "\n" + "★" * 50)
    if wins == 3:
        print(Fore.YELLOW + "\n🎉 YOU ARE THE CHAMPION! 🎉")
    else:
        print(Fore.RED + "\n💻 Computer wins the game! 💻")

    print(Fore.CYAN + f"\nFinal Score: You {wins} - {losses} Computer")
    print(Fore.LIGHTBLUE_EX + f"Ties: {ties}")
    print(Fore.GREEN + "★" * 50)

    # Play again option
    if input(Fore.MAGENTA + "\nPlay again? (y/n): ").lower() == 'y':
        play_game()
    else:
        print(Fore.YELLOW + "\nThanks for playing! Goodbye!\n")

# Start the game
if __name__ == "__main__":
    play_game()