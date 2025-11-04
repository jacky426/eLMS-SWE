from django.db import models

# pypractice/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class LearningPath(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paths')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Tutorial(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()  # Markdown
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='tutorials')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ['path', 'order']

    def get_absolute_url(self):
        return reverse('pypractice:tutorial', args=[self.slug])

    def __str__(self):
        return self.title

class Exercise(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    starter_code = models.TextField(blank=True, default="# Write your code here")
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='exercises')
    time_limit = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.title

class TestCase(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='testcases')
    input_data = models.TextField(blank=True)
    expected_output = models.TextField()
    is_visible = models.BooleanField(default=False)

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    code = models.TextField()
    passed = models.BooleanField(default=False)
    output = models.TextField(blank=True)
    error = models.TextField(blank=True)
    runtime = models.FloatField(null=True)
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['user', 'exercise']

# === QUIZ ===
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='quizzes')
    duration = models.PositiveIntegerField(default=15)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def is_active(self):
        if not self.start_time or not self.end_time:
            return False
        return self.start_time <= timezone.now() <= self.end_time

    def __str__(self):
        return self.title

class Question(models.Model):
    TYPE_CHOICES = [('mcq', 'Multiple Choice'), ('tf', 'True/False'), ('fib', 'Fill in Blank')]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)

    class Meta:
        unique_together = ['quiz', 'user']

class StudentAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, null=True, blank=True, on_delete=models.SET_NULL)
    text_answer = models.TextField(blank=True)

    def is_correct(self):
        if self.question.question_type in ['mcq', 'tf']:
            return self.selected_choice and self.selected_choice.is_correct
        correct = self.question.choices.filter(is_correct=True).first()
        return correct and self.text_answer.strip().lower() == correct.text.strip().lower()

# === FORUM ===
class ForumThread(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ForumReply(models.Model):
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)