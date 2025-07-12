from django.contrib import admin
from .models import (
    Profile, Category, Comment, Announcement, DailyQuote,
    Document, PostMedia, PostImage, Post, SiteSettings, PDFDocument,
    SupportInfo, QuizCategory, Question, QuizResult, DailyFact
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
    extra = 1

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1

# Custom Post admin
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [PostMediaInline, PostImageInline]  # Include both if both are used
    list_display = ('title', 'author', 'is_pinned', 'status', 'created', 'views')
    list_editable = ('is_pinned',)
    search_fields = ('title', 'author__username')
    list_filter = ('status', 'created', 'is_pinned')
