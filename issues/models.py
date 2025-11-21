from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Номи категория")
    description = models.TextField(blank=True, verbose_name="Тавсифи")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Иконка")
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категорияҳо"
    
    def __str__(self):
        return self.name

class Issue(models.Model):
    STATUS_CHOICES = [
        ('reported', 'Мушкилот дар интиқор'),
        ('in_progress', 'Дар ҳоли иҷро'),
        ('resolved', 'Ҳал шуд'),
        ('closed', 'Пӯшида шуд'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Паст'),
        ('medium', 'Миёна'),
        ('high', 'Баланд'),
        ('critical', 'Ҳаётан муҳим'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Сарлавҳа")
    description = models.TextField(verbose_name="Тавсифи мушкилот")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_issues', verbose_name="Мушкилкунанда")
    
    # Ҷойгиркунӣ
    address = models.CharField(max_length=300, verbose_name="Суроға")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Арз")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Тӯл")
    
    # Статус ва аҳамият
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported', verbose_name="Ҳолат")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name="Аҳамият")
    
    # Овоздиҳӣ ва дигар
    votes = models.IntegerField(default=0, verbose_name="Миқдори овозҳо")
    views = models.IntegerField(default=0, verbose_name="Миқдори дидан")
    
    # Вақт
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Санаи эҷод")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Санаи навсозӣ")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Санаи ҳал")
    
    class Meta:
        verbose_name = "Мушкилот"
        verbose_name_plural = "Мушкилотҳо"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def update_votes_count(self):
        self.votes = self.vote_set.count()
        self.save()

class IssueImage(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='issues/%Y/%m/%d/', verbose_name="Акс")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Шарҳ")
    is_before = models.BooleanField(default=True, verbose_name="Акси пеш аз ҳал?")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Акси мушкилот"
        verbose_name_plural = "Аксҳои мушкилот"

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Корбар")
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, verbose_name="Мушкилот")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Санаи овоздиҳӣ")
    
    class Meta:
        verbose_name = "Овоз"
        verbose_name_plural = "Овозҳо"
        unique_together = ['user', 'issue']  # Ҳар корбар фақат як бор овоз диҳад
    
    def __str__(self):
        return f"{self.user.username} - {self.issue.title}"

class Comment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments', verbose_name="Мушкилот")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Корбар")
    text = models.TextField(verbose_name="Матни шарҳ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Санаи фиристодан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Санаи навсозӣ")
    is_solution = models.BooleanField(default=False, verbose_name="Ҳалли пешниҳодӣ?")
    
    class Meta:
        verbose_name = "Шарҳ"
        verbose_name_plural = "Шарҳҳо"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.issue.title}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    points = models.IntegerField(default=0, verbose_name="Холҳо")
    level = models.IntegerField(default=1, verbose_name="Сатҳ")
    bio = models.TextField(blank=True, verbose_name="Дар бораи ман")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Аватар")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Рақами телефон")
    
    # Омори фаъолият
    issues_reported = models.IntegerField(default=0, verbose_name="Миқдори мушкилотҳои эҷодшуда")
    issues_resolved = models.IntegerField(default=0, verbose_name="Миқдори мушкилотҳои ҳалшуда")
    comments_written = models.IntegerField(default=0, verbose_name="Миқдори шарҳҳо")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Профили корбар"
        verbose_name_plural = "Профилҳои корбарон"
    
    def __str__(self):
        return self.user.username
    
    def update_points(self):
        """Холҳои корбарро навсозӣ мекунад"""
        points = (
            self.issues_reported * 10 +
            self.issues_resolved * 50 +
            self.comments_written * 5
        )
        self.points = points
        self.level = min(100, max(1, points // 100 + 1))  # Ҳисоб кардани сатҳ
        self.save()

class Rule(models.Model):
    title = models.CharField(max_length=200, verbose_name="Сарлавҳа")
    description = models.TextField(verbose_name="Тавсиф")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Категория")
    order = models.IntegerField(default=0, verbose_name="Тартиб")
    is_active = models.BooleanField(default=True, verbose_name="Фаъол аст?")
    
    class Meta:
        verbose_name = "Қоида"
        verbose_name_plural = "Қоидаҳо"
        ordering = ['order', 'id']
    
    def __str__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Корбар")
    title = models.CharField(max_length=200, verbose_name="Сарлавҳа")
    message = models.TextField(verbose_name="Паём")
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Мушкилот")
    is_read = models.BooleanField(default=False, verbose_name="Хонда шуд?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Сана эҷод")
    
    class Meta:
        verbose_name = "Огоҳинома"
        verbose_name_plural = "Огоҳиномаҳо"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"