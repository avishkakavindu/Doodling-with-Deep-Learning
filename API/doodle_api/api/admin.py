from django.contrib import admin
from api.models import User, Quiz, QuizQuestion, UserQuizMark, Sketch, DrawnSketch


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


@admin.register(UserQuizMark)
class UserQuizMarkAdmin(admin.ModelAdmin):
    list_display = ['id', 'quiz', 'marks']
    search_fields = ['user', 'quiz', 'question']
    list_filter = ['quiz']


@admin.register(Sketch)
class SketchAdmin(admin.ModelAdmin):
    list_display = ['id', 'image', 'name']
    search_fields = ['id', 'image', 'name']


@admin.register(DrawnSketch)
class DrawnSketchAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'image_name', 'marks']
    search_fields = ['id', 'user', 'image_name']
    filter_fields = ['image_name']

