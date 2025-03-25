import random
import time
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def computer_guess(x):
    # Game introduction
    print("\033c", end="")  # Clear screen
    print(Fore.CYAN + r"""
     ____                 _   _                 
    / ___|_ __ ___  __ _| |_(_)_ __   __ _ ___ 
   | |   | '__/ _ \/ _` | __| | '_ \ / _` / __|
   | |___| | |  __/ (_| | |_| | | | | (_| \__ \
    \____|_|  \___|\__,_|\__|_|_| |_|\__, |___/
                                     |___/     
    """)
    print(Fore.YELLOW + f"\nThink of a number between 1 and {x}...")
    time.sleep(1.5)
    print(Fore.MAGENTA + "\nThe computer will try to guess it!")
    time.sleep(1)
    
    low = 1
    high = x
    attempts = 0
    feedback = ''
    guess_history = []
    
    while feedback != 'c':
        attempts += 1
        if low != high:
            guess = random.randint(low, high)
        else:
            guess = low
            
        print(Fore.GREEN + f"\nAttempt #{attempts}")
        print(Fore.LIGHTBLUE_EX + f"Previous guesses: {guess_history[-3:] if guess_history else 'None'}")
        
        while True:
            feedback = input(f'Is {Fore.YELLOW}{guess}{Style.RESET_ALL} too high ({Fore.RED}H{Style.RESET_ALL}), '
                           f'too low ({Fore.GREEN}L{Style.RESET_ALL}), or correct ({Fore.CYAN}C{Style.RESET_ALL})? ').lower()
            if feedback in ['h', 'l', 'c']:
                break
            print(Fore.RED + "Please enter H, L, or C!")
            
        guess_history.append(guess)
        
        if feedback == 'h':
            high = guess - 1
            print(Fore.BLUE + f"Okay, I'll guess lower than {guess}...")
        elif feedback == 'l':
            low = guess + 1
            print(Fore.BLUE + f"Okay, I'll guess higher than {guess}...")
        time.sleep(0.7)

    # Victory celebration
    print(Fore.GREEN + "\n" + "★" * 50)
    print(Fore.YELLOW + f"\nYay! The computer guessed your number, {guess}, correctly!")
    print(Fore.CYAN + f"It only took {attempts} attempts!")
    
    # Performance rating
    if attempts <= 5:
        rating = "amazing"
        color = Fore.MAGENTA
    elif attempts <= 10:
        rating = "good"
        color = Fore.GREEN
    else:
        rating = "not bad"
        color = Fore.YELLOW
    
    print(color + f"\nThat's {rating} performance!")
    print(Fore.GREEN + "★" * 50)
    
    # Play again option
    if input(Fore.MAGENTA + "\nPlay again? (y/n): ").lower() == 'y':
        max_num = int(input(Fore.CYAN + "Enter the maximum number to guess: "))
        computer_guess(max_num)
    else:
        print(Fore.RED + "\nThanks for playing! Goodbye!\n")

# Start the game with configurable range
print("\033c", end="")
max_number = int(input(Fore.CYAN + "Enter the maximum number for the game: "))
computer_guess(max_number)