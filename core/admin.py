from django.contrib import admin
from .models import (
    Profile, Category, Comment, Announcement, DailyQuote,
    Document, PostMedia, Post, SiteSettings, PDFDocument,
    SupportInfo, QuizCategory, Question, QuizResult, DailyFact
)

# Register other models
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

# Inline and custom admin
class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [PostMediaInline]
    list_display = ('title', 'is_pinned', 'status')
    list_editable = ('is_pinned',)
