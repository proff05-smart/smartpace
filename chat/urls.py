from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'), 
    path('chat/<str:username>/', views.chat_view, name='chat_view'),  
    path('search/', views.user_search, name='user_search'), 
    path('users/', views.user_list, name='user_list'), 
    path('chat/fetch/<str:username>/', views.fetch_messages, name='fetch_messages'),
 
]
