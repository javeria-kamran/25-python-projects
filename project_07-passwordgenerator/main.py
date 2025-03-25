import string
import secrets
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def display_banner():
    print(Fore.CYAN + r"""
     ____                            ____                                      _               
    |  _ \ __ _ ___ ___  ___ _ __   / ___|___  _ __ ___  _ __ ___   ___ _ __ | |_ ___  _ __   
    | |_) / _` / __/ __|/ _ \ '__| | |   / _ \| '_ ` _ \| '_ ` _ \ / _ \ '_ \| __/ _ \| '__|  
    |  __/ (_| \__ \__ \  __/ |    | |__| (_) | | | | | | | | | | |  __/ | | | || (_) | |     
    |_|   \__,_|___/___/\___|_|     \____\___/|_| |_| |_|_| |_| |_|\___|_| |_|\__\___/|_|     
    """)
    print(Fore.YELLOW + "\n🔒 Secure Password Generator 🔒")
    print(Fore.LIGHTBLUE_EX + "──────────────────────────────────────────")

def get_password_config():
    print(Fore.GREEN + "\nPassword Requirements:")
    
    while True:
        try:
            count = int(input(Fore.WHITE + "How many passwords to generate? (1-20): "))
            if 1 <= count <= 20:
                break
            print(Fore.RED + "Please enter between 1 and 20")
        except ValueError:
            print(Fore.RED + "Please enter a valid number")

    while True:
        try:
            length = int(input(Fore.WHITE + "Password length (8-64 characters): "))
            if 8 <= length <= 64:
                break
            print(Fore.RED + "Password should be 8-64 characters")
        except ValueError:
            print(Fore.RED + "Please enter a valid number")

    print(Fore.MAGENTA + "\nSelect character types to include:")
    print(Fore.WHITE + "1. Lowercase letters (abc...)")
    print(Fore.WHITE + "2. Uppercase letters (ABC...)")
    print(Fore.WHITE + "3. Digits (123...)")
    print(Fore.WHITE + "4. Special characters (!@#...)")
    print(Fore.WHITE + "5. All of the above")

    while True:
        try:
            choice = int(input(Fore.CYAN + "\nEnter your choice (1-5): "))
            if 1 <= choice <= 5:
                break
            print(Fore.RED + "Please enter between 1 and 5")
        except ValueError:
            print(Fore.RED + "Please enter a valid number")

    return count, length, choice

def generate_password(length, char_set):
    # Use secrets module for cryptographically secure random generation
    return ''.join(secrets.choice(char_set) for _ in range(length))

def main():
    display_banner()
    
    # Character sets
    char_sets = {
        1: string.ascii_lowercase,
        2: string.ascii_uppercase,
        3: string.digits,
        4: '!@#$%&*().,?',
        5: string.ascii_letters + string.digits + '!@#$%&*().,?'
    }
    
    count, length, choice = get_password_config()
    char_set = char_sets[choice]
    
    print(Fore.GREEN + "\n" + "═" * 50)
    print(Fore.YELLOW + "\nGenerated Passwords:")
    
    for i in range(count):
        if choice == 5:
            while True:
                pwd = generate_password(length, char_set)
                # Check if password contains at least one of each type
                if (any(c.islower() for c in pwd) and \
                   (any(c.isupper() for c in pwd) and \
                   (any(c.isdigit() for c in pwd) and \
                   (any(c in '!@#$%&*().,?' for c in pwd))))):
                    break
        else:
            pwd = generate_password(length, char_set)
        
        strength = "Strong" if length >= 12 else "Medium" if length >= 8 else "Weak"
        strength_color = Fore.GREEN if strength == "Strong" else Fore.YELLOW if strength == "Medium" else Fore.RED
        
        print(Fore.CYAN + f"\nPassword {i+1}: " + Fore.WHITE + pwd)
        print(strength_color + f"Strength: {strength} | Length: {length} chars")
    
    print(Fore.GREEN + "\n" + "═" * 50)
    print(Fore.LIGHTBLUE_EX + "\nPassword Safety Tips:")
    print(Fore.WHITE + "1. Use a unique password for each account")
    print(Fore.WHITE + "2. Consider using a password manager")
    print(Fore.WHITE + "3. Change passwords every 3-6 months")
    print(Fore.WHITE + "4. Never share your passwords with anyone")
    
    if input(Fore.MAGENTA + "\nGenerate more passwords? (y/n): ").lower() == 'y':
        main()
    else:
        print(Fore.YELLOW + "\nThank you for using Secure Password Generator!")
        print(Fore.CYAN + "Stay safe online!\n")

if __name__ == '__main__':
    main()