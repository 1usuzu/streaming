from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # trang chủ chào mừng
    path('', views.welcome_page, name='welcome'), 
    
    # trang điều hướng sau khi đăng nhập
    path('login-redirect/', views.handle_login_redirect, name='login_redirect'),

    # trang Streamer
    path('stream/', views.index, name='stream_page'), 

    # Các đường dẫn xác thực
    path('login/', auth_views.LoginView.as_view(
            template_name='login.html', 
            redirect_authenticated_user=True
        ), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Các đường dẫn cũ
    path('viewer/', views.viewer_page, name='viewer_page'), 
    path('offer', views.offer, name='offer_api'),       
    path('viewer_connect', views.viewer, name='viewer_api'), 
]