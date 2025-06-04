# main.py
import requests
from bs4 import BeautifulSoup
import yaml
import re
import time
import os
from telegram import Bot

# Telegram 配置
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # 推荐在 GitHub Secrets 设置
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 订阅链接关键词匹配
CLASH_KEYWORDS = [".yaml", ".yml"]
VMESS_KEYWORDS = ["vmess://"]
SSR_KEYWORDS = ["ssr://"]
SS_KEYWORDS = ["ss://"]

headers = {
    'User-Agent': 'Mozilla/5.0'
}

def fetch_freefq_links():
    url = "https://freefq.com/free-ssr/"
    print(f"🌐 正在爬取: {url}")
    resp = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")

    links = []
    for article in soup.select(".post-inner h2 a"):
        href = article.get("href")
        if href:
            links.append(href)

    print(f"✅ 找到 {len(links)} 篇文章链接")
    return links

def extract_subscribe_links(post_url):
    print(f"➡️ 正在解析文章: {post_url}")
    try:
        resp = requests.get(post_url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text()

        # 通过正则匹配 clash/vmess/ssr/ss 链接
        found = re.findall(r'(https?://[^\s"\<>]+)', text)
        filtered = [link for link in found if any(k in link for k in CLASH_KEYWORDS + VMESS_KEYWORDS + SSR_KEYWORDS + SS_KEYWORDS)]
        return list(set(filtered))
    except Exception as e:
        print(f"⚠️ 获取失败: {post_url} 错误: {e}")
        return []

def validate_clash_link(url):
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200 and ("proxies" in resp.text or "proxy-groups" in resp.text):
            return True
    except:
        pass
    return False

def send_to_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ 未配置 Telegram Token 或 Chat ID")
        return
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')
        print("📤 成功推送到 Telegram")
    except Exception as e:
        print(f"❌ 推送失败: {e}")

def main():
    print("\n=======================")
    print("🚀 FreeFQ VPN 爬虫启动")
    print("=======================")
    articles = fetch_freefq_links()
    all_links = []

    for url in articles[:5]:  # 只取前5篇
        links = extract_subscribe_links(url)
        all_links.extend(links)
        time.sleep(2)

    all_links = list(set(all_links))
    print(f"🔍 共提取到 {len(all_links)} 条原始订阅链接")

    valid_links = []
    for link in all_links:
        if any(k in link for k in CLASH_KEYWORDS):
            if validate_clash_link(link):
                valid_links.append(link)
                print(f"✅ 有效: {link}")
            else:
                print(f"❌ 无效: {link}")

    if valid_links:
        msg = "<b>🎯 免费 Clash 节点推送</b>\n"
        for i, link in enumerate(valid_links, 1):
            msg += f"{i}. <code>{link}</code>\n"
        send_to_telegram(msg)
    else:
        print("❌ 没有可用链接，跳过推送")

    with open("valid_links.txt", "w") as f:
        for link in valid_links:
            f.write(link + "\n")

if __name__ == "__main__":
    main()
