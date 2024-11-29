import serial
import time

# 配置串口（请根据需要修改串口号和波特率）
ser = serial.Serial('COM18', 115200, timeout=1)  # 替换为您的串口号

# 检查串口是否打开
if ser.is_open:
    print(f"串口 {ser.portstr} 打开成功")
else:
    print("串口打开失败")
    exit(1)

# 向串口发送数据
ser.write(b'Hello Arduino!\n')  # 发送一条简单的消息

# 等待 Arduino 的回应
time.sleep(2)  # 等待 2 秒

# 从串口读取数据
if ser.in_waiting > 0:
    data = ser.readline()  # 读取一行数据
    print(f"收到数据: {data.decode('utf-8').strip()}")
else:
    print("没有收到数据")

# 关闭串口
ser.close()
