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




def homepage_view(request):
    settings = SiteSettings.objects.first()
    categories = QuizCategory.objects.all()[:4] 
    posts = Post.objects.order_by('-created')[:3] 
    quiz_categories = QuizCategory.objects.all()
    today = date.today()
    daily_fact = DailyFact.objects.filter(date=today).first()

    return render(request, 'core/home.html', {
        'settings': settings,
        'categories': categories,
        'posts': posts,
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

    category = QuizCategory.objects.get(id=quiz['category_id'])

    QuizResult.objects.create(
        user=request.user,
        category=category,
        score=quiz['score']
    )

    return render(request, 'quiz/result.html', {
        'score': quiz['score'],
        'total': len(quiz['question_ids']),
        'answers': quiz['answers'],
        'category': category
    })



from django.db.models import Sum
from django.contrib.auth.models import User

def quiz_leaderboard(request):
    leaderboard = (
        QuizResult.objects
        .values('user__username')
        .annotate(total_score=Sum('score'))
        .order_by('-total_score')[:10]  
    )
    return render(request, 'quiz/leaderboard.html', {'leaderboard': leaderboard})


@login_required
def quiz_history(request):
    attempts = QuizResult.objects.filter(user=request.user).order_by('-taken_at')
    return render(request, 'quiz/history.html', {'attempts': attempts})



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
