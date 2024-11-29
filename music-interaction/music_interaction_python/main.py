import ultralytics
from ultralytics import YOLO
import os
import cv2
import serial
import time
import threading
from pythonosc import udp_client

# 检查 Ultralytics 库
ultralytics.checks()

# 获取当前工作目录
HOME = os.getcwd()
print(HOME)

# 加载训练好的YOLO模型
model = YOLO(f'{HOME}/best.pt')

# 串口配置（根据实际的串口号进行修改）
ser = serial.Serial('COM18', 115200, timeout=3)  # 替换为您的串口号

try:
    if ser.is_open:
        print("串口打开成功！")
    else:
        print("串口打开失败！")
        exit()
except serial.SerialException as e:
    print(f"串口连接失败: {e}")
    exit()

target_objects = ["red", "blue", "green", "yellow"]

# 网格设置（4 行 7 列）
grid_width = 7
grid_height = 4
grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]

# 设置偏移量
offset_left = 0
offset_right = 0
offset_top = 70
offset_bottom = 10

# 计算网格位置的函数
def get_grid_position(x, y, w, h, frame_width, frame_height):
    grid_x = int((x-offset_left + w / 2) / ((frame_width-offset_left-offset_right) / grid_width))
    grid_y = int((y-offset_top + h / 2) / ((frame_height-offset_top-offset_bottom) / grid_height))
    return grid_x, grid_y

# 创建 OSC 客户端，目标地址为 127.0.0.1，端口为 12345
ip = "127.0.0.1"
port = 1111
osc_client = udp_client.SimpleUDPClient(ip, port)

# 定义全局变量存储鼠标坐标
mouse_x = 0
mouse_y = 0

# 鼠标回调函数
def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_y
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x = x
        mouse_y = y

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Frame Width: {frame_width}, Frame Height: {frame_height}")

    grid_cell_width = (frame_width-offset_left-offset_right)  // grid_width
    grid_cell_height = (frame_height-offset_top-offset_bottom) // grid_height
    print(f"Grid Cell Width: {grid_cell_width}, Grid Cell Height: {grid_cell_height}")

    bg_image = cv2.imread('bg.png')
    bg_image = cv2.resize(bg_image, (frame_width, frame_height))

    while True:
        oscmsg = ""
        grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
        ret, frame = cap.read()
        if not ret:
            print("无法读取帧")
            break

        results = model.predict(source=frame, conf=0.7, save=False, save_txt=False)
        annotated_frame = results[0].plot()

        for i in range(0, grid_width):
            cv2.line(annotated_frame, (int(i * grid_cell_width+offset_left), 0), (int(i * grid_cell_width+offset_left), frame_height), (255, 0, 0), 2)
        for i in range(0, grid_height):
            cv2.line(annotated_frame, (0,int( i * grid_cell_height+offset_top)), (frame_width, int(i * grid_cell_height+offset_top)), (255, 0, 0), 2)

        boxes = results[0].boxes
        for box in boxes:
            class_id = int(box.cls[0].item())
            class_name = model.names[class_id]

            if class_name in target_objects and box.conf[0].item() > 0.75:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                oscmsg = oscmsg + str(x2 / 2 + x1 / 2) + "," + str(y1 / 2 + y2 / 2) + ","
                grid_x, grid_y = get_grid_position(x1, y1, x2 - x1, y2 - y1, frame_width, frame_height)

                if 0 <= grid_x < grid_width and 0 <= grid_y < grid_height:
                    grid[class_id][grid_x] = 1

        grid_string = ''.join([str(grid[y][x]) for y in range(grid_height) for x in range(grid_width)])
        send_osc_coordinates(oscmsg)
        send_grid_data(grid_string)

        annotated_frame = cv2.addWeighted(annotated_frame, 0.7, bg_image, 0.3, 0)

        # 显示鼠标坐标
        cv2.putText(annotated_frame, f"Mouse: ({mouse_x}, {mouse_y})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow('YOLO Real-Time Detection', annotated_frame)

        # 设置鼠标回调函数
        cv2.setMouseCallback('YOLO Real-Time Detection', mouse_callback)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def send_grid_data(grid_string):
    try:
        ser.write(grid_string.encode())
        ser.flush()
        print(f"Sent: {grid_string}")
    except serial.SerialException as e:
        print(f"串口发送数据失败: {e}")
        pass
    except Exception as e:
        print(f"发生其他错误: {e}")
        pass

def send_osc_coordinates(oscmsg):
    try:
        osc_client.send_message("/object_coordinates", oscmsg)
        print(f"Sent OSC coordinates: {oscmsg}")
    except Exception as e:
        print(f"发送 OSC 数据失败: {e}")

def listen_for_success():
    while True:
        if ser.in_waiting > 0:
            message = ser.readline().strip()
            print(f"收到其他信息: {message}")

listener_thread = threading.Thread(target=listen_for_success, daemon=True)
listener_thread.start()




if __name__ == '__main__':
    main()
