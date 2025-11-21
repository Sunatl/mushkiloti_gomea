from django.contrib import admin
from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['title', 'reporter', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['title', 'description', 'address']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'level', 'issues_reported']
    search_fields = ['user__username']

@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'order', 'is_active']
    list_filter = ['is_active', 'category']

admin.site.register(IssueImage)
admin.site.register(Comment)
admin.site.register(Vote)
admin.site.register(Notification)