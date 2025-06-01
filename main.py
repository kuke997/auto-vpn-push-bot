import os
import requests

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

def get_nodes():
    # 这里模拟抓取节点，实际你要改成抓你数据源
    # 返回节点列表字符串，每个节点用换行分隔
    nodes = [
        "ss://example1",
        "vmess://example2",
        "clash://example3",
        # ...最多10条
    ]
    return nodes[:10]

def format_nodes(nodes):
    # 把节点列表格式化成消息字符串
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
        print("Failed to send message:", response.text)
    else:
        print("Message sent successfully.")

def main():
    nodes = get_nodes()

    message = """*🎯 免费 VPN 节点更新（每日）*
以下是今日可用节点：
""" + format_nodes(nodes)

    send_message(BOT_TOKEN, CHANNEL_ID, message)

if __name__ == "__main__":
    main()
