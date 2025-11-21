from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'issues', views.IssueViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'votes', views.VoteViewSet)
router.register(r'rules', views.RuleViewSet)
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'issue-images', views.IssueImageViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]