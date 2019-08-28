from django.urls import path
from core import views

app_name = 'core'

urlpatterns =[
    path('', views.items_list, name='items_list'),
]