# streaming/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # GET /viewer/ (trang HTML)
    # THÊM DẤU / Ở ĐÂY
    path('viewer/', views.viewer_page, name='viewer_page'), 
    
    # POST /offer (API) - Giữ nguyên không có dấu /
    path('offer', views.offer, name='offer_api'),       
    
    # POST /viewer_connect (API) - Giữ nguyên không có dấu /
    path('viewer_connect', views.viewer, name='viewer_api'), 
    
    # GET / (trang HTML)
    path('', views.index, name='index'),                
]