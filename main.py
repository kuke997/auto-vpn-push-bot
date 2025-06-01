import os
import requests
import yaml

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SUBSCRIBE_URL = os.getenv("SUBSCRIBE_URL")

def get_nodes_from_yaml(yaml_text):
    """
    解析 Clash YAML 配置，提取节点详细信息，返回字符串列表
    """
    try:
        data = yaml.safe_load(yaml_text)
        proxies = data.get("proxies", [])
        nodes = []
        for proxy in proxies:
            ptype = proxy.get("type", "未知类型").upper()
            name = proxy.get("name", "未知节点")
            server = proxy.get("server", "")
            port = proxy.get("port", "")
            if ptype == "VMESS":
                uuid = proxy.get("uuid", "")
                alterId = proxy.get("alterId", "")
                network = proxy.get("network", "")
                nodes.append(
                    f"- {ptype} | {name}\n"
                    f"  服务器: {server}:{port}\n"
                    f"  UUID: {uuid}\n"
                    f"  AlterId: {alterId}\n"
                    f"  网络: {network}"
                )
            elif ptype == "TROJAN":
                password = proxy.get("password", "")
                nodes.append(
                    f"- {ptype} | {name}\n"
                    f"  服务器: {server}:{port}\n"
                    f"  密码: {password}"
                )
            elif ptype == "SS":
                cipher = proxy.get("cipher", "")
                password = proxy.get("password", "")
                nodes.append(
                    f"- {ptype} | {name}\n"
                    f"  服务器: {server}:{port}\n"
                    f"  加密方式: {cipher}\n"
                    f"  密码: {password}"
                )
            else:
                # 其他类型，简单输出
                nodes.append(f"- {ptype} | {name}\n  服务器: {server}:{port}")
        return nodes
    except Exception as e:
        print("解析 YAML 出错:", e)
        return []

def get_nodes():
    try:
        print(f"使用的订阅地址：'{SUBSCRIBE_URL}'")
        resp = requests.get(SUBSCRIBE_URL, timeout=15)
        resp.raise_for_status()
        print("响应头信息：", resp.headers)
        content_type = resp.headers.get("Content-Type", "")
        print("内容类型：", content_type)
        preview = resp.text[:300].replace("\n", "\\n")
        print("开始解析 YAML，内容预览：", preview)
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

    # 只取前10个节点，避免消息过长
    nodes_message = "\n\n".join(nodes[:10])
    message = (
        "*🎯 免费 VPN 节点更新（每日）*\n"
        "以下是今日可用节点（仅展示部分）：\n\n"
        f"{nodes_message}"
    )
    send_message(BOT_TOKEN, CHANNEL_ID, message)

if __name__ == "__main__":
    main()
