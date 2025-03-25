import random
import time
import matplotlib.pyplot as plt
from colorama import Fore, Style, init
import sys
import numpy as np

# Initialize colorama
init(autoreset=True)

class SearchBenchmark:
    def __init__(self):
        self.results = {
            'native': [],
            'binary': [],
            'sizes': []
        }
        self.colors = {
            'native': Fore.RED,
            'binary': Fore.GREEN,
            'text': Fore.CYAN
        }

    def native_search(self, l, target):
        for i in range(len(l)):
            if l[i] == target:
                return i
        return -1

    def binary_search(self, l, target, low=None, high=None):
        if low is None:
            low = 0
        if high is None:
            high = len(l) - 1
            
        if high < low:
            return -1
        
        midpoint = (low + high) // 2
        
        if l[midpoint] == target:
            return midpoint
        elif target < l[midpoint]:
            return self.binary_search(l, target, low, midpoint - 1)
        else:
            return self.binary_search(l, target, midpoint + 1, high)

    def generate_sorted_list(self, length):
        unique_set = set()
        while len(unique_set) < length:
            unique_set.add(random.randint(-3*length, 3*length))
        return sorted(list(unique_set))

    def run_benchmark(self, min_size=1000, max_size=10000, step=1000):
        print(f"\n{Fore.YELLOW}🚀 Running Search Algorithm Benchmark{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Testing from {min_size} to {max_size} elements in steps of {step}{Style.RESET_ALL}\n")
        
        for size in range(min_size, max_size + 1, step):
            sorted_list = self.generate_sorted_list(size)
            
            # Native search benchmark
            start = time.perf_counter()
            for target in sorted_list:
                self.native_search(sorted_list, target)
            native_time = time.perf_counter() - start
            
            # Binary search benchmark
            start = time.perf_counter()
            for target in sorted_list:
                self.binary_search(sorted_list, target)
            binary_time = time.perf_counter() - start
            
            self.results['native'].append(native_time / size)
            self.results['binary'].append(binary_time / size)
            self.results['sizes'].append(size)
            
            print(f"{self.colors['text']}Size: {size:6d} | "
                  f"{self.colors['native']}Native: {native_time/size:.8f}s | "
                  f"{self.colors['binary']}Binary: {binary_time/size:.8f}s")

    def visualize_results(self):
        plt.figure(figsize=(12, 6))
        
        # Plot Native Search
        plt.plot(self.results['sizes'], self.results['native'], 
                'r-', label='Native Search', linewidth=2)
        
        # Plot Binary Search
        plt.plot(self.results['sizes'], self.results['binary'], 
                'g-', label='Binary Search', linewidth=2)
        
        plt.xlabel('List Size', fontsize=12)
        plt.ylabel('Time per Search (seconds)', fontsize=12)
        plt.title('Search Algorithm Performance Comparison', fontsize=14)
        plt.legend(fontsize=12)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.tight_layout()
        
        # Save and show plot
        plt.savefig('search_benchmark.png', dpi=300)
        print(f"\n{Fore.GREEN}✅ Benchmark results saved as search_benchmark.png{Style.RESET_ALL}")
        plt.show()

    def run_interactive_demo(self):
        print(f"\n{Fore.YELLOW}🔍 Interactive Search Demo{Style.RESET_ALL}")
        size = int(input(f"{Fore.CYAN}Enter list size (10-1000): {Style.RESET_ALL}"))
        if size < 10 or size > 1000:
            size = 100
        
        sorted_list = self.generate_sorted_list(size)
        print(f"\n{Fore.CYAN}Generated a sorted list of {size} unique integers between {-3*size} and {3*size}{Style.RESET_ALL}")
        
        while True:
            target = input(f"\n{Fore.CYAN}Enter number to search (or 'q' to quit): {Style.RESET_ALL}")
            if target.lower() == 'q':
                break
                
            try:
                target = int(target)
            except ValueError:
                print(f"{Fore.RED}Please enter a valid integer{Style.RESET_ALL}")
                continue
                
            print(f"\n{Fore.MAGENTA}Searching for {target}...{Style.RESET_ALL}")
            
            # Native search
            start = time.perf_counter()
            result = self.native_search(sorted_list, target)
            native_time = time.perf_counter() - start
            print(f"{self.colors['native']}Native Search: {'Found' if result != -1 else 'Not found'} at index {result} | Time: {native_time:.8f}s")
            
            # Binary search
            start = time.perf_counter()
            result = self.binary_search(sorted_list, target)
            binary_time = time.perf_counter() - start
            print(f"{self.colors['binary']}Binary Search: {'Found' if result != -1 else 'Not found'} at index {result} | Time: {binary_time:.8f}s")
            
            print(f"\n{Fore.CYAN}Binary search was {native_time/binary_time:.1f}x faster!{Style.RESET_ALL}")

if __name__ == '__main__':
    benchmark = SearchBenchmark()
    
    print(f"\n{Fore.YELLOW}=== Search Algorithm Benchmark Suite ==={Style.RESET_ALL}")
    print(f"{Fore.CYAN}1. Run full benchmark test")
    print(f"{Fore.CYAN}2. Interactive demo")
    print(f"{Fore.CYAN}3. Exit{Style.RESET_ALL}")
    
    while True:
        choice = input(f"\n{Fore.YELLOW}Enter your choice (1-3): {Style.RESET_ALL}")
        
        if choice == '1':
            benchmark.run_benchmark(min_size=1000, max_size=20000, step=2000)
            benchmark.visualize_results()
        elif choice == '2':
            benchmark.run_interactive_demo()
        elif choice == '3':
            print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
            sys.exit()
        else:
            print(f"{Fore.RED}Invalid choice. Please enter 1, 2, or 3.{Style.RESET_ALL}")