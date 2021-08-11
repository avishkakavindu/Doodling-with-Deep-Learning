from django.urls import path
from api.api_views import UserActivationView, QuizCSVImportAPIView, QuizQuestionAPIView

urlpatterns = [
    path('activate/<str:uid>/<str:token>/', UserActivationView.as_view(), name='user_activation'),
    path('upload_csv/', QuizCSVImportAPIView.as_view(), name='csv_import'),
    path('quiz_questions/<str:name>/', QuizQuestionAPIView.as_view(), name='quiz_questions'),
]