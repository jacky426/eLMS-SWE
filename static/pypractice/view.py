# pypractice/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import markdown
from .models import *
from .executor import run_code

# === 學生儀表板 ===
@login_required
def student_dashboard(request):
    paths = LearningPath.objects.all()
    progress = {}
    for path in paths:
        total = path.exercises.count()
        solved = Submission.objects.filter(
            user=request.user, exercise__path=path, passed=True
        ).count()
        progress[path.id] = (solved, total)
    return render(request, 'pypractice/student/dashboard.html', {
        'paths': paths,
        'progress': progress
    })

# === 教程 ===
@login_required
def tutorial_detail(request, slug):
    tutorial = get_object_or_404(Tutorial, slug=slug)
    html_content = markdown.markdown(tutorial.content)
    return render(request, 'pypractice/student/tutorial.html', {
        'tutorial': tutorial,
        'html_content': html_content
    })

# === 練習題 ===
@login_required
def exercise_detail(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    visible_tests = exercise.testcases.filter(is_visible=True)
    submission = Submission.objects.filter(exercise=exercise, user=request.user).first()
    return render(request, 'pypractice/student/exercise.html', {
        'exercise': exercise,
        'visible_tests': visible_tests,
        'submission': submission
    })

@login_required
@csrf_exempt
def submit_code(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    exercise = get_object_or_404(Exercise, pk=pk)
    code = request.POST.get('code', '')

    results = []
    all_passed = True
    total_runtime = 0

    for test in exercise.testcases.all():
        res = run_code(code, test.input_data, exercise.time_limit)
        got = res['output'].strip()
        expected = test.expected_output.strip()
        passed = got == expected and 'error' not in res

        if not passed:
            all_passed = False
        total_runtime += res.get('runtime', 0)

        if test.is_visible:
            results.append({
                'input': test.input_data,
                'expected': expected,
                'got': got,
                'passed': passed,
                'error': res.get('error', '')
            })

    Submission.objects.update_or_create(
        exercise=exercise, user=request.user,
        defaults={
            'code': code,
            'passed': all_passed,
            'output': "\n---\n".join([f"GOT: {r['got']}" for r in results]),
            'runtime': round(total_runtime, 3)
        }
    )

    return JsonResponse({
        'passed': all_passed,
        'results': results,
        'runtime': round(total_runtime, 3)
    })

# === 測驗列表 ===
@login_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(path__in=LearningPath.objects.all())
    return render(request, 'pypractice/quiz/list.html', {'quizzes': quizzes})

# === 測驗作答 ===
@login_required
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    attempt, created = QuizAttempt.objects.get_or_create(quiz=quiz, user=request.user)

    if request.method == 'POST' and quiz.is_active():
        score = 0
        total = 0
        for key, value in request.POST.items():
            if key.startswith('question_'):
                qid = key.split('_')[1]
                question = Question.objects.get(id=qid)
                total += question.points

                answer, _ = StudentAnswer.objects.get_or_create(
                    attempt=attempt, question=question
                )
                if question.question_type in ['mcq', 'tf']:
                    answer.selected_choice = Choice.objects.get(id=value)
                else:
                    answer.text_answer = value
                answer.save()

                if answer.is_correct():
                    score += question.points

        attempt.score = score
        attempt.total_points = total
        attempt.finished_at = timezone.now()
        attempt.save()
        return redirect('pypractice:quiz_result', pk=quiz.pk)

    return render(request, 'pypractice/quiz/detail.html', {
        'quiz': quiz,
        'attempt': attempt
    })

# === 測驗結果 ===
@login_required
def quiz_result(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    attempt = get_object_or_404(QuizAttempt, quiz=quiz, user=request.user, finished_at__isnull=False)
    return render(request, 'pypractice/quiz/result.html', {
        'quiz': quiz, 'attempt': attempt
    })

# === 論壇 ===
@login_required
def forum_list(request):
    threads = ForumThread.objects.all().order_by('-created_at')
    return render(request, 'pypractice/forum/list.html', {'threads': threads})

@login_required
def forum_thread(request, pk):
    thread = get_object_or_404(ForumThread, pk=pk)
    if request.method == 'POST':
        ForumReply.objects.create(
            thread=thread,
            author=request.user,
            content=request.POST['content']
        )
        return redirect('pypractice:forum_thread', pk=pk)
    return render(request, 'pypractice/forum/thread.html', {'thread': thread})