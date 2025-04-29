import os
import sys
import time
import socket
import re
import json
import platform
from datetime import datetime
import requests
from requests.exceptions import RequestException, Timeout
from colorama import init, Fore, Style, Back

# Initialize colorama with autoreset
init(autoreset=True)

# ASCII art logo
IP_TRACK_LOGO = r"""
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

# API endpoints for IP information
API_SERVICES = {
    "ipinfo": "https://ipinfo.io/{ip}/json",
    "ip-api": "http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,mobile,proxy,hosting",
    "ipgeolocation": "https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={ip}"
}

# Configuration
CONFIG = {
    "api_keys": {
        "ipgeolocation": ""  # Add your API key here if you have one
    },
    "timeout": 10,
    "save_history": True,
    "history_file": "ip_track_history.json",
    "default_service": "ipinfo"
}

def clear_screen():
    """Clear the terminal screen based on the operating system."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header():
    """Display the application header with logo and version info."""
    clear_screen()
    print(Fore.CYAN + Style.BRIGHT + IP_TRACK_LOGO)
    print(Fore.WHITE + Style.BRIGHT + "Advanced IP Address Tracker v1.2")
    print(Fore.BLUE + "~" * 60)
    print(Fore.CYAN + f"System: {platform.system()} {platform.release()} | Python: {platform.python_version()}")
    print(Fore.BLUE + "~" * 60)

def loading_animation(message, duration=1.5):
    """Display a simple loading animation."""
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    end_time = time.time() + duration
    i = 0
    
    print()
    while time.time() < end_time:
        sys.stdout.write(f"\r{Fore.CYAN}{chars[i % len(chars)]} {message}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    print()

def is_valid_ip(ip):
    """Check if the given string is a valid IPv4 or IPv6 address."""
    try:
        socket.inet_pton(socket.AF_INET, ip)
        return True
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET6, ip)
            return True
        except socket.error:
            return False

def is_domain(domain):
    """Check if the given string is potentially a valid domain name."""
    domain_pattern = re.compile(
        r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'
    )
    return bool(domain_pattern.match(domain.lower()))

def resolve_domain_to_ip(domain):
    """Resolve a domain name to an IP address."""
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None

def fetch_ip_info(ip, service="ipinfo"):
    """Fetch IP information from the specified service."""
    try:
        if service not in API_SERVICES:
            service = CONFIG["default_service"]
            
        url = API_SERVICES[service].format(
            ip=ip, 
            api_key=CONFIG["api_keys"].get(service, "")
        )
        
        headers = {
            "User-Agent": "IP-Tracker/1.2 (https://github.com/username/ip-tracker)"
        }
        
        response = requests.get(url, headers=headers, timeout=CONFIG["timeout"])
        
        if response.status_code == 200:
            return {
                "success": True,
                "service": service,
                "data": response.json(),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "service": service,
                "error": f"HTTP Error: {response.status_code}",
                "message": response.text
            }
    except Timeout:
        return {"success": False, "error": "Request timed out", "service": service}
    except RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}", "service": service}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}", "service": service}

def save_to_history(ip, result):
    """Save the IP lookup result to history file."""
    if not CONFIG["save_history"]:
        return
        
    history_data = []
    try:
        if os.path.exists(CONFIG["history_file"]):
            with open(CONFIG["history_file"], "r") as f:
                history_data = json.load(f)
    except Exception:
        pass
        
    # Add new entry
    entry = {
        "ip": ip,
        "timestamp": datetime.now().isoformat(),
        "result": result
    }
    
    # Limit history to 100 entries
    history_data = [entry] + history_data[:99]
    
    try:
        with open(CONFIG["history_file"], "w") as f:
            json.dump(history_data, f, indent=2)
    except Exception as e:
        print(f"Error saving history: {str(e)}")

def get_history():
    """Retrieve IP lookup history."""
    try:
        if os.path.exists(CONFIG["history_file"]):
            with open(CONFIG["history_file"], "r") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def format_location_info(data):
    """Format location information for display."""
    if not data.get("success", False):
        return "Location information unavailable"
    
    data = data["data"]
    location_parts = []
    
    # Format based on which API was used
    if "city" in data:
        location_parts.append(data["city"])
    if "region" in data:
        location_parts.append(data["region"])
    if "country" in data:
        location_parts.append(data["country"])
    
    return ", ".join(filter(None, location_parts))

def format_whois_info(ip):
    """
    Get WHOIS information for the IP address.
    This is a simplified version - in a real implementation,
    you might use a library like ipwhois or python-whois.
    """
    try:
        # This is just a placeholder - in a real implementation
        # you would implement proper WHOIS lookup
        whois_data = {
            "message": f"WHOIS data for {ip} is not implemented in this version. Consider using the python-whois library for full functionality."
        }
        return whois_data
    except Exception as e:
        return {"error": str(e)}

def display_ip_info(ip, info):
    """Display the IP information in a well-formatted manner."""
    if not info.get("success", False):
        print(f"\n{Fore.RED}⚠️  Error retrieving information: {info.get('error', 'Unknown error')}")
        return
    
    data = info["data"]
    service = info["service"]
    
    print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} IP Information: {ip} {Style.RESET_ALL}")
    print(Fore.BLUE + "─" * 60)
    
    # Basic information
    print(f"{Fore.WHITE}{Style.BRIGHT}📌 Basic Information{Style.RESET_ALL}")
    
    if "hostname" in data:
        print(f"{Fore.CYAN}Hostname:{Fore.YELLOW} {data.get('hostname', 'N/A')}")
    
    if "org" in data:
        print(f"{Fore.CYAN}Organization:{Fore.YELLOW} {data.get('org', 'N/A')}")
    
    if "isp" in data:
        print(f"{Fore.CYAN}ISP:{Fore.YELLOW} {data.get('isp', 'N/A')}")
    
    if "asn" in data or "as" in data:
        print(f"{Fore.CYAN}ASN:{Fore.YELLOW} {data.get('asn', data.get('as', 'N/A'))}")
    
    # Location information
    print(f"\n{Fore.WHITE}{Style.BRIGHT}🌎 Location Information{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}Location:{Fore.YELLOW} {format_location_info(info)}")
    
    if "loc" in data:
        print(f"{Fore.CYAN}Coordinates:{Fore.YELLOW} {data.get('loc', 'N/A')}")
    elif "lat" in data and "lon" in data:
        print(f"{Fore.CYAN}Coordinates:{Fore.YELLOW} {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}")
    
    if "postal" in data or "zip" in data:
        print(f"{Fore.CYAN}Postal/ZIP:{Fore.YELLOW} {data.get('postal', data.get('zip', 'N/A'))}")
    
    if "timezone" in data:
        print(f"{Fore.CYAN}Timezone:{Fore.YELLOW} {data.get('timezone', 'N/A')}")
    
    # Network information
    if any(key in data for key in ["mobile", "proxy", "hosting"]):
        print(f"\n{Fore.WHITE}{Style.BRIGHT}🔒 Network Classification{Style.RESET_ALL}")
        
        if "mobile" in data:
            print(f"{Fore.CYAN}Mobile Network:{Fore.YELLOW} {'Yes' if data.get('mobile') else 'No'}")
        
        if "proxy" in data:
            proxy_status = data.get('proxy')
            if proxy_status:
                print(f"{Fore.CYAN}Proxy/VPN:{Fore.RED} Yes (This IP appears to be a proxy or VPN)")
            else:
                print(f"{Fore.CYAN}Proxy/VPN:{Fore.GREEN} No")
        
        if "hosting" in data:
            print(f"{Fore.CYAN}Hosting/Data Center:{Fore.YELLOW} {'Yes' if data.get('hosting') else 'No'}")
    
    # Source information
    print(f"\n{Fore.WHITE}{Style.BRIGHT}ℹ️  Source Information{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Data Source:{Fore.YELLOW} {service}")
    print(f"{Fore.CYAN}Retrieved:{Fore.YELLOW} {info.get('timestamp', 'N/A')}")
    
    print(Fore.BLUE + "─" * 60)

def run_ping_test(ip, count=4):
    """Run a simple ping test to the IP address."""
    print(f"\n{Fore.WHITE}{Style.BRIGHT}📡 Running ping test to {ip}...{Style.RESET_ALL}")
    
    ping_command = "ping"
    count_param = "-n" if os.name == 'nt' else "-c"
    
    try:
        result = os.popen(f"{ping_command} {count_param} {count} {ip}").read()
        print(f"\n{Fore.CYAN}{result}")
    except Exception as e:
        print(f"\n{Fore.RED}Error running ping test: {str(e)}")

def run_traceroute(ip):
    """Run a traceroute to the IP address."""
    print(f"\n{Fore.WHITE}{Style.BRIGHT}🔍 Running traceroute to {ip}...{Style.RESET_ALL}")
    
    traceroute_command = "tracert" if os.name == 'nt' else "traceroute"
    
    try:
        result = os.popen(f"{traceroute_command} {ip}").read()
        print(f"\n{Fore.CYAN}{result}")
    except Exception as e:
        print(f"\n{Fore.RED}Error running traceroute: {str(e)}")

def show_help():
    """Display help information."""
    display_header()
    print(f"{Fore.WHITE}{Style.BRIGHT}📚 IP Tracker Help{Style.RESET_ALL}")
    print(Fore.BLUE + "─" * 60)
    print(f"{Fore.CYAN}Commands:{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}IP Address{Fore.WHITE}: Enter an IPv4 or IPv6 address to track")
    print(f"  {Fore.YELLOW}Domain Name{Fore.WHITE}: Enter a domain name to resolve and track")
    print(f"  {Fore.YELLOW}help{Fore.WHITE}: Show this help information")
    print(f"  {Fore.YELLOW}history{Fore.WHITE}: View your IP tracking history")
    print(f"  {Fore.YELLOW}clear{Fore.WHITE}: Clear the screen")
    print(f"  {Fore.YELLOW}my ip{Fore.WHITE}: Track your own public IP address")
    print(f"  {Fore.YELLOW}exit/quit/back{Fore.WHITE}: Exit the program")
    print()
    print(f"{Fore.CYAN}After tracking an IP, you can use these additional commands:{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}p{Fore.WHITE}: Run a ping test to the IP address")
    print(f"  {Fore.YELLOW}t{Fore.WHITE}: Run a traceroute to the IP address")
    print(f"  {Fore.YELLOW}w{Fore.WHITE}: Get WHOIS information for the IP")
    print(Fore.BLUE + "─" * 60)
    input(f"{Fore.GREEN}Press Enter to continue...")

def show_history():
    """Display IP tracking history."""
    display_header()
    print(f"{Fore.WHITE}{Style.BRIGHT}📜 IP Tracking History{Style.RESET_ALL}")
    print(Fore.BLUE + "─" * 60)
    
    history = get_history()
    
    if not history:
        print(f"{Fore.YELLOW}No tracking history found.")
    else:
        print(f"{Fore.CYAN}{'#':2} {'IP Address':15} {'Date':19} {'Location'}")
        print(Fore.BLUE + "─" * 60)
        
        for i, entry in enumerate(history[:15]):  # Show only the most recent 15
            ip = entry["ip"]
            timestamp = entry["timestamp"][:19]  # Truncate milliseconds
            location = format_location_info(entry["result"])
            print(f"{Fore.WHITE}{i+1:2} {Fore.YELLOW}{ip:15} {Fore.CYAN}{timestamp} {Fore.GREEN}{location}")
    
    print(Fore.BLUE + "─" * 60)
    
    while True:
        choice = input(f"{Fore.CYAN}Enter number to view details, or press Enter to return: {Fore.WHITE}").strip()
        
        if not choice:
            break
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(history):
                entry = history[index]
                display_ip_info(entry["ip"], entry["result"])
                input(f"\n{Fore.GREEN}Press Enter to continue...")
                break
            else:
                print(f"{Fore.RED}Invalid selection.")
        except ValueError:
            print(f"{Fore.RED}Please enter a valid number.")

def get_own_ip():
    """Get the user's own public IP address."""
    loading_animation("Detecting your public IP address...")
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        if response.status_code == 200:
            return response.json()["ip"]
        else:
            return None
    except Exception:
        return None

def run_ip_track():
    """Main IP tracking function."""
    while True:
        display_header()
        
        print(f"{Fore.CYAN}Enter an IP address or domain to track:")
        print(f"{Fore.CYAN}(or type 'help', 'history', 'my ip', 'clear', or 'exit')")
        
        user_input = input(f"{Fore.BLUE}≈≈≈> {Fore.WHITE}").strip()
        
        if not user_input:
            continue
            
        user_input_lower = user_input.lower()
        
        # Handle special commands
        if user_input_lower in ['exit', 'quit', 'back']:
            print(f"{Fore.GREEN}Exiting IP Tracker. Goodbye!")
            time.sleep(1)
            return
        elif user_input_lower == 'help':
            show_help()
            continue
        elif user_input_lower == 'history':
            show_history()
            continue
        elif user_input_lower == 'clear':
            continue  # Just refresh the screen
        elif user_input_lower == 'my ip':
            ip = get_own_ip()
            if not ip:
                print(f"{Fore.RED}Unable to detect your public IP address.")
                input(f"{Fore.GREEN}Press Enter to continue...")
                continue
            print(f"{Fore.GREEN}Your public IP address: {ip}")
            user_input = ip  # Track this IP
        
        # Check if input is domain and resolve it
        elif is_domain(user_input):
            loading_animation(f"Resolving domain {user_input} to IP...")
            ip = resolve_domain_to_ip(user_input)
            if not ip:
                print(f"{Fore.RED}Unable to resolve domain {user_input} to an IP address.")
                input(f"{Fore.GREEN}Press Enter to continue...")
                continue
            print(f"{Fore.GREEN}Domain {user_input} resolved to IP: {ip}")
            user_input = ip  # Track the resolved IP
        
        # Validate IP address
        elif not is_valid_ip(user_input):
            print(f"{Fore.RED}Invalid IP address format.")
            input(f"{Fore.GREEN}Press Enter to continue...")
            continue
        
        # Fetch IP information
        loading_animation(f"Tracking IP address {user_input}, please wait...")
        info = fetch_ip_info(user_input)
        
        # Save to history if successful
        if info.get("success", False):
            save_to_history(user_input, info)
        
        # Display information
        display_ip_info(user_input, info)
        
        # Additional actions menu
        while True:
            next_action = input(f"\n{Fore.CYAN}Commands: [Enter]: Track another | p: Ping | t: Traceroute | w: WHOIS | b: Back\n{Fore.BLUE}≈≈≈> {Fore.WHITE}").strip().lower()
            
            if not next_action:
                break
            elif next_action == 'p':
                run_ping_test(user_input)
            elif next_action == 't':
                run_traceroute(user_input)
            elif next_action == 'w':
                whois_info = format_whois_info(user_input)
                if "error" in whois_info:
                    print(f"\n{Fore.RED}Error retrieving WHOIS information: {whois_info['error']}")
                else:
                    print(f"\n{Fore.CYAN}WHOIS Information: {whois_info.get('message', 'Not available')}")
            elif next_action == 'b':
                break

if __name__ == "__main__":
    try:
        run_ip_track()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Program interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n{Fore.RED}An unexpected error occurred: {str(e)}")
    finally:
        print(f"\n{Fore.GREEN}Thank you for using IP Tracker!")
        time.sleep(1)