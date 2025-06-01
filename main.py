import os
import requests
import base64

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

# 示例：公共订阅链接（请替换成你自己找到的真实订阅）
SUBSCRIBE_URL = "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub"

def get_nodes():
    try:
        resp = requests.get(SUBSCRIBE_URL)
        resp.raise_for_status()
        data = resp.text.strip()
        
        # 有些订阅内容是 base64 编码，需要先解码
        decoded = base64.b64decode(data).decode('utf-8')
        
        # 按行分割，过滤出有效节点
        nodes = [line for line in decoded.splitlines() if line.startswith(("ss://", "vmess://", "clash://"))]
        
        return nodes[:10]  # 取前10条
    except Exception as e:
        print("抓取节点出错:", e)
        return []

def format_nodes(nodes):
    return "\n".join(nodes)

def send_message(bot_token, channel_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": channel_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    if not response.ok:
        print("发送消息失败:", response.text)
    else:
        print("消息发送成功")

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
