from django.urls import path
from api.api_views import UserActivationView


urlpatterns = [
    path('activate/<str:uid>/<str:token>/', UserActivationView.as_view(), name='user_activation'),
]