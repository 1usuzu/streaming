#!/usr/bin/env bash
# Exit on error
set -o errexit

# Cài đặt các gói từ requirements.txt
pip install -r requirements.txt

# Thu thập các tệp tĩnh (CSS, JS...)
python manage.py collectstatic --no-input

# Chạy migrate để tạo bảng CSDL
python manage.py migrate