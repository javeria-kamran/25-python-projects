import os
from colorama import Fore, Style, init
import sys
from PIL import Image

# Initialize colorama
init(autoreset=True)

def display_banner():
    print(Fore.CYAN + r"""
     ____  ____    ____                      _            _          
    / ___||  _ \  |  _ \ ___  __ _ _   _ ___| |_ ___   __| | ___ ___ 
    \___ \| |_) | | |_) / _ \/ _` | | | / __| __/ _ \ / _` |/ _ / __|
     ___) |  _ <  |  _ <  __| (_| | |_| \__ | || (_) | (_| |  __\__ \
    |____/|_| \_\ |_| \_\___|\__, |\__,_|___/\__\___/ \__,_|\___|___/
                                 |_|                                  
    """)
    print(Fore.YELLOW + "\n🔷 Advanced QR Code Decoder 🔷")
    print(Fore.LIGHTBLUE_EX + "──────────────────────────────────────────")

def decode_qr(filename):
    try:
        # Try using OpenCV first
        try:
            import cv2
            img = cv2.imread(filename)
            detector = cv2.QRCodeDetector()
            data, _, _ = detector.detectAndDecode(img)
            if data:
                return data
        except ImportError:
            pass
        
        # Fallback to pure Python method if OpenCV not available
        try:
            import pyzbar.pyzbar as pyzbar
            img = Image.open(filename)
            results = pyzbar.decode(img)
            if results:
                return results[0].data.decode('utf-8')
        except ImportError:
            pass
        
        print(Fore.RED + "No QR code decoder available! Please install opencv-python or pyzbar")
        print(Fore.YELLOW + "Run: pip install opencv-python")
        return None
        
    except Exception as e:
        print(Fore.RED + f"Error decoding QR code: {e}")
        return None

def main():
    display_banner()
    
    # Check if any decoder is available
    try:
        import cv2
    except ImportError:
        try:
            import pyzbar.pyzbar as pyzbar
        except ImportError:
            print(Fore.RED + "\nError: No QR code decoder libraries found!")
            print(Fore.YELLOW + "Please install one of these packages:")
            print(Fore.WHITE + "1. For best results: pip install opencv-python")
            print(Fore.WHITE + "2. Alternative: pip install pyzbar")
            print(Fore.WHITE + "\nRecommended: pip install opencv-python")
            return
    
    while True:
        filename = input(Fore.CYAN + "\nEnter QR code image path (or drag & drop file here): ").strip('"')
        
        if not os.path.exists(filename):
            print(Fore.RED + "File not found! Please try again.")
            continue
            
        data = decode_qr(filename)
        
        if data:
            print(Fore.GREEN + "\n" + "═" * 50)
            print(Fore.YELLOW + "\n🔍 Decoded QR Code Content:")
            print(Fore.WHITE + data)
            
            # Detect content type
            if data.startswith("http"):
                print(Fore.BLUE + "\n🔗 Detected: URL")
            elif data.startswith("WIFI:"):
                print(Fore.BLUE + "\n📶 Detected: WiFi Credentials")
            elif data.startswith("BEGIN:VCARD"):
                print(Fore.BLUE + "\n👤 Detected: Contact Information")
            else:
                print(Fore.BLUE + "\n📝 Detected: Plain Text")
            
            print(Fore.GREEN + "═" * 50)
        
        if input(Fore.MAGENTA + "\nDecode another QR code? (y/n): ").lower() != 'y':
            break
    
    print(Fore.YELLOW + "\nThank you for using Advanced QR Code Decoder!")

if __name__ == '__main__':
    main()