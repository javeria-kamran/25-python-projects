import numpy as np
import png
import os
from colorama import Fore, Style, init
import matplotlib.pyplot as plt
from tqdm import tqdm
from PIL import Image as PILImage

# Initialize colorama
init(autoreset=True)

class ImageProcessor:
    def __init__(self):
        self.input_path = 'input/'
        self.output_path = 'output/'
        self.current_image = None
        self.history = []
        self.supported_formats = ('.png', '.jpg', '.jpeg')
        self.create_directories()

    def create_directories(self):
        os.makedirs(self.input_path, exist_ok=True)
        os.makedirs(self.output_path, exist_ok=True)

    def print_banner(self):
        print(Fore.CYAN + r"""
     _____           _       _____                           _____      _             __   ___  
    |_   _|         | |     |  __ \                         / ____|    | |           /_ | / _ \ 
      | |  _ __  ___| |_ ___| |__) | __ ___  _ __   ___ ___| |     __ _| | ___  ___   | || | | |
      | | | '_ \/ __| __/ _ \  ___/ '__/ _ \| '_ \ / __/ _ \ |    / _` | |/ _ \/ __|  | || | | |
     _| |_| | | \__ \ ||  __/ |   | | | (_) | |_) | (_|  __/ |___| (_| | |  __/\__ \  | || |_| |
    |_____|_| |_|___/\__\___|_|   |_|  \___/| .__/ \___\___|\_____\__,_|_|\___||___/  |_(_)___/ 
                                            | |                                                 
                                            |_|                                                 
        """)
        print(Fore.YELLOW + "Professional Image Processing Toolkit")
        print(Fore.GREEN + "="*70)
        print(Fore.WHITE + f"Supported formats: {', '.join(self.supported_formats)}")
        print(Fore.GREEN + "="*70)

    class Image:
        def __init__(self, processor, filename=''):
            self.processor = processor
            self.filename = filename
            self.array = self.read_image(filename)
            if self.array is not None:
                self.x_pixels, self.y_pixels, self.num_channels = self.array.shape
            else:
                raise ValueError("Failed to load image")

        def read_image(self, filename):
            try:
                filepath = os.path.join(self.processor.input_path, filename)
                
                # Check file extension
                if not filename.lower().endswith(self.processor.supported_formats):
                    print(Fore.RED + f"Unsupported file format: {filename}")
                    return None
                
                # Use PIL to handle multiple formats
                with PILImage.open(filepath) as img:
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img_array = np.array(img) / 255.0  # Normalize to 0-1
                    return img_array
                    
            except Exception as e:
                print(Fore.RED + f"Error reading image: {e}")
                return None

        def write_image(self, output_filename):
            try:
                if not output_filename.lower().endswith('.png'):
                    output_filename += '.png'
                
                output_path = os.path.join(self.processor.output_path, output_filename)
                img_array = (np.clip(self.array, 0, 1) * 255).astype(np.uint8)
                
                with PILImage.fromarray(img_array) as img:
                    img.save(output_path)
                
                print(Fore.GREEN + f"Image successfully saved as {output_filename}")
                return True
                
            except Exception as e:
                print(Fore.RED + f"Error saving image: {e}")
                return False

        def display_stats(self):
            print(Fore.CYAN + "\nImage Statistics:")
            print(Fore.WHITE + f"Filename: {self.filename}")
            print(f"Dimensions: {self.x_pixels}x{self.y_pixels}")
            print(f"Channels: {self.num_channels}")
            print(f"Min value: {np.min(self.array):.4f}")
            print(f"Max value: {np.max(self.array):.4f}")
            print(f"Mean value: {np.mean(self.array):.4f}")

    def list_input_images(self):
        images = [f for f in os.listdir(self.input_path) 
                 if f.lower().endswith(self.supported_formats)]
        if not images:
            print(Fore.RED + "No images found in input folder!")
            return []
        return images

    def load_image(self, filename=None):
        try:
            if filename is None:
                images = self.list_input_images()
                if not images:
                    return False
                
                print(Fore.CYAN + "\nAvailable images:")
                for i, img in enumerate(images, 1):
                    print(Fore.WHITE + f"{i}. {img}")
                
                choice = input(Fore.YELLOW + "\nSelect image (number) or enter filename: ").strip()
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(images):
                        filename = images[choice_num-1]
                    else:
                        print(Fore.RED + "Invalid selection")
                        return False
                except ValueError:
                    filename = choice
            
            self.current_image = self.Image(self, filename)
            self.history.append(f"Loaded image: {filename}")
            self.current_image.display_stats()
            return True
            
        except Exception as e:
            print(Fore.RED + f"\nError loading image: {e}")
            return False

    def show_preview(self):
        if not self.current_image:
            print(Fore.RED + "No image loaded!")
            return

        plt.figure(figsize=(10, 6))
        plt.imshow(self.current_image.array)
        plt.title(f"Preview: {self.current_image.filename}")
        plt.axis('off')
        plt.show()

    # [Rest of your methods (brighten, adjust_contrast, etc.) remain the same]
    # ... (include all the other methods from the previous implementation)

    def run(self):
        self.print_banner()
        
        while True:
            print(Fore.GREEN + "\nMain Menu:")
            print(Fore.CYAN + "1. Load Image")
            print(Fore.CYAN + "2. Show Image Preview")
            print(Fore.CYAN + "3. Brighten/Darken")
            print(Fore.CYAN + "4. Adjust Contrast")
            print(Fore.CYAN + "5. Apply Blur")
            print(Fore.CYAN + "6. Edge Detection")
            print(Fore.CYAN + "7. Save Image")
            print(Fore.CYAN + "8. Show History")
            print(Fore.CYAN + "9. Exit")
            
            choice = input(Fore.YELLOW + "\nEnter your choice (1-9): ").strip()
            
            try:
                if choice == '1':
                    self.load_image()
                elif choice == '2':
                    self.show_preview()
                elif choice == '3':
                    if not self.current_image:
                        print(Fore.RED + "Please load an image first!")
                        continue
                    factor = float(input("Enter brighten factor (>1 brightens, <1 darkens): "))
                    self.brighten(factor)
                # ... (rest of menu handling)
                elif choice == '9':
                    print(Fore.YELLOW + "\nThank you for using the Image Processing Toolkit!")
                    break
                else:
                    print(Fore.RED + "Invalid choice. Please enter 1-9")
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
            
            input("\nPress Enter to continue...")

if __name__ == '__main__':
    processor = ImageProcessor()
    processor.run()