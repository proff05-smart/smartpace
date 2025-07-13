from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView




urlpatterns = [
    # Authentication and user profile
    path('', views.homepage_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/logout/', LogoutView.as_view(next_page='login'), name='logout'),
   

    path('profile/', views.profile_view, name='profile'),
    path('profile/dashboard/', views.profile_dashboard, name='profile_dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/delete/', views.delete_account, name='delete_account'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),

    # Blog posts
    path('blog/', views.post_list, name='blog'),
    path('posts/', views.post_list_view, name='post_list'),
    path('add-post/', views.add_post, name='add_post'),
    path('post/new/', views.post_create_view, name='post_create'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/like/', views.like_post_view, name='like_post'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/download/', views.download_post_pdf, name='download_post_pdf'),
    path('comment/add/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/replies/', views.load_replies, name='load_replies'),
    path('like-reply/', views.like_reply, name='like-reply'),
    # urls.py
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),





    # Comments
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/comment/<int:parent_id>/reply/', views.add_comment, name='reply_comment'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),


    # AJAX comment (replies and new)
    #path('post/<int:post_id>/comment/ajax/', views.ajax_add_comment, name='ajax_add_comment'),
    #path('post/<int:post_id>/comment/reply/', views.ajax_reply_comment, name='ajax_reply_comment'),
    #path('ajax/reply/<int:post_id>/<int:comment_id>/', views.ajax_add_reply, name='ajax_add_reply'),  # Uncomment only if view exists

    # PDFs
    path('pdfs/', views.pdf_list_view, name='pdf_list'),
    path('pdfs/upload/', views.pdf_upload_view, name='pdf_upload'),

    # Quizzes
    path('quiz/', views.quiz_category_list, name='quiz_category_list'),
    path('quiz/start/<int:category_id>/', views.start_quiz, name='start_quiz'),
    path('quiz/question/', views.quiz_question, name='quiz_question'),
    path('quiz/result/', views.quiz_result, name='quiz_result'),
    path('quiz/leaderboard/', views.quiz_leaderboard, name='quiz_leaderboard'),
    path('quiz/history/', views.quiz_history, name='quiz_history'),
    path('quizzes/', views.quiz_list_view, name='quiz_list'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),


    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/unread/', views.unread_notifications, name='unread_notifications'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('notifications/read-all/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    path('notifications/json/', views.unread_notifications_json, name='unread_notifications_json'),
    path('notifications/all/', views.all_notifications, name='all_notifications'),
    path('notifications/mark/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read_alt'),
    path('notifications/mark_all/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read_alt'),

    # Others
    path('search/', views.search_view, name='search'),
    path('support/', views.support_view, name='support'),
    path('online-users/', views.online_users_view, name='online_users'),
    path("like-reply/", views.like_reply, name="like_reply"),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    #path("post/<int:post_id>/comment/<int:parent_id>/reply/", views.reply_comment, name="reply_comment"),
    #path("post/<int:post_id>/comment/<int:parent_id>/reply/", views.reply_to_comment, name="reply_comment"),
    path("comment/<int:comment_id>/replies/", views.load_replies, name="load_replies"),
    path('post/<int:post_id>/comment/<int:comment_id>/reply/', views.reply_to_comment, name='reply_comment'),
    #path("post/<int:post_id>/comment/<int:parent_id>/reply/", views.reply_comment, name="reply_comment"),
    path("post/<int:post_id>/comment/<int:comment_id>/reply/", views.reply_to_comment, name="reply_to_comment"),
    # core/urls.py or users/urls.py


    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/comment/<int:parent_id>/reply/', views.add_comment, name='reply_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
   # path('profile/edit/', views.profile_edit, name='profile_edit'),
   # path('profile/edit/', views.edit_profile, name='profile_edit'), 
    path('profile/edit/', views.profile_view, name='profile_edit'),
 # ✅ Correct name and function


    path("notifications/unread/", views.unread_notifications, name="unread_notifications"),
    path("notifications/mark/<int:notification_id>/", views.mark_notification_as_read, name="mark_notification_as_read"),
    path("notifications/mark-all/", views.mark_all_notifications_as_read, name="mark_all_notifications_as_read"),
    #path('unread-notifications/json/', unread_notifications_json, name='unread_notifications_json'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/comment/<int:comment_id>/reply/', views.reply_to_comment, name='reply_to_comment'),
    path('post/<int:pk>/like/', views.like_post_view, name='like_post'),
    path('post/<int:pk>/download/', views.download_post_pdf, name='download_post_pdf'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    # urls.py
    path("post/<int:post_id>/comment/<int:comment_id>/reply/", views.reply_to_comment, name="reply_to_comment"),
    # urls.py
    path("post/<int:post_id>/comment/<int:comment_id>/reply/", views.reply_to_comment, name="reply_to_comment"),
    path("post/<int:post_id>/comment/<int:comment_id>/reply/", views.reply_to_comment, name="reply_to_comment"),
    path('post/<int:post_id>/comment/<int:comment_id>/reply/', views.reply_to_comment, name='reply_to_comment'),
    path('', views.homepage_view, name='home'),
    path('post/<int:pk>/like/', views.like_post_view, name='like_post'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:pk>/comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    path('reply/<int:comment_id>/', views.add_reply, name='add_reply'),



# Post views
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    #path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/download/', views.download_post_pdf, name='download_post_pdf'),

    # Commenting
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:pk>/comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),

    # Comment management
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:comment_id>/replies/', views.load_replies, name='load_replies'),
    

    # path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    # path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    # path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # # Custom register view (optional)
    # path('accounts/register/', views.register, name='register'),













]




    









