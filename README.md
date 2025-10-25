# Dự án Stream Video WebRTC bằng Django

Đây là một dự án streaming video 1-nhiều (one-to-many) sử dụng Django làm backend (signaling server) và aiortc cho kết nối WebRTC.

## Yêu cầu
* Python 3.8+
* Một camera/webcam

## Cài đặt

1.  Clone repository này về:
    ```bash
    git clone https://github.com/1usuzu/streaming.git
    cd streaming
    ```

2.  Tạo và kích hoạt môi trường ảo:
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    
    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Cài đặt các thư viện cần thiết:
    ```bash
    pip install -r requirements.txt
    ```

## Chạy dự án

Dự án này phải được chạy bằng một máy chủ ASGI như Uvicorn (không dùng `manage.py runserver`).

```bash
uvicorn webrtc.asgi:application --host 127.0.0.1 --port 8000
```

## Cách sử dụng

1.  **Streamer:** Mở trình duyệt và truy cập:
    `http://127.0.0.1:8000/`
    Nhập ID phòng (ví dụ: `room1`) và nhấn "Start Streaming".

2.  **Viewer:** Mở trình duyệt (trong tab hoặc máy khác) và truy cập:
    `http://127.0.0.1:8000/viewer/`
    Nhập chính xác ID phòng (`room1`) và nhấn "Connect".
