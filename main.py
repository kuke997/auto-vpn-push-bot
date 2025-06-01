import os
import requests
import yaml

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

# 示例 Clash 节点订阅链接（YAML 格式）
SUBSCRIBE_URL = "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub/clash.yaml"

def get_nodes():
    try:
        resp = requests.get(SUBSCRIBE_URL, timeout=10)
        resp.raise_for_status()

        data = yaml.safe_load(resp.text)
        proxies = data.get("proxies", [])

        nodes = []
        for proxy in proxies:
            name = proxy.get("name", "无名节点")
            proxy_type = proxy.get("type")
            server = proxy.get("server")

            if proxy_type in ["ss", "vmess", "trojan"]:
                node = f"{proxy_type.upper()} | {name} | {server}"
                nodes.append(node)

        return nodes[:10]  # 最多10条
    except Exception as e:
        print("抓取节点出错:", e)
        return []

def format_nodes(nodes):
    return "\n".join([f"- `{node}`" for node in nodes])

def send_message(bot_token, channel_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": channel_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    if not response.ok:
        print("发送失败:", response.text)
    else:
        print("发送成功")

def main():
    nodes = get_nodes()
    if not nodes:
        print("没有获取到有效节点")
        return

    message = """*🎯 免费 VPN 节点更新（每日）*
以下是今日可用节点：
""" + format_nodes(nodes)

    send_message(BOT_TOKEN, CHANNEL_ID, message)

if __name__ == "__main__":
    main()
