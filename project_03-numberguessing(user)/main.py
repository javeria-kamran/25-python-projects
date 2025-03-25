import random
import time
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def guess_game():
    # Clear screen and display fancy header
    print("\033c", end="")
    print(Fore.CYAN + r"""
     ____                      
    / ___|_   _  ___  ___ ___  
    \___ \ | | |/ _ \/ __/ __| 
     ___) || |_|  __/\__ \__ \ 
    |____/ \__,_|\___||___/___/
    """)
    time.sleep(0.5)
    
    # Game configuration
    max_number = 0
    while max_number <= 1:
        try:
            max_number = int(input(Fore.YELLOW + "\nEnter the maximum number for the game (minimum 2): "))
            if max_number <= 1:
                print(Fore.RED + "Please enter a number greater than 1!")
        except ValueError:
            print(Fore.RED + "Please enter a valid number!")

    # Game setup
    random_number = random.randint(1, max_number)
    attempts = 0
    guess_history = []
    
    print(Fore.MAGENTA + f"\nI'm thinking of a number between 1 and {max_number}...")
    time.sleep(1)
    print(Fore.LIGHTBLUE_EX + "Can you guess it?\n")
    time.sleep(0.5)

    # Main game loop
    while True:
        try:
            guess = int(input(Fore.GREEN + f"Guess a number between 1 and {max_number}: "))
            
            if guess < 1 or guess > max_number:
                print(Fore.RED + f"Please enter a number between 1 and {max_number}!")
                continue
                
            attempts += 1
            guess_history.append(guess)
            
            if guess < random_number:
                print(Fore.BLUE + "Too low! " + Fore.WHITE + "↑ Try higher ↑")
            elif guess > random_number:
                print(Fore.RED + "Too high! " + Fore.WHITE + "↓ Try lower ↓")
            else:
                break
                
        except ValueError:
            print(Fore.RED + "Please enter a valid number!")

    # Victory celebration
    print(Fore.GREEN + "\n" + "★" * 50)
    print(Fore.YELLOW + f"\n🎉 Congratulations! You guessed the number {random_number} correctly!")
    print(Fore.CYAN + f"📊 Total attempts: {attempts}")
    
    # Display guess history
    print(Fore.LIGHTBLUE_EX + "\nYour guess history:")
    for i, g in enumerate(guess_history, 1):
        if g < random_number:
            print(f"{i}. {g} (Too low)")
        elif g > random_number:
            print(f"{i}. {g} (Too high)")
        else:
            print(f"{i}. {g} (Correct!)")

    # Performance rating
    perfect = max_number // 4
    good = max_number // 2
    
    if attempts <= perfect:
        rating = "EXCELLENT"
        color = Fore.MAGENTA
    elif attempts <= good:
        rating = "Great"
        color = Fore.GREEN
    else:
        rating = "Good"
        color = Fore.YELLOW
    
    print(color + f"\n🏆 Performance: {rating}!")
    print(Fore.GREEN + "★" * 50)

    # Play again option
    if input(Fore.MAGENTA + "\nPlay again? (y/n): ").lower() == 'y':
        guess_game()
    else:
        print(Fore.RED + "\nThanks for playing! Goodbye!\n")

# Start the game
if __name__ == "__main__":
    guess_game()