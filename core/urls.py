from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from .views import most_attempted_categories
from .views import learner_analytics
from core.views import unread_notifications_json
from .views import all_notifications

from core.views import (
    unread_notifications_json,
    unread_notifications,
    mark_all_notifications_as_read,
    mark_notification_as_read,
)



urlpatterns = [
    # Home
    path('', views.homepage_view, name='home'),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

   # Profile routes (clean and correct)
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/dashboard/', views.profile_dashboard, name='profile_dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    #path('edit-profile/', views.edit_profile, name='edit_profile'),

    path('profile/delete/', views.delete_account, name='delete_account'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile_by_id'),
    path('edit-profile/', views.edit_profile, name='profile_edit'),
    path('profile/', views.profile_view, name='profile_view'),





    # Blog Posts
    path('blog/', views.post_list, name='blog'),
    path('posts/', views.post_list_view, name='post_list'),
    path('add-post/', views.add_post, name='add_post'),
    path('post/new/', views.post_create_view, name='post_create'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/like/', views.like_post_view, name='like_post'),
  


    # Comments & Replies
    path('comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    path('post/<int:post_id>/comment/<int:parent_id>/reply/', views.reply_to_comment, name='reply_to_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:comment_id>/replies/', views.load_replies, name='load_replies'),
    path('comment/<int:parent_id>/reply-form/', views.load_reply_form, name='load_reply_form'),
    path('like-reply/', views.like_reply, name='like_reply'),
    path('post/<int:post_pk>/comment/<int:parent_id>/reply/ajax/', views.add_reply_ajax, name='add_reply_ajax'),

    # Quizzes
    path('quiz/', views.quiz_category_list, name='quiz_category_list'),
    path('quiz/start/<int:category_id>/', views.start_quiz, name='start_quiz'),
    path('quiz/question/', views.quiz_question, name='quiz_question'),
    path('quiz/result/', views.quiz_result, name='quiz_result'),
    path('quiz/leaderboard/', views.quiz_leaderboard, name='quiz_leaderboard'),
    path('quiz/history/', views.quiz_history, name='quiz_history'),
    path('quizzes/', views.quiz_list_view, name='quiz_list'),
    path('analytics/most-attempted/', most_attempted_categories, name='most_attempted_categories'),
    path('analytics/learners/', learner_analytics, name='learner_analytics'),


        #notifications

    path('notifications/all/', views.all_notifications, name='all_notifications'),
    path('notifications/mark-all-read/', mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    path('notifications/', unread_notifications, name='notification_list'),  
    path('notifications/all/', all_notifications, name='all_notifications'),  
    path('notifications/unread/json/', unread_notifications_json, name='unread_notifications_json'),  
    path('notifications/unread/', unread_notifications, name='unread_notifications'),  
    path('notifications/mark/<int:notification_id>/', mark_notification_as_read, name='mark_notification_as_read'),
    path('notifications/mark_all/', mark_all_notifications_as_read, name='mark_all_notifications'),
    path('notifications/json/', unread_notifications_json, name='notifications-json'),
    path("notifications/json/", views.unread_notifications_json, name="unread_notifications_json"),
    path("notifications/", views.notifications, name="notifications"),
    path("notifications/unread/", views.unread_notifications, name="unread_notifications"),
    path("notifications/all/", views.all_notifications, name="all_notifications"),
    path("notifications/read/<int:notification_id>/", views.mark_notification_as_read, name="mark_notification_as_read"),
    path("notifications/mark-all-read/", views.mark_all_notifications_as_read, name="mark_all_notifications_as_read"),

    # Utilities
    path('search/', views.search_view, name='search'),
    path('support/', views.support_view, name='support'),
    path('post/<int:pk>/likes/', views.post_likes_list, name='post_likes_list'),


    #homework

    path('homework/', views.homework_list, name='homework_list'),
    path('homework/<int:homework_id>/submit/', views.submit_homework, name='submit_homework'),
    path('homework/my_submissions/', views.homework_submissions, name='homework_submissions'),
    path('homework/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    #path('homework/teacher/create/', views.create_homework, name='create_homework'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('my-graded-homework/', views.my_graded_homework, name='my_graded_homework'),

]

