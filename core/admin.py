from django.contrib import admin
from .models import HomeworkSubmissionImage 
from django.utils.html import format_html
from django.contrib import admin
from .models import HomeworkSubmission

from .models import (
    Profile, Category, Comment, Announcement, DailyQuote,
    Document, PostMedia, PostImage, Post, SiteSettings, PDFDocument,
    SupportInfo, QuizCategory, Question, QuizResult, DailyFact,
    Homework, HomeworkSubmission, HomeworkImage,
)

# Register models
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Announcement)
admin.site.register(DailyQuote)
admin.site.register(Document)
admin.site.register(QuizCategory)
admin.site.register(Question)
admin.site.register(QuizResult)
admin.site.register(SiteSettings)
admin.site.register(PDFDocument)
admin.site.register(Profile)
admin.site.register(SupportInfo)
admin.site.register(DailyFact)


# Inlines
class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 5

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 5

# Post admin
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [PostMediaInline, PostImageInline]
    list_display = ('title', 'author', 'is_pinned', 'status', 'created', 'views')
    list_editable = ('is_pinned',)
    search_fields = ('title', 'author__username')
    list_filter = ('status', 'created', 'is_pinned')

# Homework admin with inline images
class HomeworkImageInline(admin.TabularInline):
    model = HomeworkImage
    extra = 5

class HomeworkAdmin(admin.ModelAdmin):
    inlines = [HomeworkImageInline]
    list_display = ('title', 'subject', 'grade', 'due_date')

# Register Homework with its custom admin
admin.site.register(Homework, HomeworkAdmin)


class HomeworkSubmissionImageInline(admin.TabularInline):
    model = HomeworkSubmissionImage
    extra = 3
from django.contrib import admin
from .models import HomeworkSubmission
from .models import HomeworkSubmissionImage  # if needed

class HomeworkSubmissionImageInline(admin.TabularInline):
    model = HomeworkSubmissionImage
    extra = 5
from django.utils.html import format_html

@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    inlines = [HomeworkSubmissionImageInline]
    
    list_display = ('student', 'homework', 'grade', 'mark_percentage', 'is_graded', 'submitted_at')
    list_filter = ('is_graded', 'homework')
    search_fields = ('student__username',)

    fields = (
        'student',
        'homework',
        'rendered_answer_text',
        'submitted_file',
        'grade',
        'mark_percentage',  # 👈 Added this line
        'feedback',
        'is_graded',
    )

    readonly_fields = (
        'student',
        'homework',
        'rendered_answer_text',
        'submitted_file',
    )

    def rendered_answer_text(self, obj):
        return format_html(obj.answer_text)

    rendered_answer_text.short_description = "Your Answer"