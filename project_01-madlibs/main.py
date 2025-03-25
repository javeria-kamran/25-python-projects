import re
import time
import os
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def mad_libs():
    # Clear screen and display header
    print("\033c", end="")
    print(Fore.CYAN + r"""
     __  __           _   _      _       _     
    |  \/  |         | | | |    (_|)   | |    
    | \  / | __ _  __| | | |     _ _ __| |__  
    | |\/| |/ _` |/ _` | | |    | | '__| '_ \ 
    | |  | | (_| | (_| | | |____| | |  | |_) |
    |_|  |_|\__,_|\__,_| |______|_|_|  |_.__/ 
    """)
    time.sleep(0.5)

    # Story templates
    stories = {
        1: {
            'title': "Space Adventure",
            'template': """
            In the year __YEAR__, a __ADJECTIVE__ astronaut named __PERSON__ discovered a __ADJECTIVE__ 
            __ANIMAL__ on planet __PLACE__. The __ANIMAL__ had __NUMBER__ __COLOR__ eyes and could 
            speak __LANGUAGE__. Together, they fought against __ADJECTIVE__ space __NOUN__ using 
            __FOOD__-powered __NOUN__. "This is __ADVERB__ __ADJECTIVE__!" shouted __PERSON__.
            """
        },
        2: {
            'title': "Magical Kingdom",
            'template': """
            Once upon a time in __PLACE__, there lived a __ADJECTIVE__ __ANIMAL__ who could __VERB__ 
            __ADVERB__. One day, it found a __COLOR__ __NOUN__ containing __NUMBER__ __FOOD__ items. 
            The kingdom's __OCCUPATION__ declared this "The __ADJECTIVE__ __EVENT__ of the century!" 
            Everyone celebrated by __VERB_ENDING_IN_ING__ __ADVERB__ until __PERSON__ arrived riding 
            a __ADJECTIVE__ __ANIMAL__.
            """
        },
        3: {
            'title': "Crazy School Day",
            'template': """
            At __PLACE__ High School, our __ADJECTIVE__ teacher Mr./Ms. __PERSON__ taught us how to 
            __VERB__ __ADVERB__ while balancing __NUMBER__ __ANIMAL__ on their __BODY_PART__. Suddenly, 
            a __ADJECTIVE__ __NOUN__ burst in shouting "__EXCLAMATION__!" We all __VERB_ED__ __ADVERB__ 
            and learned __ADJECTIVE__ __NOUN__ instead.
            """
        }
    }

    # Story selection
    print(Fore.YELLOW + "\nChoose your story:")
    for num, story in stories.items():
        print(Fore.WHITE + f"{num}. {story['title']}")
    
    while True:
        try:
            choice = int(input(Fore.GREEN + "\nEnter story number (1-3): "))
            if 1 <= choice <= 3:
                break
            print(Fore.RED + "Please enter 1, 2, or 3!")
        except ValueError:
            print(Fore.RED + "That's not a number!")

    story = stories[choice]['template']
    placeholders = re.findall(r"(__\w+__)", story)

    # Input collection
    inputs = []
    print(Fore.MAGENTA + "\nLet's fill in the blanks! ")
    
    hints = {
        'ADJECTIVE': ['(e.g., fluffy, terrifying)', Fore.YELLOW],
        'NOUN': ['(e.g., banana, spaceship)', Fore.BLUE],
        'VERB': ['(action word)', Fore.CYAN],
        'ADVERB': ['(ends with -ly)', Fore.MAGENTA],
        'ANIMAL': ['(e.g., platypus, dragon)', Fore.GREEN],
        'COLOR': ['', Fore.LIGHTRED_EX],
        'NUMBER': ['', Fore.LIGHTBLUE_EX],
        'PLACE': ['(e.g., Mars, Taco Bell)', Fore.LIGHTYELLOW_EX],
        'PERSON': ['(name)', Fore.LIGHTCYAN_EX],
        'FOOD': ['', Fore.LIGHTMAGENTA_EX],
        'OCCUPATION': ['(e.g., dentist, wizard)', Fore.LIGHTGREEN_EX],
        'EVENT': ['(e.g., Festival, Disaster)', Fore.LIGHTWHITE_EX],
        'BODY_PART': ['', Fore.LIGHTRED_EX],
        'EXCLAMATION': ['(with !)', Fore.RED],
        'YEAR': ['(4 digits)', Fore.WHITE],
        'LANGUAGE': ['(e.g., Klingon, Python)', Fore.LIGHTBLUE_EX],
        'VERB_ENDING_IN_ING': ['(ends with -ing)', Fore.CYAN],
        'VERB_ED': ['(past tense verb)', Fore.CYAN]
    }

    for i, ph_pattern in enumerate(placeholders, 1):
        ph = ph_pattern.strip('_')
        hint_text, color = hints.get(ph, ['', Fore.WHITE])
        
        while True:
            answer = input(f"{color}{i}. Enter {ph.lower()} {hint_text}: {Style.RESET_ALL}").strip()
            if answer:
                inputs.append(answer)
                break
            print(Fore.RED + "Don't leave it blank! Try again.")

    # Build the story
    parts = re.split(r"(__\w+__)", story)
    for i in range(len(parts)):
        if re.match(r"__\w+__", parts[i]):
            parts[i] = inputs.pop(0)

    final_story = ''.join(parts)

    # Display result
    print(Fore.CYAN + "\nGenerating your story", end="")
    for _ in range(3):
        time.sleep(0.3)
        print(Fore.CYAN + ".", end="", flush=True)
    
    print(Fore.GREEN + "\n\n" + "★" * 50)
    print(Fore.YELLOW + "Here's Your Epic Story!\n")
    print(Fore.WHITE + final_story)
    print(Fore.GREEN + "★" * 50 + "\n")

    # Save option with validation
    save_choice = input(Fore.CYAN + "Save story to file? (y/n): ").lower()
    if save_choice == 'y':
        while True:
            filename = input("Enter filename (e.g., my_story.txt): ").strip()
            if filename:  # Check if filename is not empty
                try:
                    with open(filename, 'w') as f:
                        f.write(final_story)
                    print(Fore.GREEN + f"Story saved to {filename}!")
                    break
                except Exception as e:
                    print(Fore.RED + f"Error saving file: {e}")
            else:
                print(Fore.RED + "Filename cannot be empty!")

    # Play again
    if input(Fore.MAGENTA + "\nPlay again? (y/n): ").lower() == 'y':
        mad_libs()
    else:
        print(Fore.RED + "\nThanks for playing! Keep being awesome!\n")

# Start the game
if __name__ == "__main__":
    mad_libs()