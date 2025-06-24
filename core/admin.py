from django.contrib import admin
from .models import (
    Profile, Category, Comment, Announcement, DailyQuote,
    Document, PostMedia, Post, SiteSettings, PDFDocument,
    Profile, SupportInfo, QuizCategory, Question, QuizResult,DailyFact
)

# Register basic models

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

# Custom admin for Post with media inlines
class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1

class PostAdmin(admin.ModelAdmin):
    inlines = [PostMediaInline]

admin.site.register(Post, PostAdmin)





admin.site.register(DailyFact)
