from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='trade_map-home'),
    path('about/', views.about, name='map-about'),
]
