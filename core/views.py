from datetime import date, timedelta
import random

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.utils import timezone
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.contrib.auth.models import User



# Models
from .models import (
    Profile,
    Post,
    Comment,
    Category,
    PostMedia,
    SupportInfo,
    SiteSettings,
    PDFDocument,
    QuizCategory,
    Question,
    QuizResult,
    DailyFact,
    Notification,
)

# Forms
from .forms import (
    RegisterForm,
    ProfileForm,
    UserForm,
    UserProfileForm,
    PostForm,
    CommentForm,
    PDFUploadForm,
)

# Utilities
from .utils import is_user_online


# Register user
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)  # Create empty profile
            messages.success(request, "Account created successfully.")
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "core/register.html", {"form": form})


# Login user
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "core/login.html")


# Logout user
def logout_view(request):
    logout(request)
    return redirect("login")


# Profile page
@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "core/profile.html", {"form": form})


@login_required
def post_create_view(request):
    if request.method == "POST":
        post_form = PostForm(request.POST)
        media_formset = PostMediaFormSet(
            request.POST, request.FILES, queryset=PostMedia.objects.none()
        )

        if post_form.is_valid() and media_formset.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()

            for form in media_formset.cleaned_data:
                if form:
                    PostMedia.objects.create(
                        post=post, image=form.get("image"), video=form.get("video")
                    )
            messages.success(request, "Post created!")
            return redirect("home")
    else:
        post_form = PostForm()
        media_formset = PostMediaFormSet(queryset=PostMedia.objects.none())

    return render(
        request,
        "core/post_create.html",
        {"post_form": post_form, "media_formset": media_formset},
    )


from django.core.paginator import Paginator


def post_list_view(request):
    query = request.GET.get("q")
    posts = Post.objects.all().order_by("-created")

    if query:
        posts = posts.filter(title__icontains=query)

    paginator = Paginator(posts, 6)  # Show 6 posts per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "core/post_list.html",
        {"posts": page_obj, "page_obj": page_obj},  # Use this in template
    )


# @login_required
# def like_post_view(request, pk):
#     post = get_object_or_404(Post, pk=pk)

#     if request.user in post.likes.all():
#         post.likes.remove(request.user)
#     else:
#         post.likes.add(request.user)

#     return redirect("post_detail", pk=pk)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils.timezone import now
from datetime import date

from .models import SiteSettings, Post, Comment, DailyFact, QuizCategory
from .forms import CommentForm
from django.contrib.auth.models import User

def homepage_view(request):
    settings = SiteSettings.objects.first()
    categories = QuizCategory.objects.all()[:4]
    all_posts = Post.objects.order_by("-created")
    paginator = Paginator(all_posts, 6)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)

    # Attach top-level comments to each post
    for post in posts:
        post.top_level_comments = post.comments.filter(parent__isnull=True)

    quiz_categories = QuizCategory.objects.all()
    today = date.today()
    daily_fact = DailyFact.objects.filter(date=today).first()
    all_users = User.objects.all().order_by('username')

    comment_form = CommentForm()

    return render(
        request,
        "core/home.html",
        {
            "settings": settings,
            "categories": categories,
            "posts": posts,
            "quiz_categories": quiz_categories,
            "daily_fact": daily_fact,
            "all_users": all_users,
            "comment_form": comment_form,
        },
    )


@login_required
def like_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        messages.info(request, "You unliked this post.")
    else:
        post.likes.add(request.user)
        messages.success(request, "You liked this post.")
    return redirect("home")


@login_required
def add_comment(request, post_id, parent_id=None):
    post = get_object_or_404(Post, id=post_id)
    parent_comment = get_object_or_404(Comment, id=parent_id) if parent_id else None

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.parent = parent_comment
            comment.approved = True
            comment.save()

    return redirect("home")  


@login_required
def add_reply(request, pk, comment_id):
    post = get_object_or_404(Post, pk=pk)
    parent_comment = get_object_or_404(Comment, pk=comment_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = post
            reply.parent = parent_comment
            reply.name = request.user.username
            reply.save()
            messages.success(request, "Reply posted!")
        else:
            messages.error(request, "Failed to post reply.")
    return redirect("home")




def pdf_list_view(request):
    pdfs = PDFDocument.objects.order_by("-uploaded_at")
    return render(request, "core/pdf_list.html", {"pdfs": pdfs})


@login_required
def pdf_upload_view(request):
    if request.method == "POST":
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf = form.save(commit=False)
            pdf.uploaded_by = request.user
            pdf.save()
            return redirect("pdf_list")
    else:
        form = PDFUploadForm()
    return render(request, "core/pdf_upload.html", {"form": form})


@login_required
def profile_dashboard(request):
    user = request.user
    profile = user.profile
    user_posts = Post.objects.filter(author=user)
    quiz_attempts = user.quizresult_set.all().order_by("-taken_at")

    return render(
        request,
        "core/profile_dashboard.html",
        {
            "profile_user": user,
            "profile": profile,
            "user_posts": user_posts,
            "quiz_result": quiz_attempts,
        },
    )


@login_required
def edit_profile(request):
    user = request.user
    profile = user.profile
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("profile_dashboard")
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    return render(
        request,
        "core/edit_profile.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


@login_required
def delete_account(request):
    if request.method == "POST":
        request.user.delete()
        return redirect("home")
    return render(request, "core/delete_account.html")


def support_view(request):
    support = SupportInfo.objects.first()
    return render(request, "core/support.html", {"support": support})


@login_required
def quiz_category_list(request):
    categories = QuizCategory.objects.all()
    return render(request, "quiz/category_list.html", {"categories": categories})


@login_required
def start_quiz(request, category_id):
    category = QuizCategory.objects.get(id=category_id)
    questions = list(Question.objects.filter(category=category))
    selected_questions = random.sample(questions, min(len(questions), 10))

    request.session["quiz"] = {
        "category_id": category.id,
        "question_ids": [q.id for q in selected_questions],
        "current": 0,
        "score": 0,
        "answers": [],
        "start_time": timezone.now().isoformat(),
    }

    return redirect("quiz_question")


@login_required
def quiz_question(request):
    quiz = request.session.get("quiz")
    if not quiz or quiz["current"] >= len(quiz["question_ids"]):
        return redirect("quiz_result")

    question_id = quiz["question_ids"][quiz["current"]]
    question = Question.objects.get(id=question_id)

    if request.method == "POST":
        selected = request.POST.get("choice")
        correct = question.correct_answer

        is_correct = selected == correct
        quiz["score"] += 1 if is_correct else 0
        quiz["answers"].append(
            {
                "id": question.id,
                "selected": selected,
                "correct": correct,
                "explanation": question.explanation,
            }
        )
        quiz["current"] += 1
        request.session["quiz"] = quiz

        return redirect("quiz_question")

    return render(
        request,
        "quiz/question.html",
        {
            "question": question,
            "current": quiz["current"] + 1,
            "total": len(quiz["question_ids"]),
        },
    )


@login_required
def quiz_result(request):
    quiz = request.session.pop("quiz", None)
    if not quiz:
        return redirect("quiz_category_list")

    category = get_object_or_404(QuizCategory, id=quiz["category_id"])
    total_questions = len(quiz["question_ids"])
    score = quiz["score"]
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0

    # Badge logic
    if percentage >= 90:
        remarks, badge, badge_class, emoji = (
            "🏅 Excellent work! You're a quiz champion! 🎉 Keep shining!",
            "Gold Medal",
            "badge bg-warning text-dark",
            "🥇",
        )
    elif percentage >= 70:
        remarks, badge, badge_class, emoji = (
            "👍 Great job! You're on the right path! ✨",
            "Silver Medal",
            "badge bg-secondary",
            "🥈",
        )
    elif percentage >= 50:
        remarks, badge, badge_class, emoji = (
            "🙂 Good effort! Keep learning and growing! 📚",
            "Bronze Medal",
            "badge bg-info text-dark",
            "🥉",
        )
    else:
        remarks, badge, badge_class, emoji = (
            "😕 Don't worry, practice makes perfect! 💪 You got this!",
            "No Badge",
            "badge bg-danger",
            "❌",
        )

    # Save quiz result
    QuizResult.objects.create(
        user=request.user,
        category=category,
        score=score,
        percentage=percentage,
        total_questions=total_questions,
        total=total_questions,
    )

    # Prepare question data for the template
    question_ids = [ans["id"] for ans in quiz["answers"]]
    questions = Question.objects.in_bulk(question_ids)

    question_texts = []
    for ans in quiz["answers"]:
        question = questions.get(ans["id"])
        if question:
            question_texts.append(
                {
                    "text": question.text,
                    "selected": ans["selected"],
                    "correct": ans["correct"],
                    "explanation": ans["explanation"],
                }
            )

    quiz_title = f"Quiz Results for {category.name}"

    return render(
        request,
        "quiz/result.html",
        {
            "score": score,
            "total": total_questions,
            "percentage": percentage,
            "remarks": remarks,
            "badge": badge,
            "badge_class": badge_class,
            "emoji": emoji,
            "answers": question_texts,
            "category": category,
            "total_questions": total_questions,
            "quiz_title": quiz_title,
        },
    )
from django.db.models import Sum, Count
from django.contrib.auth.models import User

def quiz_leaderboard(request):
    leaderboard = (
        User.objects.filter(quizresult__isnull=False)
        .annotate(total_score=Sum("quizresult__score"), attempts=Count("quizresult"))
        .order_by("-total_score", "username")
    )

    badges = [
        ("🥇", "Gold"),
        ("🥈", "Silver"),
        ("🥉", "Bronze"),
        ("🏅", "Top4"),
        ("🎖️", "Top5"),
    ]

    leaderboard_with_badges = []
    for idx, user in enumerate(leaderboard, start=1):
        badge = ""
        emoji = ""
        if idx <= 5:
            emoji, badge = badges[idx - 1]

        # Use `photo` instead of `avatar`
        photo_url = "/static/img/avatar-placeholder.png"
        if hasattr(user, "profile") and getattr(user.profile, "photo", None):
            try:
                photo_url = user.profile.photo.url
            except:
                pass

        leaderboard_with_badges.append({
            "rank": idx,
            "username": user.username,
            "photo_url": photo_url,
            "total_score": user.total_score,
            "attempts": user.attempts,
            "badge": badge,
            "emoji": emoji,
        })

    return render(request, "quiz/leaderboard.html", {"leaderboard": leaderboard_with_badges})




def quiz_history(request):
    raw_history = QuizResult.objects.filter(user=request.user).order_by("-date_taken")
    paginator = Paginator(raw_history, 10)  # 10 attempts per page
    page_number = request.GET.get("page")
    history_page = paginator.get_page(page_number)

    formatted_history = []
    for attempt in history_page:
        percentage = (
            (attempt.score / attempt.total_questions) * 100
            if attempt.total_questions
            else 0
        )
        total_seconds = attempt.time_used_seconds or 0
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        formatted_history.append(
            {
                "date_taken": attempt.date_taken,
                "category__name": attempt.category.name,
                "score": attempt.score,
                "total_questions": attempt.total_questions,
                "percentage": percentage,
                "minutes": minutes,
                "seconds": seconds,
            }
        )

    history_page.object_list = formatted_history

    return render(request, "quiz/history.html", {"history": history_page})


def search_view(request):
    query = request.GET.get("q")
    results = []
    if query:

        from .models import Post

        results = Post.objects.filter(title__icontains=query)
    return render(
        request, "core/search_results.html", {"query": query, "results": results}
    )


@login_required
def add_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm()
    return render(request, "blog/add_post.html", {"form": form})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to edit this post.")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = PostForm(instance=post)

    return render(request, "edit_post.html", {"form": form})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    if request.method == "POST":
        post.delete()
        return redirect("home")

    return render(request, "confirm_delete.html", {"post": post})


from django.core.paginator import Paginator


def post_list(request):
    posts = Post.objects.filter(status="published").order_by("-created_at")
    paginator = Paginator(posts, 6)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/post_list.html", {"page_obj": page_obj})


def online_users_view(request):
    users = User.objects.all()
    online_users = [user for user in users if is_user_online(user)]
    return render(request, "online_users.html", {"online_users": online_users})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from .forms import CommentForm


# @login_required
# def add_comment(request, post_id, parent_id=None):
#     post = get_object_or_404(Post, id=post_id)
#     parent_comment = get_object_or_404(Comment, id=parent_id) if parent_id else None

#     if request.method == "POST":
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.post = post
#             comment.user = request.user
#             comment.parent = parent_comment
#             comment.approved = True
#             comment.save()

#     return redirect("home", pk=post.id)


@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)

    return redirect("home")


from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from .forms import CommentForm

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    session_key = f'viewed_post_{post.pk}'
    if not request.session.get(session_key, False):
        post.views += 1
        post.save()
        request.session[session_key] = True

    comments = Comment.objects.filter(post=post, approved=True).select_related('user', 'parent').prefetch_related('replies', 'likes')
    top_level_comments = comments.filter(parent__isnull=True).order_by('-created')

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id)
                    new_comment.parent = parent_comment
                except Comment.DoesNotExist:
                    pass
            new_comment.save()
            return redirect('core/post_detail', pk=post.pk)
    else:
        comment_form = CommentForm()

    context = {
        "post": post,
        "top_level_comments": top_level_comments,
        "top_level_comment_count": top_level_comments.count(),
        "comment_form": comment_form,
        "comments": comments,
    }

    return render(request, "core/post_detail.html", context)




def download_post_pdf(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    template_path = "core/post_pdf.html"
    context = {"post": post}
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="post_{post_id}.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    return response


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated successfully.")
            return redirect("post_detail", pk=comment.post.id)
    else:
        form = CommentForm(instance=comment)

    return render(request, "core/edit_comment.html", {"form": form, "comment": comment})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    post_id = comment.post.id
    comment.delete()
    messages.success(request, "Comment deleted.")
    return redirect("post_detail", pk=post_id)


def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=profile_user, status="published").order_by(
        "-created"
    )
    quiz_attempts = QuizResult.objects.filter(user=profile_user).order_by("-date_taken")

    return render(
        request,
        "core/user_profile.html",
        {
            "profile_user": profile_user,
            "user_posts": user_posts,
            "quiz_attempts": quiz_attempts,
        },
    )

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Comment, Post, Notification

@login_required
def reply_to_comment(request, post_id, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        if body:
            reply = Comment.objects.create(
                user=request.user,
                post=post,
                body=body,
                parent=parent_comment
            )

            if parent_comment.user != request.user:
                Notification.objects.create(
                    user=parent_comment.user,
                    message=f"{request.user.username} replied to your comment.",
                    url=f"/post/{post.id}#comment-{reply.id}",
                    tone="reply_sound.mp3",
                )

            return redirect(f"{reverse('home', kwargs={'pk': post.id})}#comment-{reply.id}")

    return redirect("home", pk=post.id)


def notifications(request):
    return render(request, "notifications.html")


def is_root(self):
    return self.parent is None


# admin_views.py
def user_analytics(request):
    user_data = User.objects.annotate(
        total_quizzes=Count("userquizhistory"), most_played=Subquery(...)
    )
    return render(request, "admin/user_analytics.html", {"data": user_data})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from .models import Notification


# =============================
# 🔔 UNREAD NOTIFICATIONS (JSON)
# =============================
@login_required
def unread_notifications_json(request):
    notifications = Notification.objects.filter(
        user=request.user, is_read=False
    ).select_related("sender", "post")

    data = []
    for n in notifications:
        message = (
            f"{n.sender.username} {n.verb} your post '{n.post.title if n.post else ''}'"
        )
        url = reverse("mark_notification_as_read", args=[n.id])  # 🔁 this view will mark as read
        data.append({
            "id": n.id,
            "message": message,
            "url": url,
            "tone": n.tone,
        })

    return JsonResponse(data, safe=False)


# =============================
# 📥 UNREAD NOTIFICATIONS (HTML)
# =============================
@login_required
def unread_notifications(request):
    """
    Display and auto-mark all unread notifications as read.
    """
    notifications = Notification.objects.filter(
        user=request.user, is_read=False
    ).select_related("sender", "post")

    # Mark them as read after displaying
    notifications.update(is_read=True)

    return render(
        request, "notifications/unread.html", {"notifications": notifications}
    )


# =============================
# 📚 ALL NOTIFICATIONS (Read + Unread)
# =============================
@login_required
def all_notifications(request):
 
    notifications = (
        Notification.objects.filter(user=request.user)
        .select_related("sender", "post")
        .order_by("-created_at")
    )
    return render(request, "notifications/all.html", {"notifications": notifications})


# =============================
# ☑️ MARK SINGLE NOTIFICATION AS READ
# =============================
@login_required
def mark_notification_as_read(request, notification_id):
    """
    Mark a specific notification as read and redirect to related post or fallback.
    """
    notification = get_object_or_404(
        Notification, id=notification_id, user=request.user
    )
    notification.is_read = True
    notification.save()

    redirect_url = (
        notification.post.get_absolute_url()
        if notification.post
        else reverse("unread_notifications")
    )
    return redirect(redirect_url)


# =============================
# 🧹 MARK ALL AS READ (Button)
# =============================
@login_required
def mark_all_notifications_as_read(request):
    """
    Mark all unread notifications as read.
    """
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect("unread_notifications")


def quiz_list_view(request):
    # logic here
    return render(request, "quiz/quiz_list.html")


from django.shortcuts import get_object_or_404, render
from .models import Comment


def load_replies(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    replies = (
        comment.replies.all()
        .select_related("user", "user__profile")
        .order_by("created_at")
    )
    context = {
        "replies": replies,
        "post": comment.post,
        "user": request.user,
        "depth": 4,
    }
    return render(request, "partials/replies.html", context)


# views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Reply


@login_required
@require_POST
def like_reply(request):
    reply_id = request.POST.get("reply_id")
    reply = get_object_or_404(Reply, id=reply_id)

    if request.user in reply.likes.all():
        reply.likes.remove(request.user)
        liked = False
    else:
        reply.likes.add(request.user)
        liked = True

    return JsonResponse(
        {
            "liked": liked,
            "total_likes": reply.likes.count(),
        }
    )
