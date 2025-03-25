import random
import time
from colorama import Fore, Style, init
import string
import os
from words import words
from visual import lives_visual_dict

# Initialize colorama
init(autoreset=True)

def get_valid_word(words):
    word = random.choice(words)
    while '-' in word or ' ' in word:
        word = random.choice(words)
    return word.upper()

def display_intro():
    print("\033c", end="")  # Clear screen
    print(Fore.RED + r"""
     _    _                                          
    | |  | |                                         
    | |__| | __ _ _ __   __ _ _ __ ___   __ _ _ __  
    |  __  |/ _` | '_ \ / _` | '_ ` _ \ / _` | '_ \ 
    | |  | | (_| | | | | (_| | | | | | | (_| | | | |
    |_|  |_|\__,_|_| |_|\__, |_| |_| |_|\__,_|_| |_|
                          __/ |                      
                         |___/                       
    """)
    time.sleep(1)
    print(Fore.YELLOW + "\nWelcome to Hangman!")
    print(Fore.CYAN + "Guess the word before the man gets hanged!")
    print(Fore.LIGHTMAGENTA_EX + "You have 7 lives. Good luck!\n")
    time.sleep(1.5)

def hangman():
    display_intro()
    word = get_valid_word(words)
    word_letters = set(word)
    alphabet = set(string.ascii_uppercase)
    used_letters = set()
    lives = 7
    hint_used = False
    word_length = len(word)
    
    # Game statistics
    start_time = time.time()
    incorrect_guesses = []

    while len(word_letters) > 0 and lives > 0:
        print("\033c", end="")  # Clear screen for each guess
        
        # Display game info
        print(Fore.GREEN + f"\nWord Length: {word_length} letters")
        print(Fore.YELLOW + f"Lives remaining: {lives}")
        print(Fore.LIGHTBLUE_EX + f"Used letters: {' '.join(sorted(used_letters))}")
        
        if incorrect_guesses:
            print(Fore.RED + f"Incorrect guesses: {' '.join(incorrect_guesses)}")
        
        # Display hangman visual
        print(Fore.WHITE + lives_visual_dict[lives])
        
        # Display current word progress
        word_list = [letter if letter in used_letters else '_' for letter in word]
        print(Fore.CYAN + "\nCurrent word: " + ' '.join(word_list))
        
        # Hint system
        if not hint_used and lives <= 3:
            hint = input(Fore.MAGENTA + "\nNeed a hint? (y/n): ").lower()
            if hint == 'y':
                hint_letter = random.choice(list(word_letters))
                word_letters.remove(hint_letter)
                used_letters.add(hint_letter)
                print(Fore.GREEN + f"\nHint: The letter {hint_letter} is in the word!")
                hint_used = True
                time.sleep(2)
                continue
        
        # Get user input
        user_letter = input(Fore.LIGHTCYAN_EX + "\nGuess a letter (or 'quit' to exit): ").upper()
        
        if user_letter == 'QUIT':
            print(Fore.YELLOW + "\nThanks for playing!")
            return
        
        if user_letter in alphabet - used_letters:
            used_letters.add(user_letter)
            if user_letter in word_letters:
                word_letters.remove(user_letter)
                print(Fore.GREEN + "\nCorrect!")
            else:
                lives -= 1
                incorrect_guesses.append(user_letter)
                print(Fore.RED + f"\nSorry, {user_letter} is not in the word!")
        elif user_letter in used_letters:
            print(Fore.YELLOW + "\nYou've already guessed that letter!")
        else:
            print(Fore.RED + "\nThat's not a valid letter!")
        
        time.sleep(1)

    # Game over screen
    print("\033c", end="")
    print(Fore.GREEN + "★" * 50)
    
    if lives == 0:
        print(Fore.RED + lives_visual_dict[lives])
        print(Fore.RED + "\nGAME OVER! You ran out of lives.")
        print(Fore.YELLOW + f"The word was: {word}")
    else:
        end_time = time.time()
        game_time = round(end_time - start_time, 2)
        print(Fore.GREEN + lives_visual_dict[lives])
        print(Fore.GREEN + "\nCONGRATULATIONS! You guessed the word!")
        print(Fore.YELLOW + f"The word was: {word}")
        print(Fore.CYAN + f"\nGame Stats:")
        print(Fore.LIGHTBLUE_EX + f"Time taken: {game_time} seconds")
        print(Fore.LIGHTMAGENTA_EX + f"Lives remaining: {lives}")
        print(Fore.LIGHTGREEN_EX + f"Incorrect guesses: {len(incorrect_guesses)}")
    
    print(Fore.GREEN + "★" * 50)
    
    # Play again option
    if input(Fore.MAGENTA + "\nPlay again? (y/n): ").lower() == 'y':
        hangman()
    else:
        print(Fore.YELLOW + "\nThanks for playing! Goodbye!\n")

if __name__ == '__main__':
    hangman()