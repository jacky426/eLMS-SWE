# pypractice/urls.py
from django.urls import path
from . import views  # 這行一定要有！

app_name = 'pypractice'

urlpatterns = [
    path('', views.student_dashboard, name='student_dashboard'),
    path('tutorial/<slug:slug>/', views.tutorial_detail, name='tutorial'),
    path('exercise/<int:pk>/', views.exercise_detail, name='exercise'),
    path('exercise/<int:pk>/submit/', views.submit_code, name='submit'),
    path('quiz/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:pk>/result/', views.quiz_result, name='quiz_result'),
    path('forum/', views.forum_list, name='forum_list'),
    path('forum/<int:pk>/', views.forum_thread, name='forum_thread'),
]