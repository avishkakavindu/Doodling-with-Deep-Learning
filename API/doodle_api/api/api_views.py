import requests
from django.http import Http404
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.models import QuizQuestion, Quiz
from rest_framework import generics
from api.permissions import IsStaff

from api.serializers import QuizQuestionSerializer


class UserActivationView(APIView):
    """
        Activates newly registered user by calling '/users/activation/' end point
        https://djoser.readthedocs.io/en/latest/base_endpoints.html
    """

    def get(self, request, uid, token, format=None):
        payload = {
            'uid': uid,
            'token': token
        }
        # call user activation endpoint
        url = 'http://localhost:8000/api/auth/users/activation/'
        response = requests.post(url, data=payload)

        if response.status_code == 204:
            return Response({'detail': 'Account activated successfully!'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)


class QuizCSVImportAPIView(APIView):
    """
        Populate quiz questions using csv data by calling 'api/upload_csv/'
     """

    authentication_classes = [JWTTokenUserAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_obj = request.FILES['file']
        try:
            quiz = Quiz.objects.get(name=request.data.get('quiz'))
        except Quiz.DoesNotExist:
            quizes = Quiz.objects.values_list('name', flat=True)

            context = {
                'detail': 'Invalid Quiz Type!',
                'quiz_types': quizes
            }

            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        import pandas as pd

        df = pd.read_csv(file_obj)
        df.info()

        model_instances = [
            QuizQuestion(
                quiz=quiz,
                question=row[1],
                image=str(row[2]),
                dummy_answer1=str(row[3]),
                dummy_answer2=str(row[4]),
                answer=str(row[5])
            ) for row in df.itertuples()]
        QuizQuestion.objects.bulk_create(model_instances)

        return Response({'detail': 'File uploaded successfully!'}, status=status.HTTP_201_CREATED)


# class QuizQuestionRetrieveAPIView(generics.RetrieveAPIView):
#     """
#
#     """
#
#     authentication_classes = [JWTTokenUserAuthentication]
#     permission_classes = [permissions.IsAuthenticated]
#
#     serializer_class = QuizSerializer
#     queryset = Quiz.objects.all().order_by('?')
#     lookup_field = 'name'


class QuizQuestionAPIView(APIView):
    """ QuezQuestionAPIView - Retrieve 10 questions for a quiz """

    authentication_classes = [JWTTokenUserAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuizQuestionSerializer

    def get_object(self, name):
        try:
            return Quiz.objects.get(name=name)
        except Quiz.DoesNotExist:
            raise Http404

    def get(self, request, name, format=None):
        """
            Return a 10 questions.
        """

        questions = QuizQuestion.objects.filter(
            quiz=self.get_object(name)
        ).order_by('?')[:10]
        questions_serialized = QuizQuestionSerializer(questions, many=True)

        return Response(questions_serialized.data)


