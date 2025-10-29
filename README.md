# Dự án Stream Video WebRTC bằng Django

Đây là một dự án streaming video sử dụng Django làm backend, aiortc cho kết nối WebRTC, và Django Channels cho chat thời gian thực.

## Công Nghệ Sử Dụng

* **Backend:** Django, Django Channels
* **WebRTC:** aiortc
* **ASGI Server:** Daphne
* **Database:** PostgreSQL
* **Chat Backend:** Redis
* **Frontend:** HTML, CSS, JavaScript
* **Deployment:** Render.com

## Yêu cầu (Development)

* Python 3.8+
* Một camera/webcam

## Cài đặt (Development)

1.  Clone repository này về:
    ```bash
    git clone [<URL_REPO_CUA_BAN>](https://github.com/1usuzu/streaming)
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

4.  Chạy migrate (để tạo bảng CSDL ban đầu, bao gồm cả bảng user):
    ```bash
    python manage.py migrate
    ```

## Chạy Dự Án (Development)

Dự án này phải được chạy bằng một máy chủ ASGI như Daphne (không dùng `manage.py runserver`).

```bash
daphne -p 8000 webrtc.asgi:application
