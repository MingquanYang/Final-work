from pythonosc import udp_client
import time

# 配置 OSC 客户端
ip = "127.0.0.1"  # 本地地址（确保 TouchDesigner 在本机上运行）
port = 12345       # 目标端口（和 TouchDesigner 中的 OSC In DAT 配置一致）

# 创建一个 SimpleUDPClient 实例
osc_client = udp_client.SimpleUDPClient(ip, port)

# 发送 OSC 消息的函数
def send_osc_test_message():
    try:
        # 发送测试消息到 TouchDesigner，地址是 "/test/message"，值为 "Hello from Python"
        osc_client.send_message("/test/message", "Hello from Python")
        print("发送 OSC 消息成功: /test/message Hello from Python")
    except Exception as e:
        print(f"发送 OSC 消息失败: {e}")

if __name__ == "__main__":
    while True:
        send_osc_test_message()
        time.sleep(1)  # 每秒发送一次测试消息
