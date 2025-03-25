import random
import re
from collections import defaultdict
import json
import os
from typing import List, Dict, Tuple
from colorama import Fore, Style, init
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Initialize colorama
init(autoreset=True)

class AdvancedMarkovChain:
    def __init__(self, order: int = 2):
        self.model: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        self.order = order
        self.stop_words = set(stopwords.words('english')) if 'english' in stopwords.fileids() else set()
        
        # Ensure NLTK data is downloaded
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')

    def preprocess_text(self, text: str) -> List[str]:
        """Clean and tokenize input text."""
        # Remove special characters and normalize whitespace
        text = re.sub(r'[^\w\s]', '', text.lower())
        tokens = word_tokenize(text)
        # Optional: Remove stop words
        # tokens = [word for word in tokens if word not in self.stop_words]
        return tokens

    def train(self, text: str) -> None:
        """Train the Markov model on the given text."""
        words = self.preprocess_text(text)
        
        if len(words) < self.order + 1:
            raise ValueError(f"Text is too short for order {self.order} Markov chain")
        
        for i in range(len(words) - self.order):
            state = tuple(words[i:i + self.order])
            next_word = words[i + self.order]
            self.model[state].append(next_word)

    def train_from_file(self, file_path: str) -> None:
        """Train the model from a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            self.train(text)
            print(Fore.GREEN + f"Successfully trained model from {file_path}")
        except Exception as e:
            print(Fore.RED + f"Error reading file: {e}")

    def generate(self, seed: str = None, length: int = 50, temperature: float = 1.0) -> str:
        """
        Generate text using the trained Markov model.
        
        Args:
            seed: Starting phrase (must match the order of the model)
            length: Maximum length of generated text
            temperature: Controls randomness (0.0 = deterministic, 1.0 = default randomness)
        """
        if not self.model:
            raise ValueError("Model has not been trained yet")
            
        # If no seed provided, start with a random state
        if seed is None:
            current_state = random.choice(list(self.model.keys()))
        else:
            seed_words = self.preprocess_text(seed)
            if len(seed_words) != self.order:
                raise ValueError(f"Seed must contain exactly {self.order} words")
            current_state = tuple(seed_words)
            
            if current_state not in self.model:
                similar = self._find_similar_state(current_state)
                if similar:
                    print(Fore.YELLOW + f"Warning: Seed not found, using similar state instead")
                    current_state = similar
                else:
                    raise ValueError(f"Seed '{seed}' not found in model")

        output = list(current_state)
        
        for _ in range(length):
            if current_state not in self.model:
                break
                
            next_words = self.model[current_state]
            
            # Apply temperature to control randomness
            if temperature != 1.0:
                counts = defaultdict(int)
                for word in next_words:
                    counts[word] += 1
                total = len(next_words)
                weights = [(count / total) ** (1/temperature) for count in counts.values()]
                next_word = random.choices(list(counts.keys()), weights=weights, k=1)[0]
            else:
                next_word = random.choice(next_words)
                
            output.append(next_word)
            current_state = tuple(output[-self.order:])
            
        # Capitalize first letter and add period if missing
        generated = ' '.join(output)
        generated = generated.capitalize()
        if not generated.endswith(('.', '!', '?')):
            generated += '.'
            
        return generated

    def _find_similar_state(self, state: Tuple[str, ...]) -> Tuple[str, ...]:
        """Find a similar state if exact match isn't found."""
        for key in self.model.keys():
            if any(word in key for word in state):
                return key
        return None

    def save_model(self, file_path: str) -> None:
        """Save the trained model to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                # Convert defaultdict to regular dict and tuples to lists for JSON
                model_data = {
                    'order': self.order,
                    'model': {' '.join(k): v for k, v in self.model.items()}
                }
                json.dump(model_data, file)
            print(Fore.GREEN + f"Model saved to {file_path}")
        except Exception as e:
            print(Fore.RED + f"Error saving model: {e}")

    def load_model(self, file_path: str) -> None:
        """Load a trained model from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                model_data = json.load(file)
                self.order = model_data['order']
                self.model = defaultdict(list)
                for k, v in model_data['model'].items():
                    self.model[tuple(k.split())] = v
            print(Fore.GREEN + f"Model loaded from {file_path}")
        except Exception as e:
            print(Fore.RED + f"Error loading model: {e}")

    def interactive_mode(self):
        """Run an interactive session with the Markov chain."""
        print(Fore.CYAN + r"""
  __  __                  _       ____ _           _       
 |  \/  | __ _ _ __ ___ | | __  / ___| |__   __ _| | _____ 
 | |\/| |/ _` | '__/ _ \| |/ / | |   | '_ \ / _` | |/ / _ \
 | |  | | (_| | | | (_) |   <  | |___| | | | (_| |   <  __/
 |_|  |_|\__,_|_|  \___/|_|\_\  \____|_| |_|\__,_|_|\_\___|
        """)
        print(Fore.YELLOW + "Interactive Markov Chain Text Generator")
        print(Fore.GREEN + "="*60)
        
        while True:
            print(Fore.CYAN + "\nOptions:")
            print(Fore.WHITE + "1. Train from text")
            print(Fore.WHITE + "2. Train from file")
            print(Fore.WHITE + "3. Generate text")
            print(Fore.WHITE + "4. Save model")
            print(Fore.WHITE + "5. Load model")
            print(Fore.WHITE + "6. Exit")
            
            choice = input(Fore.YELLOW + "\nEnter your choice (1-6): ").strip()
            
            try:
                if choice == '1':
                    text = input("Enter training text: ")
                    self.train(text)
                    print(Fore.GREEN + "Model trained successfully!")
                elif choice == '2':
                    file_path = input("Enter file path: ")
                    self.train_from_file(file_path)
                elif choice == '3':
                    if not self.model:
                        print(Fore.RED + "Model not trained yet!")
                        continue
                    seed = input(f"Enter seed ({self.order} words) or leave blank: ")
                    length = int(input("Enter length (default 50): ") or "50")
                    temp = float(input("Enter temperature (0.1-2.0, default 1.0): ") or "1.0")
                    try:
                        generated = self.generate(seed if seed else None, length, temp)
                        print(Fore.GREEN + "\nGenerated Text:")
                        print(Fore.WHITE + generated)
                    except ValueError as e:
                        print(Fore.RED + str(e))
                elif choice == '4':
                    file_path = input("Enter file path to save: ")
                    self.save_model(file_path)
                elif choice == '5':
                    file_path = input("Enter file path to load: ")
                    self.load_model(file_path)
                elif choice == '6':
                    print(Fore.YELLOW + "Goodbye!")
                    break
                else:
                    print(Fore.RED + "Invalid choice. Please enter 1-6")
            except Exception as e:
                print(Fore.RED + f"Error: {str(e)}")

if __name__ == "__main__":
    # Example usage
    chain = AdvancedMarkovChain(order=2)
    
    # You can either use the interactive mode
    chain.interactive_mode()
    
    # Or use it programmatically
    # text = "Your training text here..."
    # chain.train(text)
    # print(chain.generate(seed="markov chain", length=100))