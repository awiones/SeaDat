import os
import csv
import time
import re
from datetime import datetime
from pathlib import Path
from colorama import init, Fore, Back, Style
from tabulate import tabulate
import requests
from deepface import DeepFace
import numpy as np
import cv2
from tqdm import tqdm
import tempfile
import sys

misc_path = str(Path(__file__).resolve().parent.parent / "misc")
if misc_path not in sys.path:
    sys.path.append(misc_path)
try:
    from misc.training import FaceRecognitionSystem
except ImportError:
    try:
        from training import FaceRecognitionSystem
    except ImportError as e:
        print(f"{Fore.RED}Error: Could not import FaceRecognitionSystem from training.py in {misc_path}")
        print(f"{Fore.RED}{e}")
        exit(1)

# Initialize colorama
init(autoreset=True)

# Configuration
DATA_FILE = str(Path(__file__).resolve().parent.parent / "data" / "data.csv")
VERSION = "1.0.0"

# Ocean-themed ASCII art with camera emphasis
IMAGE_SEARCH_LOGO = r"""
            .--.                .--.
        .-(    ).-.          .-(    ).-.
        (___.__)__)         (___.__)__)
        ∽∽∽∽∽∽∽∽∽∽         ∽∽∽∽∽∽∽∽∽∽

        ██╗███╗░░░███╗░█████╗░░██████╗░███████╗   
        ██║████╗░████║██╔══██╗██╔════╝░██╔════╝
        ██║██╔████╔██║███████║██║░░██╗░█████╗░░
        ██║██║╚██╔╝██║██╔══██║██║░░╚██╗██╔══╝░░
        ██║██║░╚═╝░██║██║░░██║╚██████╔╝███████╗
        ╚═╝╚═╝░░░░░╚═╝╚═╝░░╚═╝░╚═════╝░╚══════╝  

             Face in the Depths
                                
∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽~
"""

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_image_search_header():
    """Display the image search module header with ocean theme."""
    clear_screen()
    print(Fore.CYAN + Style.BRIGHT + IMAGE_SEARCH_LOGO)
    print(Fore.WHITE + Style.BRIGHT + f"Created by awiones")
    print(Fore.WHITE + Style.BRIGHT + f"Version: {VERSION}")
    print(Fore.BLUE + "~" * 50)
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"{Fore.CYAN}Dive Time: {Fore.WHITE}{current_time}{Fore.CYAN} | Face Scanner Active")
    print()

def scanning_animation(message="Scanning face patterns"):
    """Display a scanning animation."""
    print(f"\n{Fore.CYAN}{message}", end="", flush=True)
    frames = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    for _ in range(10):
        for frame in frames:
            print(f"\r{Fore.CYAN}{message} {frame}", end="", flush=True)
            time.sleep(0.1)
    print("\n")

def download_image(url):
    """Download image from URL to temporary file."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Create temp file with .jpg extension
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp.write(response.content)
        temp.close()
        return temp.name
    except Exception as e:
        print(f"{Fore.RED}Error downloading image: {str(e)}")
        return None

def validate_input(path_or_url):
    """Validate if the input is a valid image URL or local file path."""
    if not path_or_url:
        return False, None
    
    # Check if it's a local file
    if os.path.exists(path_or_url):
        ext = os.path.splitext(path_or_url)[1].lower()
        if ext in ('.jpg', '.jpeg', '.png', '.gif', '.bmp'):
            return True, "local"
        return False, None
    
    # Check if it's a URL
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    if (path_or_url.startswith(('http://', 'https://')) and
        any(path_or_url.lower().endswith(ext) for ext in image_extensions)):
        return True, "url"
    
    return False, None

def get_image_path(path_or_url):
    """Get the image path whether it's a URL or local file."""
    is_valid, input_type = validate_input(path_or_url)
    
    if not is_valid:
        return None
        
    if input_type == "local":
        return path_or_url
    else:  # URL
        return download_image(path_or_url)

def search_face_in_database(image_path):
    """Search for matching faces in the database using the trained system."""
    try:
        # Initialize and load the trained face database
        face_system = FaceRecognitionSystem()
        face_system.load_or_build_database()
        # Recognize faces in the input image
        results = face_system.recognize_faces(image_path)
        return results
    except Exception as e:
        print(f"{Fore.RED}Error during face search: {str(e)}")
        return []

def display_results(matches, orig_image_path=None):
    """Display search results in a formatted table and save annotated image if possible."""
    if not matches:
        print(f"\n{Fore.YELLOW}⚠ No matching faces found in the database.")
        return

    print(f"\n{Fore.CYAN}🔍 Found {Fore.WHITE}{len(matches)}{Fore.CYAN} face(s) in the image:\n")

    headers = ["Face #", "Name", "Confidence"]
    table_data = []

    for idx, match in enumerate(matches, 1):
        # Only color the percentage part
        confidence_val = f"{match['confidence']:.2%}"
        if match['confidence'] > 0.8:
            confidence_str = f"{Fore.GREEN}{confidence_val}{Style.RESET_ALL}"
        else:
            confidence_str = f"{Fore.RED}{confidence_val}{Style.RESET_ALL}"
        row = [
            f"{idx}",
            f"{match['person']}",
            confidence_str
        ]
        table_data.append(row)

    print(tabulate(table_data, headers=headers, tablefmt="pretty"))
    print(f"\n{Fore.BLUE}{'~' * 60}")

    # Save annotated image to results folder if possible
    if orig_image_path and os.path.exists(orig_image_path):
        results_dir = os.path.join(os.path.dirname(__file__), "..", "results")
        os.makedirs(results_dir, exist_ok=True)
        img = cv2.imread(orig_image_path)
        for result in matches:
            region = result.get("region")
            if not region:
                continue
            x, y, w, h = region["x"], region["y"], region["w"], region["h"]
            color = (0, 255, 0) if result["person"] != "Unknown" else (0, 0, 255)
            cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
            text = f"{result['person']} ({result['confidence']:.2f})"
            cv2.putText(img, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        result_img_path = os.path.join(results_dir, f"search_{os.path.basename(orig_image_path)}")
        cv2.imwrite(result_img_path, img)
        print(f"{Fore.GREEN}Result image saved to: {Fore.WHITE}{result_img_path}")

def run_image_search():
    """Run the image search functionality."""
    while True:
        display_image_search_header()
        
        print(f"{Fore.CYAN}Enter image URL or local file path to search")
        print(f"{Fore.CYAN}Example: /path/to/image.jpg or https://example.com/image.jpg")
        print(f"{Fore.CYAN}(Type {Fore.YELLOW}back{Fore.CYAN} to return)")
        
        image_input = input(f"{Fore.BLUE}≈≈≈>{Fore.WHITE} ").strip()
        
        if not image_input:
            continue
        if image_input.lower() == 'back':
            return
        
        is_valid, input_type = validate_input(image_input)
        if not is_valid:
            print(f"{Fore.YELLOW}Please enter a valid image path or URL")
            print(f"{Fore.YELLOW}Supported formats: .jpg, .jpeg, .png, .gif, .bmp")
            time.sleep(2)
            continue
        
        if input_type == "url":
            scanning_animation("Downloading image")
        else:
            scanning_animation("Loading image")
            
        image_path = get_image_path(image_input)
        
        if not image_path:
            print(f"{Fore.RED}Failed to process image. Please try another file or URL.")
            time.sleep(2)
            continue
        
        try:
            scanning_animation("Analyzing facial features")
            matches = search_face_in_database(image_path)
            display_results(matches, orig_image_path=image_path)
            
            # Cleanup temporary file only if it was downloaded from URL
            if input_type == "url":
                try:
                    os.unlink(image_path)
                except:
                    pass
            
            print(f"\n{Fore.CYAN}What would you like to do next?")
            print(f"{Fore.WHITE}[Enter]{Fore.CYAN}: New search  |  {Fore.WHITE}b{Fore.CYAN}: Back to main menu")
            next_action = input(f"{Fore.BLUE}≈≈≈>{Fore.WHITE} ").strip().lower()
            
            if next_action == 'b':
                return
                
        except Exception as e:
            print(f"{Fore.RED}Error during image search: {str(e)}")
            input(f"\n{Fore.CYAN}Press Enter to continue...")

if __name__ == "__main__":
    print(f"{Fore.CYAN}Running Image Search Module directly...")
    run_image_search()
    print(f"{Fore.CYAN}Search completed. Returning to shore.")
