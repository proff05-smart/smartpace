
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.urls import reverse
from cloudinary.models import CloudinaryField
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.models import Group
from django.db import models 
from django.contrib.auth.models import Group
#from ckeditor_uploader.fields import CKEditor5Field
from cloudinary.models import CloudinaryField
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField






class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    photo = CloudinaryField('image', blank=True, null=True)
    followers = models.ManyToManyField('self', symmetrical=False, blank=True)
    last_activity = models.DateTimeField(default=timezone.now)
    role = models.CharField(
        max_length=20,
        choices=[('Student', 'Student'), ('Teacher', 'Teacher'), ('Admin', 'Admin')],
        default='Student'
    )

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name='posts')
    title = models.CharField(max_length=200)
    content = CKEditor5Field('Content', config_name='default')
    youtube_url = models.URLField(blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_pinned = models.BooleanField(default= False)
    image = CloudinaryField('image', blank=True, null=True,resource_type="image")
    video = CloudinaryField('video', blank=True, null=True,resource_type="video")
    views = models.PositiveIntegerField(default=0)



    class Meta:
        ordering = ['-created', '-is_pinned']

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})



class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='extra_images', on_delete=models.CASCADE)
    image = CloudinaryField('image', resource_type="image")
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.post.title}"





class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(verbose_name="Comment")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    updated = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    class Meta:
        ordering = ['created']  # Chronological order; change to ['-created'] for newest first

    def __str__(self):
        return f"{self.user.username} on '{self.post.title}'"

    def total_likes(self):
        return self.likes.count()

    def is_reply(self):
        return self.parent is not None


class Announcement(models.Model):
    message = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

class DailyQuote(models.Model):
    quote = CKEditor5Field('Text', config_name='default')  
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created'] 

    def __str__(self):
        return self.quote[:50] + ("..." if len(self.quote) > 50 else "")

class Document(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='documents/')


class QuizCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Question(models.Model):
    category = models.ForeignKey(QuizCategory, on_delete=models.CASCADE)
    text = CKEditor5Field('Question Text', config_name='default')
    image = CloudinaryField('image', blank=True, null=True,resource_type="image")
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1, choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ])
    explanation = CKEditor5Field('Explanation', config_name='default')



class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE, null=True, blank=True) 
    category = models.ForeignKey(QuizCategory, on_delete=models.CASCADE)
    score = models.IntegerField()
    total = models.IntegerField()
    percentage = models.FloatField()
    total_questions = models.IntegerField()  
    correct_answers = models.IntegerField(default=0)  
    taken_at = models.DateTimeField(auto_now_add=True)
    time_used_seconds = models.IntegerField(default=0)
    date_taken = models.DateTimeField(auto_now_add=True) 
    def __str__(self):
        return f"{self.user.username} - {self.category.name} - {self.score}/{self.total}"





class PostMedia(models.Model):
    post = models.ForeignKey(Post, related_name='media', on_delete=models.CASCADE)
    image = CloudinaryField('image', blank=True, null=True, resource_type='image')
    video = CloudinaryField('video', blank=True, null=True, resource_type='video')

    def __str__(self):
        return f"Media for {self.post.title}"
    
    def get_first_image_url(self):
        first_media = self.media.filter(image__isnull=False).first()
        if first_media and first_media.image:
            return first_media.image.url
        elif self.image:
            return self.image.url
        return "https://res.cloudinary.com/YOUR_CLOUD_NAME/image/upload/v1234567890/default.jpg"

        
class SiteSettings(models.Model):
    banner_text = models.CharField(max_length=255, default="Welcome to SMARTPACE - Your Science Hub!")
    announcement = models.TextField(blank=True, null=True)
    daily_quote = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "Site Settings"

    class Meta:
        verbose_name_plural = "Site Settings"


class PDFDocument(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='pdfs/')
    category = models.CharField(max_length=100, choices=[
        ('Math', 'Math'),
        ('Physics', 'Physics'),
        ('Chemistry', 'Chemistry'),
        ('Biology', 'Biology'),
        ('Other', 'Other'),
    ])
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title




class SupportInfo(models.Model):
    mpesa_number = models.CharField(max_length=20, help_text="e.g. 0712345678")
    paybill_number = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30)
    message = models.TextField(blank=True, help_text="Optional thank-you or donation message")

    def __str__(self):
        return "Support Info"




class DailyFact(models.Model):
    text = models.TextField()
    date = models.DateField(unique=True)

    def __str__(self):
        return f"Fact for {self.date}"


from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from cloudinary.models import CloudinaryField

class Notification(models.Model):
    
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications'
    )  
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_notifications'
    )  

   
    verb = models.CharField(max_length=255)  

   
    post = models.ForeignKey('Post', null=True, blank=True, on_delete=models.CASCADE)
    comment = models.ForeignKey('Comment', null=True, blank=True, on_delete=models.CASCADE)
    

   
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=now)
    
    tone = models.CharField(
        max_length=20,
        choices=[
            ('info', 'Info'),
            ('success', 'Success'),
            ('warning', 'Warning'),
            ('danger', 'Danger'),
        ],
        default='info',
    )
    sound = CloudinaryField('sound', blank=True, null=True)

    def __str__(self):
        return f"{self.sender} {self.verb} your post"

    class Meta:
        ordering = ['-timestamp']



class UserQuizHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(QuizCategory, on_delete=models.CASCADE)
    score = models.FloatField()
    time_taken = models.DurationField()
    taken_on = models.DateTimeField(auto_now_add=True)


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(QuizCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title




class Reply(models.Model):
    content = models.TextField()
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='liked_replies', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.author} on {self.post}"


from cloudinary.models import CloudinaryField

photo = CloudinaryField('image', blank=True, null=True)
avatar = CloudinaryField('image', default='https://res.cloudinary.com/your_cloud/image/upload/v123456789/default.png', blank=True)




# Grade options — customize as needed
GRADE_CHOICES = [
    ('Grade 1', 'Grade 1'),
    ('Grade 2', 'Grade 2'),
    ('Grade 3', 'Grade 3'),
    ('Grade 4', 'Grade 4'),
    ('Grade 5', 'Grade 5'),
    ('Grade 6', 'Grade 6'),
    ('Grade 7', 'Grade 7'),
    ('Grade 8', 'Grade 8'),
    ('Grade 9', 'Grade 9'),
    ('Grade 10', 'Grade 10'),
    ('Grade 11', 'Grade 11'),
    ('Grade 12', 'Grade 12'),
]

class Homework(models.Model):
    title = models.CharField(max_length=255)
    instructions = CKEditor5Field('Homework instructions')
    subject = models.CharField(max_length=100)
    image = CloudinaryField('image', blank=True, null=True)
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, default="Grade 8")  
    due_date = models.DateTimeField()  # changed from DateField to DateTimeField
    attachment = CloudinaryField('file', blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ManyToManyField(
        Group,
        help_text="Select class(es) this homework is assigned to"
    )

    def __str__(self):
        return self.title

    def is_due(self):
        
        return timezone.now() > self.due_date


class HomeworkImage(models.Model):
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = CloudinaryField('image')  

    def __str__(self):
        return f"Image for {self.homework.title}"

        
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField

User = get_user_model()

GRADE_CHOICES = [
    ('Grade 1', 'Grade 1'),
    ('Grade 2', 'Grade 2'),
    ('Grade 3', 'Grade 3'),
    ('Grade 4', 'Grade 4'),
    ('Grade 5', 'Grade 5'),
    ('Grade 6', 'Grade 6'),
    ('Grade 7', 'Grade 7'),
    ('Grade 8', 'Grade 8'),
    ('Grade 9', 'Grade 9'),
    ('Grade 10', 'Grade 10'),
    ('Grade 11', 'Grade 11'),
    ('Grade 12', 'Grade 12'),
]

class HomeworkSubmission(models.Model):
    homework = models.ForeignKey('Homework', on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, default="Grade 8", blank=True, null=True)
    submitted_file = CloudinaryField('file', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    answer_text = CKEditor5Field('Your Answer', blank=True, null=True)
    feedback = CKEditor5Field('Feedback', blank=True, null=True)
    is_graded = models.BooleanField(default=False)
    mark_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        help_text="Enter the mark as a percentage (e.g., 87.50)"
    )

    def __str__(self):
        student_name = self.student.username if self.student else "Unknown Student"
        homework_title = self.homework.title if self.homework else "Unknown Homework"
        return f"{student_name}'s submission for {homework_title}"


class HomeworkSubmissionImage(models.Model):
    submission = models.ForeignKey(HomeworkSubmission, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image')

    def __str__(self):
        return f"Image for {self.submission}"


class Reaction(models.Model):
    REACTION_CHOICES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('laugh', '😂'),
        ('wow', '😮'),
        ('sad', '😢'),
        ('angry', '😡'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user} - {self.reaction_type} on {self.post}"

from django.utils import timezone
from django.db import models

class DailyQuiz(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    question = models.TextField()
    image = CloudinaryField('image', blank=True, null=True,resource_type="image")
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)

    explanation = models.TextField(blank=True, null=True) 
    correct_answer = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        default='A'
    )

    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title if self.title else f"Quiz {self.id} - {self.question[:30]}..."

    @classmethod
    def get_today_quiz(cls):
        today = timezone.localdate()
        return cls.objects.filter(date_created__date=today).first()




class DailyQuizAttempt(models.Model):
    quiz = models.ForeignKey(DailyQuiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    date_attempted = models.DateTimeField(auto_now_add=True)
    photo = CloudinaryField('image', blank=True, null=True)

    class Meta:
        ordering = ['-date_attempted']

    def __str__(self):
        return f"{self.user.username} - {self.quiz} - {self.date_attempted.date()}"

