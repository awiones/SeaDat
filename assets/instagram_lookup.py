import requests
import re
import json
import time
import random
import os
import sys
from colorama import init, Fore, Style

init(autoreset=True)

INSTAGRAM_LOGO = r"""
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

# Maximum number of retries for a request
MAX_RETRIES = 3
# Delay between retries (in seconds)
RETRY_DELAY = [2, 5, 10]  # Progressive backoff

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header():
    clear_screen()
    print(Fore.MAGENTA + Style.BRIGHT + INSTAGRAM_LOGO)
    print(Fore.WHITE + Style.BRIGHT + "Instagram Profile Lookup")
    print(Fore.BLUE + "~" * 50)

def get_random_user_agent():
    """Return a random user agent to help avoid detection."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0"
    ]
    return random.choice(user_agents)

def get_proxies():
    """
    Return a list of proxies if available.
    You can implement your own proxy rotation logic here.
    """
    # Example: return a list of proxies if you have them
    # Format: {"http": "http://user:pass@host:port", "https": "https://user:pass@host:port"}
    return None

def make_request(session, url, headers=None, params=None, proxies=None, retry_count=0):
    """Make a request with retry logic and proxy support."""
    if headers is None:
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.instagram.com/",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }
    
    try:
        # Add a random delay to mimic human behavior
        time.sleep(random.uniform(1, 3))
        
        # Use proxy if provided
        current_proxies = proxies[retry_count % len(proxies)] if proxies else None
        
        resp = session.get(
            url, 
            headers=headers, 
            params=params, 
            proxies=current_proxies,
            timeout=15
        )
        
        # Check for rate limiting or blocking
        if resp.status_code in [429, 403, 401, 201]:
            if retry_count < MAX_RETRIES:
                # Wait with exponential backoff
                delay = RETRY_DELAY[min(retry_count, len(RETRY_DELAY)-1)]
                time.sleep(delay)
                # Try again with a different user agent
                headers["User-Agent"] = get_random_user_agent()
                return make_request(session, url, headers, params, proxies, retry_count + 1)
            else:
                return {
                    "error": f"HTTP {resp.status_code}: Instagram is rate limiting or blocking requests. Try again later or use a VPN."
                }
        
        return resp
    except requests.RequestException as e:
        if retry_count < MAX_RETRIES:
            # Wait with exponential backoff
            delay = RETRY_DELAY[min(retry_count, len(RETRY_DELAY)-1)]
            time.sleep(delay)
            return make_request(session, url, headers, params, proxies, retry_count + 1)
        else:
            return {"error": f"Request failed after {MAX_RETRIES} retries: {str(e)}"}

def fetch_instagram_profile(username):
    """
    Fetch Instagram profile data using multiple methods.
    Returns dict with profile info or error.
    """
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Get proxies if available
    proxies = get_proxies()
    
    # Try multiple methods to get profile data
    methods = [
        ("API endpoint", fetch_via_api_endpoint),
        ("HTML scraping", fetch_via_html_scraping),
        ("GraphQL API", fetch_via_graphql),
        ("Mobile API", fetch_via_mobile_api),
        ("Web API", fetch_via_web_api)
    ]
    
    errors = []
    for method_name, method_func in methods:
        print(Fore.CYAN + f"Trying method: {method_name}...")
        profile_data = method_func(username, session, proxies)
        
        if "error" not in profile_data:
            print(Fore.GREEN + f"Success with method: {method_name}")
            return profile_data
        
        errors.append(f"{method_name}: {profile_data['error']}")
        print(Fore.YELLOW + f"Method failed: {profile_data['error']}")
    
    # If all methods fail, return a comprehensive error
    return {
        "error": "All methods failed to retrieve profile data",
        "details": errors
    }

def fetch_via_api_endpoint(username, session, proxies=None):
    """Try fetching profile using the API endpoint."""
    url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.instagram.com/",
        "X-IG-App-ID": "936619743392459",
        "X-Requested-With": "XMLHttpRequest",
        "DNT": "1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    
    resp = make_request(session, url, headers, proxies=proxies)
    
    if isinstance(resp, dict) and "error" in resp:
        return resp
    
    if resp.status_code == 404:
        return {"error": "User not found"}
    
    if resp.status_code != 200:
        return {
            "error": f"HTTP {resp.status_code}: Unable to fetch profile via API endpoint."
        }
    
    try:
        data = resp.json()
        return extract_user_data(data)
    except Exception as e:
        return {"error": f"Could not parse API response: {str(e)}"}

def fetch_via_html_scraping(username, session, proxies=None):
    """Try fetching profile by scraping the HTML page."""
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.instagram.com/",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }
    
    resp = make_request(session, url, headers, proxies=proxies)
    
    if isinstance(resp, dict) and "error" in resp:
        return resp
    
    if resp.status_code == 404:
        return {"error": "User not found"}
    
    if resp.status_code != 200:
        return {
            "error": f"HTTP {resp.status_code}: Unable to fetch profile via HTML scraping."
        }
    
    # Try multiple patterns to extract data from HTML
    data_patterns = [
        # Shared data pattern
        (r'window\._sharedData\s*=\s*(\{.*?\});</script>', lambda m: json.loads(m)),
        # Additional data pattern
        (r'window\.__additionalDataLoaded\s*\(\s*[\'"]user[\'"]\s*,\s*(\{.*?\})\);</script>', lambda m: json.loads(m)),
        # React shared data pattern
        (r'<script type="application/json" data-hypernova-id=".*?">(.*?)</script>', lambda m: json.loads(m)),
        # Profile page container pattern
        (r'"ProfilePage":\[{"logging_page_id":"profilePage_([0-9]+)"', lambda m: {"user_id": m}),
    ]
    
    for pattern, parser in data_patterns:
        matches = re.search(pattern, resp.text)
        if matches:
            try:
                data = parser(matches.group(1))
                
                # Navigate to user data based on the pattern
                if "entry_data" in data and "ProfilePage" in data["entry_data"] and data["entry_data"]["ProfilePage"]:
                    user_data = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
                    return extract_user_data({"graphql": {"user": user_data}})
                elif "user" in data:
                    return extract_user_data(data)
                elif "user_id" in data:
                    # We found the user ID, but not the full data
                    # This can be used by the GraphQL method
                    return {"user_id": data["user_id"], "error": "Only user ID found, not full profile data"}
            except Exception as e:
                continue
    
    # If we couldn't extract data using any pattern
    return {"error": "Could not extract profile data from HTML"}

def fetch_via_graphql(username, session, proxies=None):
    """Try fetching profile using the GraphQL API."""
    # First, we need to get the user ID
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    resp = make_request(session, url, headers, proxies=proxies)
    
    if isinstance(resp, dict) and "error" in resp:
        return resp
    
    # Try to extract user ID from the response
    user_id = None
    user_id_patterns = [
        r'"profilePage_([0-9]+)"',
        r'"user":{"id":"([0-9]+)"',
        r'"owner":{"id":"([0-9]+)"',
        r'"instagram://user\?username=.*?&id=([0-9]+)"'
    ]
    
    for pattern in user_id_patterns:
        match = re.search(pattern, resp.text)
        if match:
            user_id = match.group(1)
            break
    
    if not user_id:
        return {"error": "Could not find user ID for GraphQL query"}
    
    # Now use the user ID to make a GraphQL query
    graphql_url = "https://www.instagram.com/graphql/query/"
    
    # Try multiple query hashes (these change periodically)
    query_hashes = [
        "d4d88dc1500312af6f937f7b804c68c3",
        "c9100bf9110dd6361671f113dd02e7d6",
        "7c16654f22c819fb63d1183034a5162f",
        "69cba1cc2991d4223954a05ddf2f7e32",
        "bfa387b2992c3a52dcbe447467b4b771"
    ]
    
    for query_hash in query_hashes:
        graphql_headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-IG-App-ID": "936619743392459",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"https://www.instagram.com/{username}/",
        }
        
        variables = json.dumps({
            "user_id": user_id,
            "include_reel": True,
            "include_chaining": True,
            "include_suggested_users": False,
            "include_logged_out_extras": False,
            "include_highlight_reels": True,
        })
        
        params = {
            "query_hash": query_hash,
            "variables": variables
        }
        
        graphql_resp = make_request(session, graphql_url, graphql_headers, params, proxies=proxies)
        
        if isinstance(graphql_resp, dict) and "error" in graphql_resp:
            continue
        
        if graphql_resp.status_code != 200:
            continue
        
        try:
            data = graphql_resp.json()
            if "data" in data and "user" in data["data"]:
                return extract_user_data({"data": data["data"]})
        except Exception:
            continue
    
    return {"error": "Could not retrieve user data via GraphQL API"}

def fetch_via_mobile_api(username, session, proxies=None):
    """Try fetching profile using the mobile API."""
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    
    headers = {
        "User-Agent": "Instagram 219.0.0.12.117 Android",
        "Accept": "application/json",
        "Accept-Language": "en-US",
        "Accept-Encoding": "gzip, deflate, br",
        "X-IG-App-ID": "936619743392459",
        "X-IG-WWW-Claim": "0",
        "Origin": "https://www.instagram.com",
        "Connection": "keep-alive",
        "Referer": "https://www.instagram.com/",
    }
    
    resp = make_request(session, url, headers, proxies=proxies)
    
    if isinstance(resp, dict) and "error" in resp:
        return resp
    
    if resp.status_code == 404:
        return {"error": "User not found"}
    
    if resp.status_code != 200:
        return {
            "error": f"HTTP {resp.status_code}: Unable to fetch profile via mobile API."
        }
    
    try:
        data = resp.json()
        if "data" in data and "user" in data["data"]:
            return extract_user_data(data)
        return {"error": "Could not find user data in mobile API response"}
    except Exception as e:
        return {"error": f"Could not parse mobile API response: {str(e)}"}

def fetch_via_web_api(username, session, proxies=None):
    """Try fetching profile using the web API with different parameters."""
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "X-IG-App-ID": "936619743392459",
        "X-ASBD-ID": "129477",
        "X-IG-WWW-Claim": "0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    
    resp = make_request(session, url, headers, proxies=proxies)
    
    if isinstance(resp, dict) and "error" in resp:
        return resp
    
    if resp.status_code == 404:
        return {"error": "User not found"}
    
    if resp.status_code != 200:
        return {
            "error": f"HTTP {resp.status_code}: Unable to fetch profile via web API."
        }
    
    try:
        data = resp.json()
        if "data" in data and "user" in data["data"]:
            return extract_user_data(data)
        return {"error": "Could not find user data in web API response"}
    except Exception as e:
        return {"error": f"Could not parse web API response: {str(e)}"}

def extract_user_data(data):
    """Extract user data from various response formats."""
    user = None
    
    # Try different paths where user data might be located
    if "graphql" in data and "user" in data["graphql"]:
        user = data["graphql"]["user"]
    elif "user" in data:
        user = data["user"]
    elif "data" in data and "user" in data["data"]:
        user = data["data"]["user"]
    elif "users" in data and data["users"] and len(data["users"]) > 0:
        user = data["users"][0]["user"] if "user" in data["users"][0] else data["users"][0]
    
    if not user:
        return {"error": "Could not find user info in Instagram response"}
    
    # Extract fields with fallbacks for different API formats
    result = {
        "username": user.get("username"),
        "id": user.get("id") or user.get("pk") or user.get("user_id"),
        "full_name": user.get("full_name"),
        "bio": user.get("biography") or user.get("bio"),
        "url": user.get("external_url") or user.get("url"),
        "is_private": user.get("is_private"),
        "is_verified": user.get("is_verified"),
        "is_business": user.get("is_business_account") or user.get("is_business"),
        "profile_pic_url": user.get("profile_pic_url_hd") or user.get("profile_pic_url"),
    }
    
    # Handle different formats for counts
    if "edge_owner_to_timeline_media" in user:
        result["total_posts"] = user["edge_owner_to_timeline_media"]["count"]
    elif "media_count" in user:
        result["total_posts"] = user["media_count"]
    elif "post_count" in user:
        result["total_posts"] = user["post_count"]
    
    if "edge_followed_by" in user:
        result["total_followers"] = user["edge_followed_by"]["count"]
    elif "follower_count" in user:
        result["total_followers"] = user["follower_count"]
    elif "followers" in user:
        result["total_followers"] = user["followers"]
    
    if "edge_follow" in user:
        result["total_following"] = user["edge_follow"]["count"]
    elif "following_count" in user:
        result["total_following"] = user["following_count"]
    elif "following" in user:
        result["total_following"] = user["following"]
    
    return result

def run_instagram_lookup():
    while True:
        display_header()
        print(Fore.CYAN + "Enter Instagram username (without @), or type 'back' to return:")
        username = input(Fore.BLUE + "≈≈≈> " + Fore.WHITE).strip()
        if not username:
            continue
        if username.lower() == 'back':
            return
        
        print(Fore.CYAN + "🌊 Looking up Instagram profile, please wait...")
        info = fetch_instagram_profile(username)
        print()
        
        if "error" in info:
            print(Fore.RED + f"Error: {info['error']}")
            if "details" in info:
                print(Fore.YELLOW + "\nDetailed errors:")
                for i, error in enumerate(info["details"], 1):
                    print(Fore.YELLOW + f"{i}. {error}")
            
            print(Fore.YELLOW + "\nTroubleshooting tips:")
            print(Fore.YELLOW + "1. Try again in a few minutes (Instagram may be rate-limiting)")
            print(Fore.YELLOW + "2. Check if the username is correct")
            print(Fore.YELLOW + "3. Try using a VPN or different network")
            print(Fore.YELLOW + "4. Instagram may be blocking automated requests")
            print(Fore.YELLOW + "5. Consider adding proxies to the script")
        else:
            print(Fore.WHITE + f"Username: {Fore.YELLOW}{info.get('username')}")
            print(Fore.WHITE + f"ID: {Fore.YELLOW}{info.get('id')}")
            print(Fore.WHITE + f"Name: {Fore.YELLOW}{info.get('full_name')}")
            print(Fore.WHITE + f"Bio: {Fore.YELLOW}{info.get('bio')}")
            print(Fore.WHITE + f"URL: {Fore.YELLOW}{info.get('url')}")
            print(Fore.WHITE + f"Total Posts: {Fore.YELLOW}{info.get('total_posts')}")
            print(Fore.WHITE + f"Followers: {Fore.YELLOW}{info.get('total_followers')}")
            print(Fore.WHITE + f"Following: {Fore.YELLOW}{info.get('total_following')}")
            print(Fore.WHITE + f"Private: {Fore.YELLOW}{info.get('is_private')}")
            print(Fore.WHITE + f"Verified: {Fore.YELLOW}{info.get('is_verified')}")
            print(Fore.WHITE + f"Business: {Fore.YELLOW}{info.get('is_business')}")
            print(Fore.WHITE + f"Profile Picture: {Fore.YELLOW}{info.get('profile_pic_url')}")
        
        print(Fore.BLUE + "~" * 50)
        next_action = input(Fore.CYAN + "\n[Enter] Lookup another | b: Back to menu\n" + Fore.BLUE + "≈≈≈> " + Fore.WHITE).strip().lower()
        if next_action == 'b':
            return

if __name__ == "__main__":
    run_instagram_lookup()