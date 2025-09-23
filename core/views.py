# Standard library
from datetime import date, timedelta
import random
import hashlib
import json


# Django / third-party
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.http import (
    JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
)
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import (
    authenticate, login, logout, get_user_model
)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import (
    F, Q, Sum, Count, Avg, OuterRef, Subquery
)
from django.template.loader import get_template
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.http import require_POST
from xhtml2pdf import pisa
import cloudinary.uploader
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory

from .utils import is_user_online
from .models import (
    Profile, Post, Comment, Category, PostMedia, SupportInfo, SiteSettings,
    PDFDocument, QuizCategory, Question, QuizResult, DailyFact, Notification,
    Homework, HomeworkSubmission, HomeworkSubmissionImage,
    DailyQuote, Reaction, DailyQuiz, DailyQuizAttempt
)
from .forms import (
    RegisterForm, ProfileForm, UserForm, UserProfileForm,
    PostForm, PostMediaForm, CommentForm, PDFUploadForm,
    HomeworkForm, HomeworkSubmissionForm, HomeworkSubmissionImageForm,
    TeacherMarkingForm, SelectGroupForm, UserLoginForm
)
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Notification

DEFAULT_PHOTO_URL = "https://res.cloudinary.com/dwp0xtvyb/image/upload/v123456789/default_profile.png"



def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            messages.success(request, "Account created successfully.")
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "core/register.html", {"form": form})


def login_view(request):
    form = UserLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  
        else:
            form.add_error(None, 'Invalid username or password')
    return render(request, 'login.html', {'form': form})

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("profile_view")  
    else:
        form = ProfileForm(instance=profile)

    return render(request, "core/profile.html", {"form": form})




PostMediaFormSet = modelformset_factory(PostMedia, form=PostMediaForm, extra=5)

@login_required
def post_create_view(request):
    if request.method == "POST":
        post_form = PostForm(request.POST, request.FILES)
        media_formset = PostMediaFormSet(request.POST, request.FILES, queryset=PostMedia.objects.none())
        if post_form.is_valid() and media_formset.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()
            for form in media_formset.cleaned_data:
                if form:
                    image = form.get("image")
                    video = form.get("video")
                    if image or video:
                        PostMedia.objects.create(post=post, image=image, video=video)

            messages.success(request, "Post created successfully!")
            return redirect("home")
    else:
        post_form = PostForm()
        media_formset = PostMediaFormSet(queryset=PostMedia.objects.none())

    return render(
        request,
        "core/post_create.html",
        {"post_form": post_form, "media_formset": media_formset}, )



   

@login_required
def post_likes_list(request, pk):
    post = get_object_or_404(Post, pk=pk)
    users = post.likes.all()
    return render(request, 'post_likes_list.html', {'post': post, 'users': users})


    
def homepage_view(request):
    settings = SiteSettings.objects.first()
    quiz_categories = QuizCategory.objects.all()
    categories = quiz_categories[:4]

    all_posts = (
        Post.objects.filter(status="published")
        .prefetch_related("comments")
        .order_by("-created")
    )
    paginator = Paginator(all_posts, 25)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)

    # Build a dictionary of top-level comments keyed by post id
    comments_map = {
        p.pk: p.comments.filter(parent__isnull=True).order_by("-created")
        for p in posts
    }

    today = date.today()
    daily_fact = DailyFact.objects.filter(date=today).first()

    quotes = list(DailyQuote.objects.all())
    if quotes:
        hash_val = int(hashlib.sha256(today.isoformat().encode()).hexdigest(), 16)
        daily_quote = quotes[hash_val % len(quotes)]
    else:
        daily_quote = None

    daily_quiz = DailyQuiz.get_today_quiz()
    all_users = User.objects.order_by("username")
    comment_form = CommentForm()

    reaction_counts = {
        post.pk: {
            key: post.reactions.filter(reaction_type=key).count()
            for key, _ in Reaction.REACTION_CHOICES
        }
        for post in posts
    }

    return render(
        request,
        "core/home.html",
        {
            "settings": settings,
            "categories": categories,
            "posts": posts,
            "quiz_categories": quiz_categories,
            "daily_fact": daily_fact,
            "daily_quote": daily_quote,
            "daily_quiz": daily_quiz,
            "all_users": all_users,
            "comment_form": comment_form,
            "reaction_counts": reaction_counts,
            "comments_map": comments_map,
        },
    )



@login_required
def like_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'total_likes': post.likes.count(),
        'message': "Liked" if liked else "Unliked"
    })



@login_required
def toggle_like_ajax(request):
    data = json.loads(request.body)
    post_id = data.get("post_id")
    post = Post.objects.get(pk=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return JsonResponse({
        "liked": liked,
        "likes_count": post.likes.count()
    })


@login_required
def load_reply_form(request, parent_id):
    """
    Renders a reply form via AJAX when user clicks 'Reply'.
    """
    comment = get_object_or_404(Comment, id=parent_id)
    form = CommentForm()

    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return HttpResponse(status=403)

    html = render_to_string(
        'partials/reply_form.html',
        {'form': form, 'post': comment.post, 'parent': comment},
        request=request
    )
    return HttpResponse(html)





@login_required
def profile_dashboard(request):
    user = request.user
    profile = user.profile
    user_posts = Post.objects.filter(author=user)
    quiz_results = user.quizresult_set.select_related("quiz").order_by("-taken_at")

    return render(
        request,
        "core/profile_dashboard.html",
        {
            "profile_user": user,
            "profile": profile,
            "user_posts": user_posts,
            "quiz_results": quiz_results,
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

   
    QuizResult.objects.create(
        user=request.user,
        category=category,
        score=score,
        percentage=percentage,
        total_questions=total_questions,
        total=total_questions,
    )

    
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

@login_required
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



@login_required

def quiz_history(request):
    raw_history = QuizResult.objects.filter(user=request.user).order_by("-date_taken")
    paginator = Paginator(raw_history, 10) 
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

def post_list(request):
    query = request.GET.get("q", "")
    posts = Post.objects.all().order_by("-created_at")  

    if query:
        posts = posts.filter(title__icontains=query)

    paginator = Paginator(posts, 25)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "posts": page_obj,
        "page_obj": page_obj,
        "query": query,
        "total_results": posts.count(),
    }

    return render(request, "core/post_list.html", context)



from django.shortcuts import redirect, get_object_or_404
from .models import Comment

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "home"
    return redirect(next_url)
    
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    session_key = f'viewed_post_{post.pk}'
    if not request.session.get(session_key, False):
        post.views += 1
        post.save()
        request.session[session_key] = True

    comments = Comment.objects.filter(post=post, approved=True)\
        .select_related('user', 'parent').prefetch_related('replies', 'likes')
    top_level_comments = comments.filter(parent__isnull=True).order_by('-created')

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')
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
            return redirect('home')  # <— redirect to home
    else:
        comment_form = CommentForm()

    context = {
        "post": post,
        "top_level_comments": top_level_comments,
        "top_level_comment_count": top_level_comments.count(),
        "comment_form": comment_form,
        "comments": comments,
    }

    return render(request, "post_detail.html", context)

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
@login_required
def add_comment(request, post_id, parent_id=None):
    post = get_object_or_404(Post, pk=post_id)
    parent_comment = get_object_or_404(Comment, pk=parent_id) if parent_id else None

    # Handle JSON (AJAX) request
    if request.content_type == "application/json":
        try:
            data = json.loads(request.body)
            body = data.get("body", "").strip()
            if not body:
                return JsonResponse({"success": False, "error": "Comment cannot be empty."}, status=400)

            comment = Comment.objects.create(
                post=post,
                user=request.user,
                body=body,
                parent=parent_comment,
                approved=True
            )

            if parent_comment and parent_comment.user != request.user:
                Notification.objects.create(
                    user=parent_comment.user,
                    sender=request.user,
                    verb="replied to",
                    post=post,
                    comment=comment,
                    tone="info"
                )

            html = render_to_string("partials/comment_item.html", {"comment": comment, "post": post}, request=request)
            return JsonResponse({"success": True, "html": html, "comment_id": comment.id})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    # Handle standard form submission
    else:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.parent = parent_comment
            comment.approved = True
            comment.save()

            if parent_comment and parent_comment.user != request.user:
                Notification.objects.create(
                    user=parent_comment.user,
                    sender=request.user,
                    verb="replied to",
                    post=post,
                    comment=comment,
                    tone="info"
                )

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                html = render_to_string("partials/comment_item.html", {"comment": comment, "post": post}, request=request)
                return JsonResponse({"success": True, "html": html, "comment_id": comment.id})

            next_url = request.POST.get("next")
            return redirect(next_url or f"{reverse('post_detail', kwargs={'pk': post.id})}#comment-{comment.id}")

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
        messages.error(request, "There was an error posting your comment.")
        return redirect("home")




@login_required
# admin_views.py
def user_analytics(request):
    user_data = User.objects.annotate(
        total_quizzes=Count("userquizhistory"), most_played=Subquery(...)
    )
    return render(request, "admin/user_analytics.html", {"data": user_data})





def quiz_list_view(request):
    # logic here
    return render(request, "quiz/quiz_list.html")



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






@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def most_attempted_categories(request):
    category_stats = (
        QuizCategory.objects
        .annotate(attempts=Count('quizresult'))
        .order_by('-attempts')
    )
    return render(request, 'analytics/most_attempted.html', {'category_stats': category_stats})




User = get_user_model()

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def learner_analytics(request):
    learners = (
        User.objects
        .filter(quizresult__isnull=False)
        .annotate(
            total_attempts=Count('quizresult'),
            average_score=Avg('quizresult__score')
        )
        .order_by('-total_attempts')
    )
    return render(request, 'analytics/learner_analytics.html', {'learners': learners})




@login_required
def homework_list(request):
    if request.user.is_staff:
        homeworks = Homework.objects.all().order_by('-created_at')
    else:
        user_groups = request.user.groups.all()
        homeworks = Homework.objects.filter(assigned_to__in=user_groups).distinct().order_by('-created_at')
    return render(request, 'homework/homework_list.html', {'homeworks': homeworks})
    


@login_required
def submit_homework(request, homework_id):
    homework = get_object_or_404(Homework, id=homework_id)

    can_submit = timezone.now() <= homework.due_date

    try:
        submission = HomeworkSubmission.objects.get(homework=homework, student=request.user)
        is_editing = True
    except HomeworkSubmission.DoesNotExist:
        submission = None
        is_editing = False

    ImageFormSet = modelformset_factory(
        HomeworkSubmissionImage,
        form=HomeworkSubmissionImageForm,
        extra=3,
        can_delete=False
    )

    if request.method == 'POST':
        if not can_submit:
            messages.error(request, "Sorry, the submission deadline has passed.")
            return redirect('homework_list')

        form = HomeworkSubmissionForm(request.POST, request.FILES, instance=submission)
        formset = ImageFormSet(request.POST, request.FILES, queryset=HomeworkSubmissionImage.objects.none())

        if form.is_valid() and formset.is_valid():
            sub = form.save(commit=False)
            sub.homework = homework
            sub.student = request.user
            sub.save()

            # Save uploaded images
            for image_form in formset.cleaned_data:
                if image_form and image_form.get('image'):
                    HomeworkSubmissionImage.objects.create(
                        submission=sub,
                        image=image_form['image']
                    )

            # Notify staff
            from django.contrib.auth.models import User
            staff_users = User.objects.filter(is_staff=True)
            for staff in staff_users:
                Notification.objects.create(
                    user=staff,
                    sender=request.user,
                    verb=f"{request.user.get_full_name() or request.user.username} submitted homework: {homework.title}",
                    tone="info"
                )

            messages.success(request, "Submission updated successfully." if is_editing else "Homework submitted successfully.")
            return redirect('homework_list')
    else:
        form = HomeworkSubmissionForm(instance=submission)
        formset = ImageFormSet(queryset=HomeworkSubmissionImage.objects.none())

    return render(request, 'homework/submit_homework.html', {
        'form': form,
        'formset': formset,
        'homework': homework,
        'is_editing': is_editing,
        'can_submit': can_submit,
        'due_date_js': homework.due_date.strftime("%Y-%m-%dT%H:%M:%S")  # For JS countdown
    })




@login_required
def homework_submissions(request):
    submissions = HomeworkSubmission.objects.filter(student=request.user).order_by('-submitted_at')
    return render(request, 'homework/homework_submissions.html', {'submissions': submissions})

@user_passes_test(lambda u: u.is_staff)
def teacher_dashboard(request):
    homeworks = Homework.objects.all().order_by('-created_at')
    return render(request, 'homework/teacher_dashboard.html', {'homeworks': homeworks})
@user_passes_test(lambda u: u.is_staff)



@login_required
def create_homework(request):
    if request.method == 'POST':
        form = HomeworkForm(request.POST, request.FILES)
        if form.is_valid():
            homework = form.save(commit=False)

            pdf_file = request.FILES.get('pdf_file')  
            if pdf_file:
                try:
                    upload_result = cloudinary.uploader.upload(
                        pdf_file,
                        resource_type="raw",  
                        format="pdf", 
                        folder="homeworks"
                    )
                    homework.pdf_file = upload_result.get('secure_url')
                except Exception as e:
                    messages.error(request, f"File upload failed: {e}")
                    return render(request, 'homework/create_homework.html', {'form': form})

            homework.save()

            # Notify students
            for group in homework.assigned_to.all():
                for student in group.user_set.all():
                    Notification.objects.create(
                        user=student,
                        sender=request.user,
                        verb=f"New homework assigned: {homework.title}",
                        tone="warning"
                    )

            messages.success(request, "Homework created successfully.")
            return redirect('teacher_dashboard')
    else:
        form = HomeworkForm()

    return render(request, 'homework/create_homework.html', {'form': form})




@login_required
def my_graded_homework(request):
    submissions = HomeworkSubmission.objects.filter(student=request.user, is_graded=True)
    return render(request, 'homework/my_graded_homework.html', {'submissions': submissions})



@login_required
def select_group_view(request):
    user = request.user

    if request.method == 'POST':
        form = SelectGroupForm(request.POST)
        if form.is_valid():
            selected_group = form.cleaned_data['group']
            user.groups.clear()
            user.groups.add(selected_group)
            messages.success(request, f"You have been assigned to {selected_group.name}.")
            return redirect('home')  
    else:
        form = SelectGroupForm()

    return render(request, 'select_group.html', {'form': form})
@staff_member_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(HomeworkSubmission, id=submission_id)

    if request.method == 'POST':
        form = TeacherMarkingForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()

            # Notify the student that their homework has been graded
            Notification.objects.create(
                user=submission.student,
                sender=request.user,
                verb=f"Your homework '{submission.homework.title}' has been graded.",
                tone="success"
            )

            return redirect('view_submissions', homework_id=submission.homework.id)
    else:
        form = TeacherMarkingForm(instance=submission)

    homework = submission.homework
    return render(request, 'homework/grade_submission.html', {
        'form': form,
        'submission': submission,
        'homework': homework,
    })


from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def view_submissions(request, homework_id):
    homework = get_object_or_404(Homework, id=homework_id)
    submissions = homework.submissions.select_related('student').all()
    return render(request, 'homework/view_submissions.html', {
        'homework': homework,
        'submissions': submissions,
    })

@staff_member_required
def edit_homework(request, pk):
    hw = get_object_or_404(Homework, pk=pk)
    if request.method == 'POST':
        form = HomeworkForm(request.POST, instance=hw)
        if form.is_valid():
            form.save()
            return redirect('teacher_dashboard')
    else:
        form = HomeworkForm(instance=hw)
    return render(request, 'homework/edit_homework.html', {'form': form})

def view_homework(request, pk):
    hw = get_object_or_404(Homework, pk=pk)
    return render(request, 'homework/view_homework.html', {'homework': hw})




def daily_quote_view(request):
    today = date.today()
    quote_of_the_day = DailyQuote.objects.filter(created__date=today).first()

    # If no quote has been assigned today, pick one randomly and save it with today's date
    if not quote_of_the_day:
        quotes = list(DailyQuote.objects.all())
        if quotes:
            quote_of_the_day = random.choice(quotes)
        else:
            quote_of_the_day = None

    context = {
        'quote': quote_of_the_day
    }
    return render(request, 'daily_quote.html', context)


@require_POST
@login_required
def react_view(request, post_id):
    reaction_type = request.POST.get("reaction_type")
    post = get_object_or_404(Post, pk=post_id)

    if reaction_type not in dict(Reaction.REACTION_CHOICES):
        return JsonResponse({"error": "Invalid reaction type"}, status=400)

    reaction, created = Reaction.objects.get_or_create(
        user=request.user,
        post=post,
        defaults={"reaction_type": reaction_type},
    )
    if not created:
        if reaction.reaction_type == reaction_type:
            
            reaction.delete()
        else:
           
            reaction.reaction_type = reaction_type
            reaction.save()

    
    counts = (
        Reaction.objects.filter(post=post)
        .values("reaction_type")
        .order_by()
        .annotate(count=Count("id"))

    )
    counts_dict = {item["reaction_type"]: item["count"] for item in counts}

    # Fill zeros for reaction types without any reactions
    for key, _ in Reaction.REACTION_CHOICES:
        counts_dict.setdefault(key, 0)

    return JsonResponse({"counts": counts_dict})


def quiz_detail(request, pk):
    quiz = get_object_or_404(DailyQuiz, pk=pk)
    quiz.question = strip_tags(quiz.question)
    feedback = None
    selected_option = None
    today = timezone.localdate()

    user_attempt_count = 0
    if request.user.is_authenticated:
        # Only count attempts for logged-in users
        user_attempt_count = DailyQuizAttempt.objects.filter(
            quiz=quiz,
            user=request.user,
            date_attempted__date=today
        ).count()

    # Subquery to get latest attempt ID per user
    latest_attempt_ids = DailyQuizAttempt.objects.filter(
        quiz=quiz,
        date_attempted__date=today,
        user=OuterRef('user')
    ).order_by('-date_attempted').values('id')[:1]

    # All latest attempts (unique per user)
    latest_attempts_today = DailyQuizAttempt.objects.filter(
        id__in=Subquery(latest_attempt_ids)
    ).select_related('user')

    total_users_today = latest_attempts_today.count()
    wrong_users_today = latest_attempts_today.filter(is_correct=False)
    correct_users_today = latest_attempts_today.filter(is_correct=True)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, "You must be logged in to attempt this quiz.")
            return redirect('login')  # or wherever your login URL is

        if user_attempt_count >= 1:
            messages.warning(request, "You have already attempted this quiz today. Try again tomorrow.")
            return redirect('quiz_detail', pk=quiz.pk)

        selected_option = request.POST.get('answer')
        is_correct = (selected_option == quiz.correct_answer)

        feedback = {
            'type': 'success' if is_correct else 'danger',
            'message': '✅ Correct! Well done.' if is_correct else f'❌ Wrong. The correct answer is {quiz.correct_answer}.',
            'correct_answer': quiz.correct_answer,
        }

        DailyQuizAttempt.objects.create(
            quiz=quiz,
            user=request.user,
            selected_option=selected_option,
            is_correct=is_correct,
            date_attempted=timezone.now()
        )

        # Recalculate after saving
        latest_attempt_ids = DailyQuizAttempt.objects.filter(
            quiz=quiz,
            date_attempted__date=today,
            user=OuterRef('user')
        ).order_by('-date_attempted').values('id')[:1]

        latest_attempts_today = DailyQuizAttempt.objects.filter(
            id__in=Subquery(latest_attempt_ids)
        ).select_related('user')
        total_users_today = latest_attempts_today.count()
        wrong_users_today = latest_attempts_today.filter(is_correct=False)
        correct_users_today = latest_attempts_today.filter(is_correct=True)

    options = [
        ('A', quiz.option_a),
        ('B', quiz.option_b),
        ('C', quiz.option_c),
        ('D', quiz.option_d),
    ]

    return render(request, 'core/quiz_detail.html', {
        'quiz': quiz,
        'feedback': feedback,
        'selected_option': selected_option,
        'options': options,
        'user_attempt_count': user_attempt_count,
        'total_users_today': total_users_today,
        'latest_attempts_today': latest_attempts_today,
        'wrong_users_today': wrong_users_today,
        'correct_users_today': correct_users_today,  
    })



def homework_pdf(request, pk):
    homework = get_object_or_404(Homework, pk=pk)
    
    images_with_urls = []
    for img in homework.images.all():
        images_with_urls.append(request.build_absolute_uri(img.image.url))
    
    template_path = 'homework/homework_pdf.html'
    context = {
        'homework': homework,
        'images': images_with_urls,  
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{homework.title}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    
    return response



DEFAULT_PHOTO_URL = "https://res.cloudinary.com/dwp0xtvyb/image/upload/v123456789/default_profile.png"


# =============================
# 🔔 NOTIFICATIONS HOME
# =============================
@login_required
def notifications(request):
    """Landing page for notifications."""
    return render(request, "notifications/index.html")


# =============================
# 📥 UNREAD NOTIFICATIONS (HTML & JSON)
# =============================
@login_required
def unread_notifications(request, as_json=False):
    """
    Returns unread notifications either as HTML or JSON.
    If as_json=True, returns a JSON response (for AJAX/live updates).
    """
    notifications = Notification.objects.filter(
        user=request.user, is_read=False
    ).select_related("sender__profile", "post")

    if as_json:
        data = []
        for n in notifications:
            message = f"{n.sender.username} {n.verb}"
            if n.post and "your post" not in n.verb:
                message += f" your post '{n.post.title}'"

            photo_url = getattr(getattr(n.sender, 'profile', None), 'photo', None)
            photo_url = photo_url.url if photo_url else DEFAULT_PHOTO_URL

            data.append({
                "id": n.id,
                "message": message,
                "url": reverse("mark_notification_as_read", args=[n.id]),
                "tone": n.tone,
                "photo": photo_url,
            })
        return JsonResponse(data, safe=False)

    # HTML version: mark as read before rendering
    notifications.update(is_read=True)
    return render(request, "notifications/unread.html", {"notifications": notifications})


# Shortcut view for JSON API
@login_required
def unread_notifications_json(request):
    return unread_notifications(request, as_json=True)


# =============================
# 📚 ALL NOTIFICATIONS
# =============================
@login_required
def all_notifications(request):
    notifications = Notification.objects.filter(user=request.user)\
        .select_related("sender__profile", "post")\
        .order_by('-timestamp')
    return render(request, "notifications/all.html", {"notifications": notifications})


# =============================
# ☑️ MARK SINGLE NOTIFICATION AS READ
# =============================
@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)

    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=['is_read'])

    # Redirect to post if applicable
    if notification.post:
        return redirect(notification.post.get_absolute_url())
    
    return redirect('unread_notifications')


# =============================
# 🧹 MARK ALL NOTIFICATIONS AS READ
# =============================
@login_required
def mark_all_notifications_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect("unread_notifications")