from django.urls import path
from . import views
from .views import post_list_view
from .views import online_users_view
urlpatterns = [
    path('', views.homepage_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    #path('blog/', post_list_view, name='blog'),
    path('post/new/', views.post_create_view, name='post_create'),
    path('post/<int:pk>/', views.post_detail_view, name='post_detail'),
    path('post/<int:pk>/like/', views.like_post_view, name='like_post'),

    path('pdfs/', views.pdf_list_view, name='pdf_list'),
    path('pdfs/upload/', views.pdf_upload_view, name='pdf_upload'),

    path('profile/dashboard/', views.profile_dashboard, name='profile_dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/delete/', views.delete_account, name='delete_account'),

    path('support/', views.support_view, name='support'),

    path('quiz/', views.quiz_category_list, name='quiz_category_list'),
    path('quiz/start/<int:category_id>/', views.start_quiz, name='start_quiz'),
    path('quiz/question/', views.quiz_question, name='quiz_question'),
    path('quiz/result/', views.quiz_result, name='quiz_result'),
    path('quiz/leaderboard/', views.quiz_leaderboard, name='quiz_leaderboard'),
    path('quiz/history/', views.quiz_history, name='quiz_history'),
    path('search/', views.search_view, name='search'),
    path('add-post/', views.add_post, name='add_post'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('blog/', views.post_list, name='blog'),
    path('online-users/', online_users_view, name='online_users'),

]
