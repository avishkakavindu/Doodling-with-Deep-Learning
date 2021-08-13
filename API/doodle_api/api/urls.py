from django.urls import path
from api.api_views import UserActivationView, QuizCSVImportAPIView, QuizQuestionAPIView, QuizMarksAPIView, ScoreAPIView

urlpatterns = [
    path('activate/<str:uid>/<str:token>/', UserActivationView.as_view(), name='user_activation'),
    path('upload_csv/', QuizCSVImportAPIView.as_view(), name='csv_import'),
    path('quiz_questions/<str:name>/', QuizQuestionAPIView.as_view(), name='quiz_questions'),
    path('quiz_marks/record/<str:name>/', QuizMarksAPIView.as_view(), name='record_quiz_marks'),
    path('quiz_performance/<slug>/', ScoreAPIView.as_view(), name='scores'),
]