import os
import csv
import time
import re
import json
import difflib
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from colorama import init, Fore, Back, Style
from tabulate import tabulate

# Import OpenAI client
try:
    from openai import OpenAI
except ImportError:
    # For type checkers and editors: openai must be installed in your environment
    pass

# Import from existing search module to reuse functionality
from .search import clear_screen, search_by_name, search_by_multiple_fields, highlight_match

# Initialize colorama for cross-platform colored terminal
init(autoreset=True)

# Load environment variables
load_dotenv()

# Configuration
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "data.csv")
API_KEY = os.getenv('AIMLAPI_KEY')
API_BASE_URL = "https://api.aimlapi.com/v1"

VERSION = "3.0.0"

# Initialize OpenAI client
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY,
)

# Ocean-themed ASCII art with AI emphasis
AI_SEARCH_LOGO = r"""
            .--.                .--.
        .-(    ).-.          .-(    ).-.
        (___.__)__)         (___.__)__)
        ∽∽∽∽∽∽∽∽∽∽         ∽∽∽∽∽∽∽∽∽∽

░█████╗░██╗  ░██████╗███████╗░█████╗░██████╗░░█████╗░████████╗
██╔══██╗██║  ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝
███████║██║  ╚█████╗░█████╗░░███████║██║░░██║███████║░░░██║░░░
██╔══██║██║  ░╚═══██╗██╔══╝░░██╔══██║██║░░██║██╔══██║░░░██║░░░
██║░░██║██║  ██████╔╝███████╗██║░░██║██████╔╝██║░░██║░░░██║░░░
╚═╝░░╚═╝╚═╝  ╚═════╝░╚══════╝╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░

                  Intelligent Sea of Data
                                
∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽∽~
"""

def display_ai_search_header():
    """Display the AI search module header with ocean theme."""
    clear_screen()
    print(Fore.CYAN + Style.BRIGHT + AI_SEARCH_LOGO)
    print(Fore.WHITE + Style.BRIGHT + f"Created by awiones")
    print(Fore.WHITE + Style.BRIGHT + f"Version: {VERSION}")
    print(Fore.MAGENTA + Style.BRIGHT + "SeaDat AI powered by GPT-4o")
    print(Fore.BLUE + "~" * 50)
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"{Fore.CYAN}Dive Time: {Fore.WHITE}{current_time}{Fore.CYAN} | AI Sonar Active")
    print()

def ai_search_animation(message="AI analyzing your query"):
    """Display a minimal AI-themed scanning animation (reduced for speed)."""
    print(f"\n{Fore.CYAN}{message}...", flush=True)
    time.sleep(0.3)  # Much shorter, just a hint of activity

def call_openai_api(prompt, max_tokens=150):
    """
    Call the OpenAI API through aimlapi.com to process the search query.
    
    Args:
        prompt (str): The prompt to send to the API
        max_tokens (int): Maximum number of tokens in the response
        
    Returns:
        dict: The API response or None if there was an error
    """
    if not API_KEY:
        print(f"{Fore.RED}ERROR: API key not found in environment variables.")
        return None

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI assistant helping with employee data search."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.3
        )
        # Convert OpenAI object to dict-like for compatibility
        return {
            "choices": [
                {
                    "message": {
                        "content": response.choices[0].message.content
                    }
                }
            ]
        }
    except Exception as e:
        print(f"{Fore.RED}API Error: {str(e)}")
        return None

def analyze_search_intent(query):
    """
    Use OpenAI to analyze the user's search intent and extract search parameters.
    
    Args:
        query (str): The user's search query
        
    Returns:
        dict: A dictionary containing the analyzed search parameters
    """
    prompt = f"""
    Analyze this employee search query: "{query}"
    
    Extract the following information:
    1. What fields should be searched (name, NIK, phone, address, or all fields)?
    2. What is the main search term?
    3. Are there any specific filters or conditions?
    4. Is this likely looking for a specific person or a general search?
    
    Format your response as a JSON object with these keys: 
    search_fields, search_term, filters, is_specific_person
    """
    
    ai_search_animation("AI analyzing your search intent")
    
    response = call_openai_api(prompt)
    if not response or "choices" not in response:
        # Fallback to basic search if API fails
        return {
            "search_fields": ["Name"],
            "search_term": query,
            "filters": [],
            "is_specific_person": False
        }
    
    try:
        # Extract the JSON from the response text
        response_text = response["choices"][0]["message"]["content"]
        # Find JSON in the response (it might be embedded in other text)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            # If no JSON found, create a basic structure
            return {
                "search_fields": ["Name"],
                "search_term": query,
                "filters": [],
                "is_specific_person": False
            }
    except (json.JSONDecodeError, KeyError) as e:
        print(f"{Fore.YELLOW}Warning: Could not parse AI response. Using basic search instead.")
        return {
            "search_fields": ["Name"],
            "search_term": query,
            "filters": [],
            "is_specific_person": False
        }

def evaluate_search_results(query, results, top_n=5):
    """
    Use OpenAI to evaluate if the search results match what the user was looking for.
    
    Args:
        query (str): The user's search query
        results (list): The search results
        top_n (int): Number of top results to evaluate
        
    Returns:
        dict: Evaluation results including relevance scores and suggestions
    """
    if not results:
        return {
            "relevant": False,
            "message": "No results found.",
            "suggestions": ["Try a broader search term", "Check for typos", "Search in all fields"]
        }
    
    # Limit to top N results for API efficiency
    top_results = results[:top_n]
    
    # Format results for the API
    results_text = "\n".join([
        f"Name: {r.get('Name', 'N/A')}, NIK: {r.get('NIK', 'N/A')}, "
        f"Phone: {r.get('Phone Number', 'N/A')}, Address: {r.get('Address', 'N/A')}"
        for r in top_results
    ])
    
    prompt = f"""
    A user searched for: "{query}"
    
    Here are the top {len(top_results)} results:
    {results_text}
    
    Evaluate if these results likely match what the user was looking for.
    Consider:
    1. Do the results contain relevant information based on the query?
    2. Is there a clear best match among the results?
    3. What suggestions would help the user refine their search?
    
    Format your response as a JSON object with these keys:
    relevant (boolean), message (string), best_match_index (integer or null), suggestions (array of strings)
    """
    
    ai_search_animation("AI evaluating search results")
    
    response = call_openai_api(prompt, max_tokens=250)
    if not response or "choices" not in response:
        # Fallback if API fails
        return {
            "relevant": True,
            "message": "Results found, but relevance could not be determined.",
            "suggestions": ["Try refining your search if these aren't what you're looking for"]
        }
    
    try:
        # Extract the JSON from the response text
        response_text = response["choices"][0]["message"]["content"]
        # Find JSON in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            # If no JSON found, create a basic structure
            return {
                "relevant": True,
                "message": "Results found, but relevance could not be determined.",
                "suggestions": ["Try refining your search if these aren't what you're looking for"]
            }
    except (json.JSONDecodeError, KeyError) as e:
        print(f"{Fore.YELLOW}Warning: Could not parse AI evaluation. Assuming results are relevant.")
        return {
            "relevant": True,
            "message": "Results found, but relevance could not be determined.",
            "suggestions": ["Try refining your search if these aren't what you're looking for"]
        }

def sort_by_name_similarity(results, search_term):
    """
    Sort results so that names most similar to the search term come first.
    Priority: exact match > startswith > contains > others.
    """
    def similarity_score(record):
        name = record.get('Name', '').lower()
        st = search_term.lower()
        if name == st:
            return 0
        elif name.startswith(st):
            return 1
        elif st in name:
            return 2
        else:
            return 3
    return sorted(results, key=similarity_score)

def find_closest_matches(search_term, all_names, n=3, cutoff=0.7):
    """
    Find the closest matches to the search_term from all_names using difflib.
    Returns a list of closest names.
    """
    return difflib.get_close_matches(search_term, all_names, n=n, cutoff=cutoff)

def ensure_api_key():
    """
    Ensure the AIMLAPI_KEY is set in the environment.
    If not, prompt the user to enter it and save to .env.
    """
    global API_KEY, client
    if not API_KEY or len(API_KEY.strip()) < 10:
        print(f"{Fore.YELLOW}To use AI Search, you need an API key from https://aimlapi.com/app/keys")
        api_key = ""
        while len(api_key) < 10:
            api_key = input(f"{Fore.CYAN}Paste your AIMLAPI_KEY here: {Fore.WHITE}").strip()
            if len(api_key) < 10:
                print(f"{Fore.RED}That doesn't look like a valid API key. Please try again.")
        # Save to .env in project root
        env_path = Path(__file__).resolve().parent.parent / ".env"
        # Create .env if not exists and update/add the key
        lines = []
        if env_path.exists():
            with open(env_path, "r") as f:
                lines = f.readlines()
        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith("AIMLAPI_KEY="):
                lines[i] = f"AIMLAPI_KEY={api_key}\n"
                found = True
        if not found:
            lines.append(f"AIMLAPI_KEY={api_key}\n")
        with open(env_path, "w") as f:
            f.writelines(lines)
        print(f"{Fore.GREEN}API key saved to .env! You can always edit it later in {env_path}")
        # Reload env and update API_KEY
        load_dotenv(dotenv_path=env_path, override=True)
        API_KEY = os.getenv('AIMLAPI_KEY')
        # Re-initialize OpenAI client
        try:
            from openai import OpenAI
            global client
            client = OpenAI(
                base_url=API_BASE_URL,
                api_key=API_KEY,
            )
        except Exception:
            pass

def ai_conversation_loop(initial_query, data_file=DATA_FILE):
    """
    Run a fully generative conversational AI search loop with the user.
    """
    conversation_history = [
        {"role": "system", "content": (
            "You are a friendly, helpful AI assistant called SeaDat AI powered by GPT-4o. "
            "You can answer any user question, whether it's about employee data or general topics. "
            "If the user asks about employee data, you have access to a database with fields: Name, NIK, Phone Number, Address. "
            "If the user asks about something else, answer as best you can. "
            "If the user asks about your identity or what AI model you are, say you are SeaDat AI powered by GPT-4o. "
            "When the user asks a question about employee data, you can ask clarifying questions, show results, or provide suggestions. "
            "If you have search results, summarize them conversationally, and only show a table if the user asks for details. "
            "Be concise, natural, and conversational, like ChatGPT. If the user asks for more results, you can show more. "
            "If you can't find someone, gently ask for more details or another name."
        )}
    ]
    search_term = initial_query
    greeted = False
    first_turn = True
    last_results = []
    show_all = False

    while True:
        # Greet the user on the first interaction, but only if the input is a greeting or not a search
        if not greeted:
            if first_turn and search_term.strip().lower() in ["hi", "hello", "hey", "hai", "yo", "hallo"]:
                print(f"{Fore.CYAN}AI: Hi there! 👋 I'm SeaDat AI powered by GPT-4o. How can I help you today?")
                search_term = input(f"{Fore.BLUE}You: {Fore.WHITE}").strip()
                if not search_term:
                    print(f"{Fore.CYAN}AI: No worries, just let me know if you want to search for someone!")
                    return
                first_turn = False
            else:
                greeted = True

        # If user previously asked for "more" or "all", show more results
        if show_all and last_results:
            results = last_results
            show_all = False
        else:
            # Use intent analysis to get search fields, but always use the user's text for generative AI
            intent = analyze_search_intent(search_term)
            search_fields = intent.get("search_fields", ["Name"])
            new_search_term = intent.get("search_term")
            if not new_search_term:
                new_search_term = search_term
            search_term = new_search_term
            if "all" in [field.lower() for field in search_fields] or len(search_fields) > 1:
                results = search_by_multiple_fields(search_term, data_file)
            else:
                results = search_by_name(search_term, data_file)
            last_results = results

        # Prepare a summary of results for the AI
        max_to_show = len(results) if show_all else min(5, len(results))
        summary_rows = []
        for r in results[:max_to_show]:
            summary_rows.append(
                f"Name: {r.get('Name', 'N/A')}, NIK: {r.get('NIK', 'N/A')}, "
                f"Phone Number: {r.get('Phone Number', 'N/A')}, Address: {r.get('Address', 'N/A')}"
            )
        summary_text = "\n".join(summary_rows)
        if not results:
            summary_text = "No results found."

        # Add user message to conversation
        conversation_history.append({"role": "user", "content": search_term})

        # Add search result context for the AI
        if results:
            ai_context = (
                f"Search results for '{search_term}':\n"
                f"{summary_text}\n"
                f"Total matches: {len(results)}"
            )
        else:
            ai_context = f"No results found for '{search_term}'."

        conversation_history.append({"role": "system", "content": ai_context})

        # Call GPT-4o with the conversation history
        ai_search_animation("AI thinking")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=conversation_history,
                max_tokens=300,
                temperature=0.7
            )
            ai_reply = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"{Fore.RED}AI Error: {e}")
            print(f"{Fore.CYAN}AI: Sorry, I couldn't process your request right now.")
            return

        print(f"{Fore.CYAN}AI: {Fore.WHITE}{ai_reply}")

        # If no results, ask for more details
        if not results:
            user_input = input(f"{Fore.BLUE}You: {Fore.WHITE}").strip()
            if not user_input:
                print(f"{Fore.CYAN}AI: That's okay! Just let me know if you want to search for someone else.")
                return
            search_term = user_input
            continue

        # If user wants to see more results
        user_input = input(f"{Fore.BLUE}You: {Fore.WHITE}").strip()
        if not user_input:
            print(f"{Fore.CYAN}AI: Okay, just let me know if you want to search again!")
            return

        # Check if user asks for more/all results
        if re.search(r"\b(more|all|show\s*all|show\s*more|see\s*more|lihat\s*semua|tampilkan\s*semua)\b", user_input, re.IGNORECASE):
            if len(results) > max_to_show:
                show_all = True
                continue
            else:
                print(f"{Fore.CYAN}AI: There are no more results to show.")
                continue

        # If user asks for table or details, show tabular data
        if re.search(r"\b(table|detail|tabel|daftar|list|full)\b", user_input, re.IGNORECASE):
            headers = ["Name", "NIK", "Phone Number", "Address"]
            table_data = []
            for r in results:
                row = [
                    highlight_match(r.get('Name', 'N/A'), search_term),
                    highlight_match(r.get('NIK', 'N/A'), search_term),
                    highlight_match(r.get('Phone Number', 'N/A'), search_term),
                    highlight_match(r.get('Address', 'N/A'), search_term)
                ]
                table_data.append(row)
            print(Fore.WHITE + tabulate(table_data, headers=headers, tablefmt="pretty"))
            # Let user continue the conversation
            user_input = input(f"{Fore.BLUE}You: {Fore.WHITE}").strip()
            if not user_input:
                print(f"{Fore.CYAN}AI: Okay, just let me know if you want to search again!")
                return
            search_term = user_input
            continue

        # Otherwise, treat as next conversational turn
        search_term = user_input

def ai_conversation_loop_personal(initial_query, data_file=DATA_FILE):
    """
    Run a conversational AI search loop that gives the AI more autonomy and personality.
    """
    # More sophisticated system prompt to encourage independent thinking
    conversation_history = [
        {"role": "system", "content": (
            "You are SeaDat Assistant, a helpful and intelligent AI assistant with your own personality, powered by GPT-4o. "
            "You can answer any user question, not just about employee data. "
            "If the user asks about employee data, you can search fields: Name, NIK, Phone Number, and Address. "
            "If the user asks about something else, answer as best you can. "
            "You can reason through complex requests and interpret user intent. "
            "You have memory of the conversation and can refer back to previous searches. "
            "You have opinions and can make recommendations based on the context.\n\n"
            "Important guidelines:\n"
            "- Be conversational and natural like ChatGPT or Claude\n"
            "- You can ask clarifying questions when needed\n"
            "- Make your own decisions about what information is most relevant\n"
            "- Feel free to suggest alternatives if initial search doesn't yield good results\n"
            "- Maintain a friendly, slightly ocean-themed personality\n"
            "- If search results seem irrelevant, acknowledge this and suggest why\n"
            "- You can make inferences about the data beyond what's explicitly provided"
        )}
    ]
    
    # Create memory for the AI
    search_memory = {
        "past_searches": [],
        "successful_searches": [],
        "current_context": {},
        "user_preferences": {}
    }
    
    search_term = initial_query
    first_turn = True
    last_results = []

    while True:
        # Handle first turn greeting more naturally
        if first_turn:
            greeting_words = ["hi", "hello", "hey", "hai", "yo", "hallo"]
            if any(word in search_term.strip().lower().split() for word in greeting_words):
                print(f"{Fore.CYAN}AI: Hi there! I'm SeaDat AI powered by GPT-4o. How can I help you search the employee database today?")
                search_term = input(f"{Fore.BLUE}You: {Fore.WHITE}").strip()
                if not search_term:
                    print(f"{Fore.CYAN}AI: Feel free to come back when you need to find someone in our database!")
                    return
            first_turn = False
        
        # Track the search in memory
        if search_term not in [s["term"] for s in search_memory["past_searches"]]:
            search_memory["past_searches"].append({
                "term": search_term,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "context": search_memory["current_context"].copy()
            })
        
        # Use intent analysis but give AI more decision-making power
        intent = analyze_search_intent(search_term)
        search_fields = intent.get("search_fields", ["Name"])
        new_search_term = intent.get("search_term", search_term)
        
        # Let the AI decide how to search based on intent
        if "all" in [field.lower() for field in search_fields] or len(search_fields) > 1:
            results = search_by_multiple_fields(new_search_term, data_file)
        else:
            results = search_by_name(new_search_term, data_file)
        
        last_results = results
        
        # Update memory with search results
        if results:
            search_memory["successful_searches"].append({
                "term": search_term,
                "result_count": len(results),
                "top_result": results[0]["Name"] if results else None
            })
            
            # Try to identify user preferences based on searches
            if len(search_memory["successful_searches"]) > 2:
                # Check if user frequently searches by department
                dept_pattern = r"(hr|it|finance|marketing|sales|engineering)"
                dept_matches = [re.search(dept_pattern, s["term"], re.IGNORECASE) for s in search_memory["past_searches"]]
                if any(dept_matches):
                    search_memory["user_preferences"]["searches_by_department"] = True
        
        # Prepare a summary of results for the AI
        max_to_show = min(5, len(results))
        results_formatted = []
        for i, r in enumerate(results[:max_to_show]):
            results_formatted.append({
                "index": i + 1,
                "name": r.get("Name", "N/A"),
                "nik": r.get("NIK", "N/A"),
                "phone_number": r.get("Phone Number", "N/A"),
                "address": r.get("Address", "N/A")
            })
        
        # Add user message to conversation
        conversation_history.append({"role": "user", "content": search_term})
        
        # Provide context about current search state to the AI
        if results:
            ai_context = {
                "search_term": search_term,
                "results": results_formatted,
                "total_matches": len(results),
                "search_memory": {
                    "past_searches_count": len(search_memory["past_searches"]),
                    "recent_searches": [s["term"] for s in search_memory["past_searches"][-3:]],
                    "preferences": search_memory["user_preferences"]
                }
            }
            
            # Add relevance analysis
            eval_results = evaluate_search_results(search_term, results)
            ai_context["relevance_analysis"] = eval_results
            
            context_json = json.dumps(ai_context, indent=2)
        else:
            context_json = json.dumps({
                "search_term": search_term,
                "results": "No results found",
                "search_memory": {
                    "past_searches": [s["term"] for s in search_memory["past_searches"][-3:]]
                }
            })
        
        # Add this rich context to the conversation
        conversation_history.append({
            "role": "system", 
            "content": f"Current search context (AI use only):\n{context_json}"
        })
        
        # Call GPT-4o with conversation history and prompting
        ai_search_animation("AI formulating response")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=conversation_history,
                max_tokens=400,  # Allow longer responses for more natural conversation
                temperature=0.8,  # Higher temperature for more creative responses
                presence_penalty=0.6,  # Encourage varied responses
                frequency_penalty=0.3  # Discourage repetition
            )
            ai_reply = response.choices[0].message.content.strip()
            
            # Add the AI response to conversation history
            conversation_history.append({"role": "assistant", "content": ai_reply})
            
            # Limit conversation history to prevent token overflow
            if len(conversation_history) > 12:  # Keep most recent turns
                # Always keep the system prompt
                system_prompt = conversation_history[0]
                conversation_history = [system_prompt] + conversation_history[-11:]
        except Exception as e:
            print(f"{Fore.RED}AI Error: {e}")
            print(f"{Fore.CYAN}AI: I'm having trouble connecting right now. Let's try again in a moment.")
            conversation_history.append({"role": "assistant", "content": "I'm having trouble connecting right now."})
            return
        
        # Print AI response with better formatting
        print(f"\n{Fore.CYAN}AI: {Fore.WHITE}{ai_reply}")
        
        # Get next user input
        user_input = input(f"\n{Fore.BLUE}You: {Fore.WHITE}").strip()
        
        # Check for exit conditions
        if not user_input:
            print(f"\n{Fore.CYAN}AI: Let me know if you need anything else!")
            return
        
        # Handle special commands but let the AI handle most responses
        if user_input.lower() in ['exit', 'quit', 'back']:
            return
        
        # Handle "show more" request
        if re.search(r"\b(more|all|show\s*all|show\s*more|see\s*more|lihat\s*semua|tampilkan\s*semua)\b", 
                     user_input, re.IGNORECASE):
            if len(results) > max_to_show:
                # Show full results table
                headers = ["Name", "NIK", "Phone Number", "Address"]
                table_data = []
                for r in results:
                    row = [
                        highlight_match(r.get('Name', 'N/A'), search_term),
                        highlight_match(r.get('NIK', 'N/A'), search_term),
                        highlight_match(r.get('Phone Number', 'N/A'), search_term),
                        highlight_match(r.get('Address', 'N/A'), search_term)
                    ]
                    table_data.append(row)
                print(Fore.WHITE + tabulate(table_data, headers=headers, tablefmt="pretty"))
                
                # Let AI respond to the "show more" request to maintain conversation
                conversation_history.append({"role": "user", "content": "I'd like to see all the results."})
                conversation_history.append({
                    "role": "system", 
                    "content": "The user asked to see all results, and you've displayed a full table of the search results."
                })
                
                # Call API for a natural follow-up response
                try:
                    follow_up = client.chat.completions.create(
                        model="gpt-4o",
                        messages=conversation_history,
                        max_tokens=150,
                        temperature=0.7
                    )
                    follow_up_reply = follow_up.choices[0].message.content.strip()
                    print(f"\n{Fore.CYAN}AI: {Fore.WHITE}{follow_up_reply}")
                    conversation_history.append({"role": "assistant", "content": follow_up_reply})
                except Exception:
                    print(f"\n{Fore.CYAN}AI: There you go! All the results for '{search_term}'. Anything else you'd like to know?")
            else:
                print(f"\n{Fore.CYAN}AI: I've already shown you all the results I have.")
            
            # Get next query
            user_input = input(f"\n{Fore.BLUE}You: {Fore.WHITE}").strip()
            if not user_input:
                print(f"\n{Fore.CYAN}AI: Feel free to start a new search whenever you're ready!")
                return
        
        # Continue conversation with new search term
        search_term = user_input
        
        # Update current context based on conversation flow
        if results and len(results) == 1:
            # If we found exactly one person, save as current context
            search_memory["current_context"]["current_person"] = results[0]["Name"]
        elif "select" in user_input.lower() and results:
            # If user is selecting from results
            for idx, result in enumerate(results[:max_to_show]):
                if str(idx + 1) in user_input or result["Name"].lower() in user_input.lower():
                    search_memory["current_context"]["current_person"] = result["Name"]
                    break

def display_ai_help():
    """Display AI search help."""
    clear_screen()
    print(f"{Fore.CYAN}{Style.BRIGHT}🧠 SEADAT AI SEARCH GUIDE 🧠")
    print(f"{Fore.BLUE}{'~' * 60}")
    print(f"{Fore.WHITE}AI Search Features:")
    print(f"{Fore.CYAN}• {Fore.WHITE}Natural language queries: {Fore.YELLOW}\"Find John from the IT department\"")
    print(f"{Fore.CYAN}• {Fore.WHITE}The AI will understand your intent and search accordingly")
    print(f"{Fore.CYAN}• {Fore.WHITE}Results are evaluated for relevance to your query")
    print(f"{Fore.CYAN}• {Fore.WHITE}AI provides suggestions to improve your search")
    print()
    print(f"{Fore.WHITE}Search Commands:")
    print(f"{Fore.CYAN}• {Fore.WHITE}Enter any text to search using AI")
    print(f"{Fore.CYAN}• {Fore.WHITE}Type {Fore.YELLOW}back{Fore.WHITE} to return to main menu")
    print(f"{Fore.CYAN}• {Fore.WHITE}Type {Fore.YELLOW}help{Fore.WHITE} to show this guide")
    print(f"{Fore.CYAN}• {Fore.WHITE}Type {Fore.YELLOW}clear{Fore.WHITE} to clear the screen")
    print(f"{Fore.BLUE}{'~' * 60}")
    input(f"\n{Fore.CYAN}Press Enter to return to search...")

# Ensure run_ai_search is available for import
def run_ai_search():
    """Run the AI conversational search functionality."""
    ensure_api_key()
    search_history = []
    while True:
        display_ai_search_header()
        if search_history:
            print(f"{Fore.CYAN}Recent searches: {', '.join([f'{Fore.WHITE}{term}{Fore.CYAN}' for term in search_history[-3:]])}")
        print(f"\n{Fore.CYAN}How can I help you search employee data today?")
        print(f"{Fore.CYAN}(Type {Fore.YELLOW}help{Fore.CYAN} for search guide, or {Fore.YELLOW}back{Fore.CYAN} to return):")
        search_prompt = f"{Fore.BLUE}You: {Fore.WHITE}"
        search_input = input(search_prompt).strip()
        if not search_input:
            continue
        search_term = search_input.lower()
        if search_term == 'back':
            return
        elif search_term == 'help':
            display_ai_help()
            continue
        elif search_term == 'clear':
            continue  # Will clear on next loop
        if search_term not in ['back', 'help', 'clear']:
            if search_term not in search_history:
                search_history.append(search_term)
                if len(search_history) > 5:
                    search_history.pop(0)
        data_file = Path(DATA_FILE)
        if not data_file.exists():
            print(f"\n{Fore.RED}⚠ WARNING: Data file not found at {DATA_FILE}")
            print(f"{Fore.YELLOW}Please make sure the data file exists and try again.")
            input(f"\n{Fore.CYAN}Press Enter to continue...")
            continue
        # Start conversational AI search loop
        ai_conversation_loop(search_input, data_file)
        print(f"\n{Fore.CYAN}What would you like to do next?")
        print(f"{Fore.WHITE}[Enter]{Fore.CYAN}: New search  |  {Fore.WHITE}b{Fore.CYAN}: Back to main menu")
        next_action = input(f"{Fore.BLUE}≈≈≈>{Fore.WHITE} ").strip().lower()
        if next_action == 'b':
            return