import time
import os
from colorama import Fore, Style, init
import msvcrt  # For Windows keyboard input
import sys
import winsound

# Initialize colorama
init(autoreset=True)

def play_sound(duration=1, frequency=1000):
    """Play a simple beep sound (Windows only)"""
    try:
        winsound.Beep(frequency, duration * 1000)
    except:
        pass  # Skip sound if not on Windows or if error occurs

def display_intro():
    print("\033c", end="")  # Clear screen
    print(Fore.CYAN + r"""
      ____                  _                 _   
     / ___|___  _ __   ___ | |_ _ __ ___   __| |  
    | |   / _ \| '_ \ / _ \| __| '_ ` _ \ / _` |  
    | |__| (_) | | | | (_) | |_| | | | | | (_| |_ 
     \____\___/|_| |_|\___/ \__|_| |_| |_|\__,_(_)
    """)
    print(Fore.YELLOW + "\n🚀 Welcome to the Ultimate Countdown Timer! 🚀")
    print(Fore.LIGHTBLUE_EX + "----------------------------------------\n")

def get_time_input():
    while True:
        try:
            time_input = input(Fore.GREEN + "Enter time (MM:SS or seconds): ")
            
            if ':' in time_input:
                mins, secs = map(int, time_input.split(':'))
                if mins < 0 or secs < 0 or secs >= 60:
                    raise ValueError
                return mins * 60 + secs
            else:
                secs = int(time_input)
                if secs < 0:
                    raise ValueError
                return secs
                
        except ValueError:
            print(Fore.RED + "Invalid input! Please use MM:SS format or positive seconds")

def countdown(t):
    original_time = t
    paused = False
    remaining_time = t
    
    while remaining_time > 0:
        try:
            mins, secs = divmod(remaining_time, 60)
            timeformat = f"{Fore.CYAN}{mins:02d}:{secs:02d}"
            
            # Visual progress bar
            progress = int(50 * (remaining_time / original_time))
            progress_bar = f"{Fore.GREEN}{'█' * progress}{Fore.RED}{'░' * (50 - progress)}"
            
            print("\033c", end="")  # Clear screen
            display_intro()
            print(f"\n{timeformat}")
            print(f"\nProgress: {progress_bar} {remaining_time/original_time:.0%}")
            print(Fore.LIGHTMAGENTA_EX + "\nControls: P = Pause, R = Reset, Q = Quit")
            
            # Play tick sound every second
            if remaining_time % 1 == 0:
                play_sound(0.1, 800 - int(700 * (remaining_time / original_time)))
            
            start_time = time.time()
            
            # Check for keyboard input (Windows-specific)
            if msvcrt.kbhit():
                key = msvcrt.getch().decode().upper()
                if key == 'P':
                    paused = not paused
                    print(Fore.YELLOW + "\nPAUSED" if paused else Fore.GREEN + "\nRESUMED")
                    time.sleep(1)
                elif key == 'R':
                    print(Fore.YELLOW + "\nRESETTING...")
                    time.sleep(1)
                    return True  # Signal to restart
                elif key == 'Q':
                    print(Fore.RED + "\nQUITTING...")
                    time.sleep(1)
                    return False  # Signal to quit
            
            if not paused:
                # Sleep in small increments to remain responsive
                while (time.time() - start_time) < 1:
                    time.sleep(0.1)
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode().upper()
                        if key == 'P':
                            paused = not paused
                            print(Fore.YELLOW + "\nPAUSED" if paused else Fore.GREEN + "\nRESUMED")
                            time.sleep(1)
                            break
                        elif key == 'R':
                            print(Fore.YELLOW + "\nRESETTING...")
                            time.sleep(1)
                            return True
                        elif key == 'Q':
                            print(Fore.RED + "\nQUITTING...")
                            time.sleep(1)
                            return False
                remaining_time -= 1
                
        except KeyboardInterrupt:
            print(Fore.RED + "\nTimer stopped!")
            return False

    # Countdown complete animation
    print("\033c", end="")
    display_intro()
    print(Fore.GREEN + "\n⏰ TIME'S UP! ⏰")
    play_sound(1, 2000)  # Final alarm sound
    time.sleep(2)
    return True  # Signal to restart

def main():
    display_intro()
    
    while True:
        total_seconds = get_time_input()
        
        # Start countdown
        should_restart = countdown(total_seconds)
        
        if not should_restart:
            break
            
        # Ask if user wants to run another timer
        if input(Fore.MAGENTA + "\nStart another timer? (y/n): ").lower() != 'y':
            break
    
    print(Fore.YELLOW + "\nThanks for using the Ultimate Countdown Timer! Goodbye!\n")

if __name__ == '__main__':
    main()