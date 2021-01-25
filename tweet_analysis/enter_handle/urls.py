from django.urls import path
from . import views

app_name = 'enter_handle'

urlpatterns = [
    path('', views.get_handle, name='get_handle'),
]
