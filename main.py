import os
import requests
import yaml

# 获取并清理环境变量
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_ID = os.getenv("CHANNEL_ID", "").strip()
SUBSCRIBE_URL = os.getenv("SUBSCRIBE_URL", "").strip()

def get_nodes_from_yaml(yaml_text):
    """
    从 Clash 配置的 YAML 文本中提取节点名称和类型，返回节点列表
    """
    try:
        data = yaml.safe_load(yaml_text)
        proxies = data.get("proxies", [])
        nodes = []
        for proxy in proxies:
            name = proxy.get("name", "未知节点")
            ptype = proxy.get("type", "未知类型")
            nodes.append(f"- {ptype.upper()} | {name}")
        return nodes
    except Exception as e:
        print("解析 YAML 出错:", e)
        return []

def get_nodes():
    try:
        print("使用的订阅地址：", repr(SUBSCRIBE_URL))
        resp = requests.get(SUBSCRIBE_URL, timeout=10)
        print("响应头信息：", resp.headers)
        print("内容类型：", resp.headers.get("Content-Type", "未知"))
        print("开始解析 YAML，内容预览：", resp.text[:300])  # 打印前300字符内容
        resp.raise_for_status()
        return get_nodes_from_yaml(resp.text)
    except Exception as e:
        print("抓取节点出错:", e)
        return []

def send_message(bot_token, channel_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": channel_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(url, json=payload)
        if resp.ok:
            print("消息发送成功")
        else:
            print("发送消息失败:", resp.text)
    except Exception as e:
        print("发送消息异常:", e)

def main():
    if not (BOT_TOKEN and CHANNEL_ID and SUBSCRIBE_URL):
        print("环境变量 BOT_TOKEN、CHANNEL_ID 或 SUBSCRIBE_URL 未设置")
        return

    nodes = get_nodes()
    if not nodes:
        print("没有获取到有效节点")
        return

    message = "*🎯 免费 VPN 节点更新（每日）*\n以下是今日可用节点：\n" + "\n".join(nodes[:10])
    send_message(BOT_TOKEN, CHANNEL_ID, message)

if __name__ == "__main__":
    main()
