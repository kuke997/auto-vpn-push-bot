import os
import requests
import yaml
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SUBSCRIBE_URL = os.getenv("SUBSCRIBE_URL")

def escape_markdown(text: str) -> str:
    # Telegram Markdown 特殊字符转义
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def get_nodes_from_yaml(yaml_text):
    """
    从 Clash 配置的 YAML 文本中提取详细节点信息，返回格式化字符串列表
    """
    try:
        data = yaml.safe_load(yaml_text)
        proxies = data.get("proxies", [])
        nodes = []
        for proxy in proxies:
            # 基础信息
            name = proxy.get("name", "未知节点")
            ptype = proxy.get("type", "未知类型").upper()
            server = proxy.get("server", "无服务器信息")
            port = proxy.get("port", "")
            password = proxy.get("password", "") or proxy.get("passwd", "")
            cipher = proxy.get("cipher", "")
            # 组合服务器地址和端口
            server_port = f"{server}:{port}" if port else server

            # 拼接节点详细信息（根据类型区分格式）
            if ptype == "SS":  # Shadowsocks
                node_info = (
                    f"- {ptype} | {escape_markdown(name)}\n"
                    f"  服务器: {escape_markdown(server_port)}\n"
                    f"  加密方式: {escape_markdown(cipher)}\n"
                    f"  密码: {escape_markdown(password)}"
                )
            elif ptype == "TROJAN":
                node_info = (
                    f"- {ptype} | {escape_markdown(name)}\n"
                    f"  服务器: {escape_markdown(server_port)}\n"
                    f"  密码: {escape_markdown(password)}"
                )
            else:
                # 其他类型简略显示
                node_info = f"- {ptype} | {escape_markdown(name)}\n  服务器: {escape_markdown(server_port)}"

            nodes.append(node_info)
        return nodes
    except Exception as e:
        print("解析 YAML 出错:", e)
        return []

def get_nodes():
    try:
        print(f"使用的订阅地址： '{SUBSCRIBE_URL}'")
        resp = requests.get(SUBSCRIBE_URL, timeout=15)
        resp.raise_for_status()

        print("响应头信息：", resp.headers)
        content_type = resp.headers.get('Content-Type', '')
        print("内容类型：", content_type)
        # 打印内容开头，防止太长
        preview = resp.text[:500].replace("\n", "\\n")
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
        "parse_mode": "MarkdownV2"
    }
    resp = requests.post(url, json=payload)
    if not resp.ok:
        print("发送消息失败:", resp.text)
    else:
        print("消息发送成功")

def main():
    if not (BOT_TOKEN and CHANNEL_ID and SUBSCRIBE_URL):
        print("环境变量 BOT_TOKEN、CHANNEL_ID 或 SUBSCRIBE_URL 未设置")
        return

    nodes = get_nodes()
    if not nodes:
        print("没有获取到有效节点")
        return

    # 拼接消息，限制展示数量，防止太长
    message = (
        "*🎯 免费 VPN 节点更新（每日）*\n"
        "以下是今日可用节点（仅展示部分）：\n\n" + "\n\n".join(nodes[:10])
    )

    send_message(BOT_TOKEN, CHANNEL_ID, message)

if __name__ == "__main__":
    main()
