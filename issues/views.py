from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django.db.models import Count, Q
from .models import *
from .serializers import *

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return IssueCreateSerializer
        return IssueSerializer

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
        
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        profile.issues_reported += 1
        profile.update_points()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def vote(self, request, pk=None):
        issue = self.get_object()
        user = request.user
        
        vote, created = Vote.objects.get_or_create(user=user, issue=issue)
        
        if not created:
            vote.delete()
            message = "Овоз бекор карда шуд"
        else:
            message = "Овоз қабул шуд"
        
        issue.update_votes_count()
        return Response({'message': message, 'votes': issue.votes})

    @action(detail=False, methods=['get'])
    def popular(self, request):
        popular_issues = Issue.objects.annotate(
            vote_count=Count('vote')
        ).order_by('-vote_count', '-created_at')[:10]
        serializer = self.get_serializer(popular_issues, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        recent_issues = Issue.objects.all().order_by('-created_at')[:20]
        serializer = self.get_serializer(recent_issues, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        profile.comments_written += 1
        profile.update_points()

class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.filter(is_active=True)
    serializer_class = RuleSerializer
    permission_classes = [AllowAny]

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        leaders = UserProfile.objects.all().order_by('-points')[:50]
        serializer = self.get_serializer(leaders, many=True)
        return Response(serializer.data)

# ИСЛОҲ КАРДАН: Илова кардани queryset ба NotificationViewSet
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()  # ИН САТРРО ИЛОВА КУНЕД
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'Ҳама огоҳиномаҳо хонда шуданд'})

class IssueImageViewSet(viewsets.ModelViewSet):
    queryset = IssueImage.objects.all()
    serializer_class = IssueImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]