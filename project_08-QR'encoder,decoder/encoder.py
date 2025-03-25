import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
import os
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def display_banner():
    print(Fore.CYAN + r"""
     ____  ____    ____                        ____            _          
    / ___||  _ \  |  _ \ ___  __ _ _   _ ___ / ___|___   ___ | | ___ ___ 
    \___ \| |_) | | |_) / _ \/ _` | | | / __| |   / _ \ / _ \| |/ _ / __|
     ___) |  _ <  |  _ <  __| (_| | |_| \__ | |__| (_) | (_) | |  __\__ \
    |____/|_| \_\ |_| \_\___|\__, |\__,_|___/\____\___/ \___/|_|\___|___/
                                 |_|                                      
    """)
    print(Fore.YELLOW + "\n🔷 Advanced QR Code Generator 🔷")
    print(Fore.LIGHTBLUE_EX + "──────────────────────────────────────────")

def get_user_input():
    print(Fore.GREEN + "\nQR Code Content Options:")
    print(Fore.WHITE + "1. Text/URL")
    print(Fore.WHITE + "2. Contact Information (vCard)")
    print(Fore.WHITE + "3. WiFi Credentials")
    
    while True:
        try:
            choice = int(input(Fore.CYAN + "\nSelect content type (1-3): "))
            if 1 <= choice <= 3:
                break
            print(Fore.RED + "Please enter between 1 and 3")
        except ValueError:
            print(Fore.RED + "Please enter a valid number")

    if choice == 1:
        data = input(Fore.MAGENTA + "Enter text or URL: ")
    elif choice == 2:
        name = input("Enter name: ")
        phone = input("Enter phone: ")
        email = input("Enter email: ")
        data = f"BEGIN:VCARD\nVERSION:3.0\nN:{name}\nTEL:{phone}\nEMAIL:{email}\nEND:VCARD"
    else:
        ssid = input("Enter WiFi SSID: ")
        password = input("Enter WiFi password: ")
        security = input("Enter security type (WPA/WEP/none): ").upper()
        data = f"WIFI:T:{security};S:{ssid};P:{password};;"

    while True:
        try:
            size = int(input(Fore.CYAN + "QR Code size (10-50): "))
            if 10 <= size <= 50:
                break
            print(Fore.RED + "Please enter between 10 and 50")
        except ValueError:
            print(Fore.RED + "Please enter a valid number")

    return data, size

def generate_qr(data, size):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create styled QR code
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=RadialGradiantColorMask(
            center_color=(70, 130, 180),  # Steel blue
            edge_color=(25, 25, 112)      # Midnight blue
        ),
        embeded_image_path=None
    )
    
    # Save QR code
    if not os.path.exists('qr_codes'):
        os.makedirs('qr_codes')
    
    filename = f"qr_codes/qr_{int(time.time())}.png"
    img.save(filename)
    return filename

def main():
    display_banner()
    data, size = get_user_input()
    filename = generate_qr(data, size)
    
    print(Fore.GREEN + "\n" + "═" * 50)
    print(Fore.YELLOW + f"\n✅ QR Code generated successfully!")
    print(Fore.CYAN + f"📁 Saved as: {filename}")
    print(Fore.LIGHTBLUE_EX + f"📏 Size: {size}px per module")
    print(Fore.MAGENTA + f"📝 Content: {data[:50]}{'...' if len(data) > 50 else ''}")
    
    if input(Fore.MAGENTA + "\nGenerate another QR code? (y/n): ").lower() == 'y':
        main()
    else:
        print(Fore.YELLOW + "\nThank you for using Advanced QR Code Generator!")

if __name__ == '__main__':
    import time
    main()