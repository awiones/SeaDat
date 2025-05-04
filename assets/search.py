import os
import csv
import time
import re
from datetime import datetime
from pathlib import Path
from colorama import init, Fore, Back, Style
from tabulate import tabulate

# Initialize colorama for cross-platform colored terminal
init(autoreset=True)

# Configuration
DATA_FILE = str(Path(__file__).resolve().parent.parent / "data" / "data.csv")

VERSION = "3.0.0" 

# Ocean-themed ASCII art
SEARCH_LOGO = r"""
            .--.                .--.
        .-(    ).-.          .-(    ).-.
        (___.__)__)         (___.__)__)
        ∽∽∽∽∽∽∽∽∽∽         ∽∽∽∽∽∽∽∽∽∽

░██████╗███████╗░█████╗░██████╗░░█████╗░████████╗
██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝
╚█████╗░█████╗░░███████║██║░░██║███████║░░░██║░░░
░╚═══██╗██╔══╝░░██╔══██║██║░░██║██╔══██║░░░██║░░░
██████╔╝███████╗██║░░██║██████╔╝██║░░██║░░░██║░░░
╚═════╝░╚══════╝╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░

                  Sea of Data
                                
∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽~
"""

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_search_header():
    """Display the search module header with ocean theme."""
    clear_screen()
    print(Fore.CYAN + Style.BRIGHT + SEARCH_LOGO)
    print(Fore.WHITE + Style.BRIGHT + f"Created by awiones")
    print(Fore.WHITE + Style.BRIGHT + f"Version: {VERSION}")
    print(Fore.BLUE + "~" * 50)
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"{Fore.CYAN}Dive Time: {Fore.WHITE}{current_time}{Fore.CYAN} | Sonar Active")
    print()

def search_animation(message="Scanning the depths"):
    """Display a sonar-like scanning animation."""
    print(f"\n{Fore.CYAN}{message}", end="", flush=True)
    for i in range(5):
        time.sleep(0.2)
        print(Fore.BLUE + "." + Fore.CYAN + "○" + Fore.BLUE + ".", end="", flush=True)
        time.sleep(0.2)
    print("\n")

def search_by_name(search_term, data_file=DATA_FILE):
    """
    Search for employees by name in the CSV file.
    """
    results = []
    search_term = search_term.lower()
    try:
        with open(data_file, 'r', newline='', encoding='utf-8') as file:
            # Always skip the first row and use the second row as header
            next(file)  # skip index/empty header row
            reader = csv.DictReader(file)
            for row in reader:
                if search_term in row.get('Name', '').lower():
                    results.append(row)
        if results:
            results.sort(key=lambda x: x.get('Name', '').lower())
        return results
    except FileNotFoundError:
        print(f"{Fore.RED}ERROR: Data file not found at {data_file}")
        return []
    except Exception as e:
        print(f"{Fore.RED}ERROR: {str(e)}")
        return []

def search_by_multiple_fields(search_term, data_file=DATA_FILE):
    """
    Search across multiple fields in the CSV file.
    """
    results = []
    search_term = search_term.lower()
    try:
        with open(data_file, 'r', newline='', encoding='utf-8') as file:
            next(file)  # skip index/empty header row
            reader = csv.DictReader(file)
            for row in reader:
                # Only search in Name, NIK, Phone Number, Address
                for field in ["Name", "NIK", "Phone Number", "Address"]:
                    value = row.get(field, "")
                    if value and search_term in str(value).lower():
                        row_copy = dict(row)
                        row_copy['_matched_field'] = field
                        results.append(row_copy)
                        break
        return results
    except FileNotFoundError:
        print(f"{Fore.RED}ERROR: Data file not found at {data_file}")
        return []
    except Exception as e:
        print(f"{Fore.RED}ERROR: {str(e)}")
        return []

def highlight_match(text, search_term):
    """Highlight the matching part of the text."""
    if not text or not search_term:
        return text
    
    pattern = re.compile(f'({re.escape(search_term)})', re.IGNORECASE)
    return pattern.sub(f'{Fore.YELLOW}\\1{Fore.WHITE}', text)

def display_results(results, search_term=""):
    """Display search results in a formatted table with highlighting."""
    if not results:
        print(f"\n{Fore.YELLOW}⚠ No matching records found in the depths.")
        return
    
    print(f"\n{Fore.CYAN}🔍 Discovered {Fore.WHITE}{len(results)}{Fore.CYAN} matching records in the data ocean:\n")
    
    # Prepare table data
    headers = ["Name", "NIK", "Phone Number", "Address"]
    table_data = []
    
    for record in results:
        row = [
            highlight_match(record.get('Name', 'N/A'), search_term),
            highlight_match(record.get('NIK', 'N/A'), search_term),
            highlight_match(record.get('Phone Number', 'N/A'), search_term),
            highlight_match(record.get('Address', 'N/A'), search_term)
        ]
        table_data.append(row)
    
    # Print using tabulate for better alignment
    print(Fore.WHITE + tabulate(
        table_data, 
        headers=headers, 
        tablefmt="pretty"
    ))
    
    print(f"\n{Fore.BLUE}{'~' * 60}")

def confirm_prompt(question):
    """Ask user to confirm an action."""
    response = input(f"{Fore.CYAN}{question} (y/n): {Fore.WHITE}").strip().lower()
    return response == 'y'

def display_help():
    """Display search help."""
    clear_screen()
    print(f"{Fore.CYAN}{Style.BRIGHT}🔍 SEADAT SEARCH GUIDE 🔍")
    print(f"{Fore.BLUE}{'~' * 60}")
    print(f"{Fore.WHITE}Search Commands:")
    print(f"{Fore.CYAN}• {Fore.WHITE}Enter any text to search by name")
    print(f"{Fore.CYAN}• {Fore.WHITE}Type {Fore.YELLOW}back{Fore.WHITE} to return to main menu")
    print(f"{Fore.CYAN}• {Fore.WHITE}Type {Fore.YELLOW}help{Fore.WHITE} to show this guide")
    print(f"{Fore.CYAN}• {Fore.WHITE}Type {Fore.YELLOW}clear{Fore.WHITE} to clear the screen")
    print(f"{Fore.BLUE}{'~' * 60}")
    input(f"\n{Fore.CYAN}Press Enter to return to search...")

def run_search():
    """Run the search functionality with enhanced UI."""
    search_history = []
    
    while True:
        display_search_header()
        
        # Show recent searches if available
        if search_history:
            print(f"{Fore.CYAN}Recent searches: {', '.join([f'{Fore.WHITE}{term}{Fore.CYAN}' for term in search_history[-3:]])}")
        
        print(f"\n{Fore.CYAN}Enter employee name to search")
        print(f"{Fore.CYAN}(Type {Fore.YELLOW}help{Fore.CYAN} for search guide, or {Fore.YELLOW}back{Fore.CYAN} to return):")
        
        search_prompt = f"{Fore.BLUE}≈≈≈>{Fore.WHITE} "
        search_input = input(search_prompt).strip()
        
        if not search_input:
            continue
            
        search_term = search_input.lower()
        
        # Handle special commands
        if search_term == 'back':
            return
        elif search_term == 'help':
            display_help()
            continue
        elif search_term == 'clear':
            continue  # Will clear on next loop
            
        # Add to search history if not a command
        if search_term not in ['back', 'help', 'clear']:
            if search_term not in search_history:
                search_history.append(search_term)
                if len(search_history) > 5:  # Keep only last 5 searches
                    search_history.pop(0)
        
        data_file = Path(DATA_FILE)
        
        if not data_file.exists():
            print(f"\n{Fore.RED}⚠ WARNING: Data file not found at {DATA_FILE}")
            print(f"{Fore.YELLOW}Please make sure the data file exists and try again.")
            input(f"\n{Fore.CYAN}Press Enter to continue...")
            continue
            
        # Check for all-fields search
        if search_term.startswith('*:'):
            # Prevent multiple *: prefixes (e.g., *:*:name)
            if search_term.count('*:') > 1 or search_term.startswith('*:*:'):
                print(f"{Fore.YELLOW}Invalid search: Please use only one '*:' prefix for all-fields search.")
                time.sleep(1.5)
                continue

            actual_term = search_term[2:]
            if not actual_term:
                print(f"{Fore.YELLOW}Please enter a search term after '*:'")
                time.sleep(1.5)
                continue
                
            search_animation(f"Deep scanning all fields for '{actual_term}'")
            results = search_by_multiple_fields(actual_term, data_file)
            display_results(results, actual_term)
        else:
            search_animation(f"Searching employee names for '{search_term}'")
            results = search_by_name(search_term, data_file)
            display_results(results, search_term)
        
        # Provide suggestions if no results
        if not results:
            print(f"{Fore.CYAN}Suggestions:")
            print(f" • Check for typos in your search term")
            print(f" • Try using {Fore.YELLOW}*:{search_term}{Fore.CYAN} to search in all fields")
            print(f" • Use shorter search terms for broader results")
        
        print(f"\n{Fore.CYAN}What would you like to do next?")
        print(f"{Fore.WHITE}[Enter]{Fore.CYAN}: New search  |  {Fore.WHITE}b{Fore.CYAN}: Back to main menu")
        next_action = input(f"{Fore.BLUE}≈≈≈>{Fore.WHITE} ").strip().lower()
        
        if next_action == 'b':
            return

if __name__ == "__main__":
    # This allows the search module to be run independently
    print(f"{Fore.CYAN}Running Search Module directly...")
    run_search()
    print(f"{Fore.CYAN}Search completed. Returning to shore.")