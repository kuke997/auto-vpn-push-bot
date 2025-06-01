import os
import requests
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

def fetch_free_nodes():
    sources = [
        "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
        "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
        "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt"
    ]
    nodes = set()
    for url in sources:
        try:
            resp = requests.get(url, timeout=10)
            if "://" in resp.text:
                nodes.update(re.findall(r'(ss://\S+|vmess://\S+|trojan://\S+)', resp.text))
        except Exception as e:
            print(f"Error fetching from {url}: {e}")
    return list(nodes)[:10]

def format_nodes(nodes):
    return "\n".join(f"{i+1}. `{node}`" for i, node in enumerate(nodes))

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    resp = requests.post(url, json=payload)
    print(resp.text)

if __name__ == "__main__":
    nodes = fetch_free_nodes()
    if nodes:
        message = "*🎯 免费 VPN 节点更新（每日）*

" + format_nodes(nodes)
        send_to_telegram(message)
    else:
        send_to_telegram("⚠️ 今日未能抓取到有效节点")
