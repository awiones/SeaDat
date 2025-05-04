import os
import sys
import time
import random
from pathlib import Path
from colorama import init, Fore, Back, Style

# Ensure project root is in sys.path for module imports
project_root = str(Path(__file__).resolve().parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Initialize colorama for cross-platform colored terminal text
init(autoreset=True)

# Ocean-themed ASCII art
WAVE_PATTERNS = [
    "~^~^~^~^~^~^~^~^~^~",
    "~~~~~~~~~~~~~~~~~~~~~",
    "≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈",
    "∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽",
    "~~~~~~~~~~~~~~~~~~~~~~~~"
]

VERSION = "2.0.0"

# Enhanced SeaDat ASCII logo
LOGO = """
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

def random_wave():
    """Return a random wave pattern."""
    return random.choice(WAVE_PATTERNS)

def display_header():
    """Display the SeaDat header with ocean theme."""
    clear_screen()
    print(Fore.CYAN + Style.BRIGHT + LOGO)
    print(Fore.WHITE + Style.BRIGHT + f"Created by awiones")
    print(Fore.WHITE + Style.BRIGHT + f"Version: {VERSION}")
    print()

def display_menu():
    """Display the main menu options with ocean theme."""
    print(Fore.CYAN + Style.BRIGHT + "\n🔱 NAVIGATION CHART:")
    print(Fore.BLUE + "~" * 50)
    print(Fore.WHITE + Style.BRIGHT + "1. " + Fore.CYAN + "🔍 Dive for Employee Data")
    print(Fore.WHITE + Style.BRIGHT + "2. " + Fore.CYAN + "🤖 AI Search")
    print(Fore.WHITE + Style.BRIGHT + "3. " + Fore.CYAN + "🌐 IP Address Track")
    print(Fore.WHITE + Style.BRIGHT + "4. " + Fore.CYAN + "📸 Instagram Lookup")
    print(Fore.WHITE + Style.BRIGHT + "5. " + Fore.CYAN + "👤 Face Search" + Fore.YELLOW + " (new!)")
    print(Fore.WHITE + Style.BRIGHT + "q. " + Fore.CYAN + "🏝️  Return to Shore")
    print(Fore.BLUE + random_wave() * 2)

def loading_indicator(message="Searching the depths"):
    """Display a loading indicator with an ocean theme."""
    print(f"\n{Fore.CYAN}{message}", end="")
    for _ in range(5):
        time.sleep(0.3)
        print(Fore.BLUE + random.choice(["~", "≈", "∽", "^"]), end="", flush=True)
    print()

def execute_search():
    """Execute the Employee Data Search module."""
    try:
        loading_indicator("🌊 Diving for employee data")
        from assets.search import run_search
        run_search()
    except ImportError as e:
        print(f"\n{Fore.RED}ERROR: search.py module not found!")
        print(f"{Fore.YELLOW}Make sure the search.py file is in the assets directory.")
        print(f"{Fore.YELLOW}ImportError details: {e}")
        input(f"\n{Fore.CYAN}Press Enter to continue...")
    except Exception as e:
        print(f"\n{Fore.RED}ERROR: {str(e)}")
        input(f"\n{Fore.CYAN}Press Enter to continue...")

def execute_ai_search():
    """Execute the AI Search module."""
    try:
        loading_indicator("🤖 Activating AI Search")
        from assets.ai_search import run_ai_search
        run_ai_search()
    except ImportError as e:
        print(f"\n{Fore.RED}ERROR: ai_search.py module not found!")
        print(f"{Fore.YELLOW}Make sure the ai_search.py file is in the assets directory.")
        print(f"{Fore.YELLOW}ImportError details: {e}")
        input(f"\n{Fore.CYAN}Press Enter to continue...")
    except Exception as e:
        print(f"\n{Fore.RED}ERROR: {str(e)}")
        input(f"\n{Fore.CYAN}Press Enter to continue...")

def execute_ip_track():
    """Execute the IP Address Track module."""
    try:
        loading_indicator("🌊 Tracking IP address")
        from assets.ip_track import run_ip_track
        run_ip_track()
    except ImportError as e:
        print(f"\n{Fore.RED}ERROR: ip_track.py module not found!")
        print(f"{Fore.YELLOW}Make sure the ip_track.py file is in the assets directory.")
        print(f"{Fore.YELLOW}ImportError details: {e}")
        input(f"\n{Fore.CYAN}Press Enter to continue...")
    except Exception as e:
        print(f"\n{Fore.RED}ERROR: {str(e)}")
        input(f"\n{Fore.CYAN}Press Enter to continue...")

def execute_instagram_lookup():
    """Execute the Instagram Lookup module."""
    try:
        loading_indicator("🌊 Looking up Instagram profile")
        from assets.instagram_lookup import run_instagram_lookup
        run_instagram_lookup()
    except ImportError as e:
        print(f"\n{Fore.RED}ERROR: instagram_lookup.py module not found!")
        print(f"{Fore.YELLOW}Make sure the instagram_lookup.py file is in the assets directory.")
        print(f"{Fore.YELLOW}ImportError details: {e}")
        input(f"\n{Fore.CYAN}Press Enter to continue...")
    except Exception as e:
        print(f"\n{Fore.RED}ERROR: {str(e)}")
        input(f"\n{Fore.CYAN}Press Enter to continue...")

def execute_image_search():
    """Execute the Image Search module."""
    try:
        loading_indicator("🔍 Activating Face Search")
        from assets.image_search import run_image_search
        run_image_search()
    except ImportError as e:
        print(f"\n{Fore.RED}ERROR: image_search.py module not found!")
        print(f"{Fore.YELLOW}Make sure the image_search.py file is in the assets directory.")
        print(f"{Fore.YELLOW}ImportError details: {e}")
        input(f"\n{Fore.CYAN}Press Enter to continue...")
    except Exception as e:
        print(f"\n{Fore.RED}ERROR: {str(e)}")
        input(f"\n{Fore.CYAN}Press Enter to continue...")

def main():
    """Main function to run the SeaDat tool."""
    
    while True:
        display_header()
        display_menu()
        
        choice = input(f"\n{Fore.CYAN}⚓ Enter your navigation choice (1-5 or q): ").strip().lower()
        
        if choice == '1':
            execute_search()
        elif choice == '2':
            execute_ai_search()
        elif choice == '3':
            execute_ip_track()
        elif choice == '4':
            execute_instagram_lookup()
        elif choice == '5':
            execute_image_search()
        elif choice == 'q':
            print(f"\n{Fore.CYAN}Thank you for exploring the Sea of Data. Safe journey back to shore!")
            for i in range(3):
                print(Fore.BLUE + random_wave() * (5 - i))
                time.sleep(0.3)
            sys.exit(0)
        else:
            print(f"\n{Fore.YELLOW}⚠️ Uncharted waters! Please choose a valid navigation option.")
            time.sleep(1.5)

if __name__ == "__main__":
    # Ensure the data directory exists
    data_dir = Path(project_root) / "data"
    if not data_dir.exists():
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
            print(f"{Fore.GREEN}Created data directory: {data_dir}")
        except Exception as e:
            print(f"{Fore.RED}WARNING: Could not create data directory: {e}")
            print(f"{Fore.YELLOW}The program will continue, but navigation may be limited.")
            time.sleep(2)
    
    # Run the main program
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.CYAN}Emergency surface! Thank you for using SeaDat.")
        sys.exit(0)