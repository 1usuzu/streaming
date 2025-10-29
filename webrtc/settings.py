import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# (QUAN TRỌNG) Kiểm tra xem chúng ta đang ở trên Render hay không
IS_RENDER = os.environ.get('RENDER', 'False') == 'True'

if IS_RENDER:
    # === CÀI ĐẶT CHO PRODUCTION (TRÊN RENDER) ===
    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    
    # (KHỐI CẬP NHẬT)
    # Khởi tạo danh sách
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
    CSRF_TRUSTED_ORIGINS = []

    # 1. Đọc biến CSRF_TRUSTED_ORIGINS mà bạn đã set
    # (Giá trị là "https://streemly.onrender.com")
    trusted_origins_env = os.environ.get('CSRF_TRUSTED_ORIGINS')
    
    if trusted_origins_env:
        # Tách chuỗi nếu có nhiều giá trị
        origins = trusted_origins_env.split(',')
        
        # Thêm vào danh sách CSRF (cho lỗi 403)
        CSRF_TRUSTED_ORIGINS.extend(origins)
        
        # (SỬA) Thêm vào ALLOWED_HOSTS (cho lỗi DisallowedHost)
        for origin in origins:
            # Lấy hostname từ URL.
            # "https://streemly.onrender.com" -> "streemly.onrender.com"
            hostname = origin.replace('https://', '').split('/')[0]
            ALLOWED_HOSTS.append(hostname)

    # 2. (DỰ PHÒNG) Thêm cả biến RENDER_EXTERNAL_URL (do Render cung cấp)
    RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')
    if RENDER_EXTERNAL_URL:
        hostname = RENDER_EXTERNAL_URL.replace('https://', '').split('/')[0]
        if hostname not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(hostname)
        if RENDER_EXTERNAL_URL not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(RENDER_EXTERNAL_URL)

    # CSDL Production (PostgreSQL)
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }

    # Lớp Kênh Production (Redis)
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [os.environ.get('REDIS_URL')],
            },
        },
    }
    
    # Cấu hình file tĩnh cho Production (WhiteNoise)
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

else:
    # === CÀI ĐẶT CHO DEVELOPMENT (Ở MÁY LOCAL) ===
    # ... (Khối này giữ nguyên) ...
    SECRET_KEY = 'django-insecure-local-key-cho-development'
    DEBUG = True
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
    CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }
    STATIC_ROOT = BASE_DIR / 'staticfiles'
# === CÀI ĐẶT CHUNG (Cho cả hai môi trường) ===

INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'streaming',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'webrtc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = 'webrtc.asgi.application'

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_DIRS = [
    BASE_DIR / "streaming/static",
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'login_redirect' 
LOGOUT_REDIRECT_URL = 'welcome' 