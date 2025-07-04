from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, ProfileForm
from .models import Profile
from .models import Post, PostMedia, Category
from .forms import PostForm, PostMediaFormSet
from django.contrib.auth.decorators import login_required
from .models import SupportInfo
from .models import Post, Comment
from .forms import CommentForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import SiteSettings
from .models import PDFDocument
from .forms import PDFUploadForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import QuizCategory, Question, QuizResult
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import random
from django.utils import timezone
from datetime import date
from .models import DailyFact
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Post
from .forms import PostForm
from xhtml2pdf import pisa









# Register user
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)  # Create empty profile
            messages.success(request, 'Account created successfully.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})

# Login user
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'core/login.html')

# Logout user
def logout_view(request):
    logout(request)
    return redirect('login')

# Profile page
@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'core/profile.html', {'form': form})




@login_required
def post_create_view(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        media_formset = PostMediaFormSet(request.POST, request.FILES, queryset=PostMedia.objects.none())
        
        if post_form.is_valid() and media_formset.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()
            
            for form in media_formset.cleaned_data:
                if form:
                    PostMedia.objects.create(
                        post=post,
                        image=form.get('image'),
                        video=form.get('video')
                    )
            messages.success(request, 'Post created!')
            return redirect('home')
    else:
        post_form = PostForm()
        media_formset = PostMediaFormSet(queryset=PostMedia.objects.none())
    
    return render(request, 'core/post_create.html', {
        'post_form': post_form,
        'media_formset': media_formset
    })

def post_list_view(request):
    query = request.GET.get('q')
    posts = Post.objects.all().order_by('-created')

    if query:
        posts = posts.filter(title__icontains=query)  

    return render(request, 'core/post_list.html', {'posts': posts})


def post_detail_view(request, pk):
    post = Post.objects.get(id=pk)
    return render(request, 'core/post_detail.html', {'post': post})




def post_detail_view(request, pk):
    post = Post.objects.get(id=pk)
    comments = post.comments.all().order_by('-created')
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = post
            new_comment.save()
            return HttpResponseRedirect(reverse('post_detail', args=[pk]))
    else:
        comment_form = CommentForm()

    return render(request, 'core/post_detail.html', {
        'post': post,
        'comment_form': comment_form,
        'comments': comments
    })

@login_required
def like_post_view(request, pk):
    post = Post.objects.get(id=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('post_detail', pk=pk)




from django.core.paginator import Paginator
from datetime import date

def homepage_view(request):
    settings = SiteSettings.objects.first()
    categories = QuizCategory.objects.all()[:4]
    
    # Get all posts ordered by created date (descending)
    all_posts = Post.objects.order_by('-created')
    
    # Setup paginator: 3 posts per page (change number as you like)
    paginator = Paginator(all_posts, 6)
    
    # Get current page number from URL GET param ?page=
    page_number = request.GET.get('page')
    
    # Get posts for the current page
    posts = paginator.get_page(page_number)
    
    quiz_categories = QuizCategory.objects.all()
    today = date.today()
    daily_fact = DailyFact.objects.filter(date=today).first()

    return render(request, 'core/home.html', {
        'settings': settings,
        'categories': categories,
        'posts': posts,          # posts is now a Page object, not a QuerySet
        'quiz_categories': quiz_categories,
        'daily_fact': daily_fact
    })





def pdf_list_view(request):
    pdfs = PDFDocument.objects.order_by('-uploaded_at')
    return render(request, 'core/pdf_list.html', {'pdfs': pdfs})

@login_required
def pdf_upload_view(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf = form.save(commit=False)
            pdf.uploaded_by = request.user
            pdf.save()
            return redirect('pdf_list')
    else:
        form = PDFUploadForm()
    return render(request, 'core/pdf_upload.html', {'form': form})






@login_required
def profile_dashboard(request):
    profile = request.user.userprofile
    return render(request, 'core/profile_dashboard.html', {'profile': profile})

@login_required
def edit_profile(request):
    user = request.user
    profile = user.userprofile
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile_dashboard')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    return render(request, 'core/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('home')
    return render(request, 'core/delete_account.html')





def support_view(request):
    support = SupportInfo.objects.first() 
    return render(request, 'core/support.html', {'support': support})





@login_required
def quiz_category_list(request):
    categories = QuizCategory.objects.all()
    return render(request, 'quiz/category_list.html', {'categories': categories})

@login_required
def start_quiz(request, category_id):
    category = QuizCategory.objects.get(id=category_id)
    questions = list(Question.objects.filter(category=category))
    selected_questions = random.sample(questions, min(len(questions), 10)) 

    request.session['quiz'] = {
        'category_id': category.id,
        'question_ids': [q.id for q in selected_questions],
        'current': 0,
        'score': 0,
        'answers': [],
        'start_time': timezone.now().isoformat()
    }

    return redirect('quiz_question')

@login_required
def quiz_question(request):
    quiz = request.session.get('quiz')
    if not quiz or quiz['current'] >= len(quiz['question_ids']):
        return redirect('quiz_result')

    question_id = quiz['question_ids'][quiz['current']]
    question = Question.objects.get(id=question_id)

    if request.method == 'POST':
        selected = request.POST.get('choice')
        correct = question.correct_answer

        is_correct = selected == correct
        quiz['score'] += 1 if is_correct else 0
        quiz['answers'].append({
            'id': question.id,
            'selected': selected,
            'correct': correct,
            'explanation': question.explanation
        })
        quiz['current'] += 1
        request.session['quiz'] = quiz

        return redirect('quiz_question')

    return render(request, 'quiz/question.html', {'question': question, 'current': quiz['current'] + 1, 'total': len(quiz['question_ids'])})
@login_required
def quiz_result(request):
    quiz = request.session.pop('quiz', None)
    if not quiz:
        return redirect('quiz_category_list')

    category = get_object_or_404(QuizCategory, id=quiz['category_id'])
    total_questions = len(quiz['question_ids'])
    score = quiz['score']
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0

    # Badge logic
    if percentage >= 90:
        remarks, badge, badge_class, emoji = (
            "🏅 Excellent work! You're a quiz champion! 🎉 Keep shining!",
            "Gold Medal", "badge bg-warning text-dark", "🥇"
        )
    elif percentage >= 70:
        remarks, badge, badge_class, emoji = (
            "👍 Great job! You're on the right path! ✨",
            "Silver Medal", "badge bg-secondary", "🥈"
        )
    elif percentage >= 50:
        remarks, badge, badge_class, emoji = (
            "🙂 Good effort! Keep learning and growing! 📚",
            "Bronze Medal", "badge bg-info text-dark", "🥉"
        )
    else:
        remarks, badge, badge_class, emoji = (
            "😕 Don't worry, practice makes perfect! 💪 You got this!",
            "No Badge", "badge bg-danger", "❌"
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
    question_ids = [ans['id'] for ans in quiz['answers']]
    questions = Question.objects.in_bulk(question_ids)

    question_texts = []
    for ans in quiz['answers']:
        question = questions.get(ans['id'])
        if question:
            question_texts.append({
                'text': question.text,
                'selected': ans['selected'],
                'correct': ans['correct'],
                'explanation': ans['explanation']
            })

    quiz_title = f"Quiz Results for {category.name}"

    return render(request, 'quiz/result.html', {
        'score': score,
        'total': total_questions,
        'percentage': percentage,
        'remarks': remarks,
        'badge': badge,
        'badge_class': badge_class,
        'emoji': emoji,
        'answers': question_texts,
        'category': category,
        'total_questions': total_questions,
        'quiz_title': quiz_title,
    })




from django.shortcuts import render
from django.db.models import Sum, Count
from django.contrib.auth.models import User

def quiz_leaderboard(request):
    # Aggregate total score and total attempts per user
    leaderboard = (
        User.objects
        .filter(quizresult__isnull=False)  # users who attempted quiz
        .annotate(
            total_score=Sum('quizresult__score'),
            attempts=Count('quizresult')
        )
        .order_by('-total_score', 'username')  # best score first, then alphabetically
    )

    # Define badges and emojis for top 5 ranks
    badges = [
        ("🥇", "Gold"),
        ("🥈", "Silver"),
        ("🥉", "Bronze"),
        ("🏅", "Top 4"),
        ("🎖️", "Top 5"),
    ]

    # Annotate badge and emoji based on rank
    leaderboard_with_badges = []
    for idx, user in enumerate(leaderboard, start=1):
        badge = ''
        emoji = ''
        if idx <= 5:
            emoji, badge = badges[idx - 1]
        leaderboard_with_badges.append({
            'rank': idx,
            'username': user.username,
            'avatar_url': user.profile.avatar.url if hasattr(user, 'profile') and user.profile.avatar else '/static/img/avatar-placeholder.png',
            'total_score': user.total_score,
            'attempts': user.attempts,
            'badge': badge,
            'emoji': emoji,
        })

    context = {
        'leaderboard': leaderboard_with_badges,
    }
    return render(request, 'quiz/leaderboard.html', context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator

from django.core.paginator import Paginator

def quiz_history(request):
    raw_history = QuizResult.objects.filter(user=request.user).order_by('-date_taken')
    paginator = Paginator(raw_history, 10)  # 10 attempts per page
    page_number = request.GET.get('page')
    history_page = paginator.get_page(page_number)

    formatted_history = []
    for attempt in history_page:
        percentage = (attempt.score / attempt.total_questions) * 100 if attempt.total_questions else 0
        total_seconds = attempt.time_used_seconds or 0
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        formatted_history.append({
            'date_taken': attempt.date_taken,
            'category__name': attempt.category.name,
            'score': attempt.score,
            'total_questions': attempt.total_questions,
            'percentage': percentage,
            'minutes': minutes,
            'seconds': seconds,
        })

    # Pass the paginated page object but with formatted data
    history_page.object_list = formatted_history

    return render(request, 'quiz/history.html', {'history': history_page})








from django.shortcuts import render

def search_view(request):
    query = request.GET.get('q')
    results = []
    if query:
     
        from .models import Post
        results = Post.objects.filter(title__icontains=query)
    return render(request, 'core/search_results.html', {'query': query, 'results': results})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PostForm

@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  
            post.save()
            return redirect('post_detail', pk=post.pk) 
    else:
        form = PostForm()
    return render(request, 'blog/add_post.html', {'form': form})




@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to edit this post.")

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('home')  
    else:
        form = PostForm(instance=post)

    return render(request, 'edit_post.html', {'form': form})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    if request.method == 'POST':
        post.delete()
        return redirect('home')

    return render(request, 'confirm_delete.html', {'post': post})


from django.core.paginator import Paginator
def post_list(request):
    posts = Post.objects.filter(status='published').order_by('-created_at')
    paginator = Paginator(posts, 6)  # Show 6 posts per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/post_list.html', {'page_obj': page_obj})


# views.py
from django.contrib.auth.models import User
from .utils import is_user_online

def online_users_view(request):
    users = User.objects.all()
    online_users = [user for user in users if is_user_online(user)]
    return render(request, 'online_users.html', {'online_users': online_users})


from django.contrib.auth.models import User
from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone

def is_user_online(user):
    profile = getattr(user, 'userprofile', None)
    if profile:
        return timezone.now() - profile.last_activity < timedelta(minutes=5)
    return False


from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from .forms import CommentForm
from django.contrib.auth.decorators import login_required

@login_required
def add_comment(request, post_id, parent_id=None):
    post = get_object_or_404(Post, id=post_id)
    parent_comment = Comment.objects.filter(id=parent_id).first() if parent_id else None

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.parent = parent_comment
            reply.save()
            #return redirect('post_detail', post_id=post.id)
            return redirect('post_detail_view', pk=post.id)

    else:
        form = CommentForm()

    return render(request, 'blog/comment_form.html', {'form': form})

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    return redirect('post_detail_view', pk=comment.post.id)




#edit

def post_detail_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    top_level_comments = post.comments.filter(parent__isnull=True)
    
    context = {
        'post': post,
        'top_level_comments': top_level_comments,
        'top_level_comment_count': top_level_comments.count(),
    }
    return render(request, 'core/post_detail.html', context)


#edit

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def download_post_pdf(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    template_path = 'core/post_pdf.html'
    context = {'post': post}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="post_{post_id}.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


#new
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Comment
from .forms import CommentForm
from django.contrib.auth.decorators import login_required

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated successfully.')
            return redirect('post_detail', pk=comment.post.id)  # ✅ FIXED
    else:
        form = CommentForm(instance=comment)

    return render(request, 'core/edit_comment.html', {'form': form, 'comment': comment})



@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    post_id = comment.post.id
    comment.delete()
    messages.success(request, 'Comment deleted.')
    return redirect('post_detail', pk=post_id)  # ✅ FIXED


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User



def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=profile_user, status='published').order_by('-created_at')
    quiz_attempts = QuizResult.objects.filter(user=profile_user).order_by('-date')  # adjust as per your model

    return render(request, 'user_profile.html', {
        'profile_user': profile_user,
        'user_posts': user_posts,
        'quiz_attempts': quiz_attempts,
    })


from .models import Notification
from django.contrib.auth.decorators import login_required

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/notifications.html', {'notifications': notifications})



from django.contrib.auth.decorators import login_required

#
