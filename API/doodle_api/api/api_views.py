import requests
from django.http import Http404
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.models import QuizQuestion, Quiz, UserQuizMark
from rest_framework import generics
from api.permissions import IsStaff

from api.serializers import QuizQuestionSerializer, QuizMarksSerializer
from api.models import User


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
    """ QuizQuestionAPIView - Retrieve 10 questions for a quiz """

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
        ).order_by('?')[:2]
        questions_serialized = QuizQuestionSerializer(questions, many=True)

        return Response(questions_serialized.data)


class QuizMarksAPIView(APIView):
    """ QUizMarksAPIView - add marks to relavant quiz """

    authentication_classes = [JWTTokenUserAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, name):
        try:
            return Quiz.objects.get(name=name)
        except Quiz.DoesNotExist:
            raise Http404

    def post(self, request, name, format=None):
        """ Calculate marks for a quiz """

        quiz = self.get_object(name)
        user = User.objects.get(id=request.user.id)

        marks = 0

        for answer in request.data:
            # check if quiz type is correct
            quiz_type = QuizQuestion.objects.get(id=answer['question']).quiz.name

            if name == quiz_type:
                actual_answer = QuizQuestion.objects.get(id=answer['question']).answer.lower()
                given_answer = answer['given_answer'].lower()

                if actual_answer == given_answer:
                    marks += 1
            else:
                return Response({'detail': 'Invalid data!'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        payload = {
            'user': user,
            'quiz': quiz,
            'marks': marks
        }

        serializer = QuizMarksSerializer(payload)

        context = {
            'detail': 'Marks recorded!',
            'marks': serializer.data
        }
        return Response(context)


class ScoreAPIView(APIView):
    """
        IQSubjectScoreAPIView - returns the average score for IQ, Math and English quizzes
    """

    authentication_classes = [JWTTokenUserAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, quiz):
        try:
            return Quiz.objects.get(name=quiz)
        except Quiz.DoesNotExist:
            raise Http404

    def get_iq_subject_score(self, user):
        """ Get average score for Iq and Subject """

        try:
            iq_score = UserQuizMark.objects.filter(user=user, quiz=self.get_object('iq')).latest('timestamp').marks
            math_score = UserQuizMark.objects.filter(user=user, quiz=self.get_object('math')).latest('timestamp').marks
            english_score = UserQuizMark.objects.filter(user=user, quiz=self.get_object('english')).latest('timestamp').marks
        except UserQuizMark.DoesNotExist:
            raise Http404

        return (iq_score + math_score + english_score)/3

    def get_overall_score(self, user):
        """ Get overall score for Iq, subject, speech and draw quiz """

        iq_subject_score = self.get_iq_subject_score

        try:
            speech_score = UserQuizMark.objects.filter(user=user, quiz=self.get_object('speech_training')).latest('timestamp').marks
            drawing_score = UserQuizMark.objects.filter(user=user, quiz=self.get_object('drawing')).latet('timestamp').marks
        except UserQuizMark.DoesNotExist:
            raise Http404

        avg_speech_drawing_score = speech_score + drawing_score

        return (iq_subject_score + avg_speech_drawing_score)/2

    def get(self, request, *args, **kwargs):
        """
            Returns the average score for iq, maths english
            /quiz_performance/iq_subject_score/ - endpoint to get average score for Iq and Subject quizzes
            /quiz_performance/overall_score/    - endpoint to get average score for
        """

        if kwargs['slug'] == 'iq_subject_score':
            score = self.get_iq_subject_score(user=request.user.id)

            if score >= 9:
                detail = "Your child's performance is very good. You're very lucky to have such a child"
                grade = 'Skillful'
            elif score >= 7:
                detail = 'Your child have average performance parents can encourage to child for performance even ' \
                         'better '
                grade = 'Developing'
            elif score >= 5:
                detail = "Better than ineffective but parents still need to focus on child's education"
                grade = 'Minimally Effective'
            else:
                detail = 'Parent should pay serious attention to their child!'
                grade = 'Ineffective'

            context = {
                'detail': detail,
                'grade': grade,
                'score': score,
            }

        return Response(context)