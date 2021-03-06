from rest_framework import serializers, status
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from api.models import Quiz, QuizQuestion, UserQuizMark, Sketch
import numpy as np

User = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'password']


class QuizQuestionSerializer(serializers.ModelSerializer):
    """ Serializer for quiz questions """

    question = serializers.CharField(read_only=True)
    image = serializers.CharField(read_only=True)
    dummy_answer1 = serializers.CharField(read_only=True)
    dummy_answer2 = serializers.CharField(read_only=True)
    answer = serializers.CharField(read_only=True)

    class Meta:
        model = QuizQuestion
        fields = '__all__'


# class QuizSerializer(serializers.ModelSerializer):
#     """ Serializer for Quizzes """
#
#     name = serializers.CharField(read_only=True)
#     questions = QuizQuestionSerializer(many=True, read_only=True, source='question_set')
#
#     class Meta:
#         model = Quiz
#         fields = '__all__'
#
#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         representation['questions'] = np.random.choice(
#             representation['questions'], 3, replace=False)
#
#         return representation


class QuizMarksSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(required=True, queryset=User.objects.all())
    quiz = serializers.PrimaryKeyRelatedField(required=True, queryset=Quiz.objects.all())
    marks = serializers.FloatField(min_value=0, max_value=1)

    class Meta:
        model = UserQuizMark
        fields = '__all__'


class SketchSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)
    name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Sketch
        fields = '__all__'

