
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.urls import reverse
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
    content = models.TextField()
    youtube_url = models.URLField(blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    created = models.DateTimeField(auto_now_add=True)
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
    quote = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)


class Document(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='documents/')


class QuizCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Question(models.Model):
    category = models.ForeignKey(QuizCategory, on_delete=models.CASCADE)
    text = models.TextField()
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
    explanation = models.TextField()


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



### to edit 
from django.utils.timezone import now

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')  # Receiver
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')  # Actor
    verb = models.CharField(max_length=255)  # e.g., "liked", "commented on"
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=now)
    tone = models.CharField(max_length=20, choices=[('info', 'Info'), ('success', 'Success'), ('warning', 'Warning'), ('danger', 'Danger')], default='info')
    sound = CloudinaryField('sound', blank=True, null=True)  # ✅ Add this

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
