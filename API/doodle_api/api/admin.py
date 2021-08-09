from django.contrib import admin
from api.models import User, Quiz, QuizQuestion, UserQuiz


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):

    list_display = ['id', 'name']
    search_fields = ['id', 'name']
    list_filter = ['name']


@admin.register(QuizQuestion)
class QuizQuestion(admin.ModelAdmin):
    list_display = ['id', 'quiz', 'question', 'dummy_answer1']
    search_fields = ['id', 'question', 'quiz', 'answer']
    list_filter = ['quiz']


@admin.register(UserQuiz)
class UserQuizAdmin(admin.ModelAdmin):
    list_display = ['id', 'quiz', 'marks']
    search_fields = ['user', 'quiz', 'question']
    list_filter = ['quiz']
