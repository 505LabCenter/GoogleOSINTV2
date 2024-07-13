import os
import subprocess
import sys
import re
import requests
from bs4 import BeautifulSoup
from termcolor import colored
import time

def install_and_import(module_name):
    try:
        return __import__(module_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
        return __import__(module_name)

# Ensure required modules are installed
requests = install_and_import('requests')
bs4 = install_and_import('bs4')
termcolor = install_and_import('termcolor')
wikipedia = install_and_import('wikipedia')

def google_search(query, user_agent=None):
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": user_agent if user_agent else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    return response.text

def wikipedia_search(query):
    try:
        summary = wikipedia.summary(query, sentences=3)
        return summary
    except Exception as e:
        return f"Error retrieving Wikipedia summary: {str(e)}"

def social_media_search(query, platform, user_agent=None):
    search_query = f"{query} {platform}"
    html = google_search(search_query, user_agent)
    soup = BeautifulSoup(html, 'html.parser')
    social_media_pattern = {
        "facebook": r'https://www\.facebook\.com/[a-zA-Z0-9.]+',
        "twitter": r'https://twitter\.com/[a-zA-Z0-9_]+',
        "instagram": r'https://www\.instagram\.com/[a-zA-Z0-9._]+',
        "linkedin": r'https://[a-z]{2,3}\.linkedin\.com/in/[a-zA-Z0-9-]+'
    }
    for link in soup.find_all('a', href=True):
        href = link['href']
        if platform in href and 'google.com' not in href:
            match = re.search(social_media_pattern[platform], href)
            if match:
                return match.group(0)
    return None

def extract_information(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    data_patterns = {
        "emails": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        "phones": r'\b\d{10,15}\b',
        "addresses": r'\b\d{1,4}\s+\w+\s+(?:St|Street|Ave|Avenue|Blvd|Boulevard|Rd|Road|Lane|Ln|Dr|Drive|Pl|Place|Terrace|Terr|Way|W)\b',
        "websites": r'https?://[^\s<>"]+|www\.[^\s<>"]+',
        "full_names": r'\b[A-Z][a-z]*\s[A-Z][a-z]*\b'
    }

    extracted_data = {key: list(set(re.findall(pattern, text))) for key, pattern in data_patterns.items()}
    return extracted_data

def save_to_file(name, data, additional_info):
    with open(f"{name}.txt", "w") as file:
        file.write(f"Results for {name}:\n\n")
        for key, values in data.items():
            file.write(f"\n{key.capitalize().replace('_', ' ')}:\n")
            for value in values:
                file.write(f"{value}\n")
        for key, value in additional_info.items():
            file.write(f"\n{key}:\n{value}\n")

def display_results(query, data, additional_info):
    print(colored(f"\n{'='*10} Results for {query} {'='*10}\n", 'cyan', attrs=['bold']))
    for key, values in data.items():
        print(colored(f"{key.capitalize().replace('_', ' ')}:", 'green', attrs=['bold', 'underline']))
        if values:
            for value in values:
                print(colored(f"  - {value}", 'yellow'))
        else:
            print(colored("  - None found", 'red'))
    for key, value in additional_info.items():
        print(colored(f"{key}:", 'green', attrs=['bold', 'underline']))
        print(colored(f"  - {value}", 'yellow'))
    print(colored(f"\n{'='*10} End of Results {'='*10}\n", 'cyan', attrs=['bold']))

def osint_dorking(query, user_agent=None):
    html = google_search(query, user_agent)
    data = extract_information(html)
    
    social_media_platforms = ['facebook', 'twitter', 'instagram', 'linkedin']
    social_media_links = {platform.capitalize(): social_media_search(query, platform, user_agent) for platform in social_media_platforms}

    additional_info = {
        "Wikipedia Summary": wikipedia_search(query),
        **{f"{platform.capitalize()} Link": link for platform, link in social_media_links.items() if link}
    }

    save_to_file(query, data, additional_info)
    display_results(query, data, additional_info)

if __name__ == "__main__":
    try:
        os.system('clear')
        print(colored(" ██████╗  ██████╗  ██████╗  ██████╗ ██╗     ███████╗ ██████╗ ███████╗██╗███╗   ██╗████████╗", 'green'))
        print(colored("██╔════╝ ██╔═══██╗██╔═══██╗██╔════╝ ██║     ██╔════╝██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝", 'green'))
        print(colored("██║  ███╗██║   ██║██║   ██║██║  ███╗██║     █████╗  ██║   ██║███████╗██║██╔██╗ ██║   ██║", 'green'))
        print(colored("██║   ██║██║   ██║██║   ██║██║   ██║██║     ██╔══╝  ██║   ██║╚════██║██║██║╚██╗██║   ██║", 'green'))
        print(colored("╚██████╔╝╚██████╔╝╚██████╔╝╚██████╔╝███████╗███████╗╚██████╔╝███████║██║██║ ╚████║   ██║", 'green'))
        print(colored(" ╚═════╝  ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝ V1", 'green'))
        print("Author @505Snoop / Under Copyright @505Lab / t.me/Lab505 /Update by @dionealfarisi")
        print("\nEnter Information of Target | Ex: Ronaldo")
        
        query = input(colored("Enter information: ", 'green', attrs=['bold'])).strip()
        if not query:
            raise ValueError("Input cannot be empty.")

        user_agent = input(colored("Enter custom User-Agent (leave blank to use default): ", 'green', attrs=['bold']))

        print(colored("Inspector finding their information 🚀", 'magenta', attrs=['bold']))
        time.sleep(0.5)

        osint_dorking(query, user_agent if user_agent.strip() else None)
    except Exception as e:
        print(colored(f"An error occurred: {e}", 'red', attrs=['bold']))