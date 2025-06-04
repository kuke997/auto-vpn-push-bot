import requests
from bs4 import BeautifulSoup
import re
import time
import yaml
from telegram import Bot

# Telegram 配置
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHANNEL_OR_USER_ID'

# 伪装请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
}

def fetch_article_links():
    print("🌐 开始爬取 freefq.com 最新页面...")
    url = 'https://freefq.com/free-ssr/'
    resp = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    articles = soup.select('article h2 a')
    article_links = [a['href'] for a in articles if '/free-' in a['href']]
    print(f"✅ 获取到 {len(article_links)} 篇文章链接")
    return article_links

def extract_subscribe_links(article_url):
    print(f"➡️ 解析文章: {article_url}")
    try:
        resp = requests.get(article_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = re.findall(r'(https?://[^\s<>"\'\)]+)', soup.text)
        clash_links = [l for l in links if 'clash' in l.lower() or 'sub' in l.lower() or 'v2ray' in l.lower()]
        return clash_links
    except Exception as e:
        print(f"⚠️ 文章解析失败: {e}")
        return []

def validate_link(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        content_type = resp.headers.get('Content-Type', '')
        if 'yaml' in content_type or 'text' in content_type or 'json' in content_type:
            return True
    except Exception:
        pass
    return False

def push_to_telegram(valid_links):
    if not valid_links:
        print("❌ 无有效链接，跳过推送")
        return

    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    msg = "🌐 免费 Clash / V2Ray 节点更新：\n\n"
    for idx, link in enumerate(valid_links[:10], start=1):
        msg += f"{idx}. [点击使用]({link})\n"

    msg += "\n📅 更新时间: " + time.strftime('%Y-%m-%d %H:%M:%S')
    print("📤 推送到 Telegram...")
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    article_links = fetch_article_links()
    all_links = []
    for link in article_links[:3]:  # 只处理前3篇
        all_links += extract_subscribe_links(link)
        time.sleep(1)

    print(f"🔍 共提取到 {len(all_links)} 条链接，开始验证...")

    valid_links = []
    for link in all_links:
        if validate_link(link):
            valid_links.append(link)

    print(f"✔️ 验证完成！共 {len(valid_links)} 条有效链接")
    with open("valid_links.txt", "w") as f:
        for l in valid_links:
            f.write(l + "\n")

    push_to_telegram(valid_links)
    print("✅ 任务完成！")

if __name__ == "__main__":
    main()
