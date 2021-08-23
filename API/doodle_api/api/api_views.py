import os
import tensorflow as tf
import keras
import requests
from django.http import Http404
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.models import QuizQuestion, Quiz, UserQuizMark, Sketch, DrawnSketch
from rest_framework import generics
from api.permissions import IsStaff
import cv2
import numpy as np
from api.serializers import QuizQuestionSerializer, QuizMarksSerializer, SketchSerializer
from api.models import User
from django.conf import settings


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

    def get_queryset(self, user, quiz):
        try:
            obj = UserQuizMark.objects.filter(user=user, quiz=quiz).order_by('timestamp').reverse()[:2]
        except UserQuizMark.DoesNotExist:
            raise Http404

        return obj

    def get_overall_score(self, user):
        """ Get average score for Iq and Subject quizzes """

        quizzes = ['iq', 'math', 'english']

        prev_scores = []
        new_scores = []

        for quiz in quizzes:
            quiz_obj = self.get_object(quiz)
            queryset = self.get_queryset(user, quiz_obj)

            try:
                new_scores.append(queryset[0].marks)
                prev_scores.append(queryset[1].marks)
            except:
                new_scores.append(queryset[0].marks)
                prev_scores.append(0)

        import statistics

        return statistics.mean(prev_scores), statistics.mean(new_scores)

    def get_final_score(self, user):
        """ Get overall score for Iq, subject, speech and draw quiz """

        iq_subject_score = self.get_overall_score(user=user)

        try:
            speech_score = UserQuizMark.objects.filter(user=user, quiz=self.get_object('speech_training')).latest(
                'timestamp').marks
            drawing_score = UserQuizMark.objects.filter(user=user, quiz=self.get_object('drawing')).latet(
                'timestamp').marks
        except UserQuizMark.DoesNotExist:
            raise Http404

        avg_speech_drawing_score = speech_score + drawing_score

        return (iq_subject_score + avg_speech_drawing_score) / 2

    def get(self, request, *args, **kwargs):
        """
            Returns the average score for iq, maths english
            /quiz_performance/overall_score/ - endpoint to get average score for Iq and Subject quizzes
            /quiz_performance/final_score/    - endpoint to get final average score
        """

        # if the requested is average of  iq and subject related quiz marks
        if kwargs['slug'] == 'overall_score':
            prev_score, new_score = self.get_overall_score(request.user.id)

            if new_score >= 9:
                detail = "Your child's performance is very good. You're very lucky to have such a child"
                grade = 'Skillful'
            elif new_score >= 7:
                detail = 'Your child have average performance parents can encourage to child for performance even ' \
                         'better '
                grade = 'Developing'
            elif new_score >= 5:
                detail = "Better than ineffective but parents still need to focus on child's education"
                grade = 'Minimally Effective'
            else:
                detail = 'Parent should pay serious attention to their child!'
                grade = 'Ineffective'

            context = {
                'detail': detail,
                'grade': grade,
                'score': new_score,
                'progress': '{}%'.format(new_score - prev_score)
            }

        elif kwargs['slug'] == 'final_score':
            score = self.get_final_score(user=request.user.id)

            context = {
                'detail': {
                    'previous_score': self.get_overall_score(user=request.user.id),
                    'current_score': {
                        'score': self.get_final_score(user=request.user.id),

                    }
                }
            }

        return Response(context)


class GetSketchAPIView(APIView):
    """ GetSketchAPIView - returns random image to draw """

    def get_object(self):
        return Sketch.objects.order_by('?')[0]

    def get(self, request, format=None):
        serializer = SketchSerializer(self.get_object())
        return Response(serializer.data)


class PredictAPIView(APIView):
    """ PredictAPIView - returns predictions for the given sketch """

    def get_object(self, **kwargs):
        try:
            obj = Sketch.objects.get(**kwargs)
        except Sketch.DoesNotExist:
            raise Http404
        return obj

    def get_processed_input_img(self, image_path, size=64):
        """ Preprocess user input image to feed to the model """

        image_path = os.path.join(settings.MEDIA_ROOT, image_path)
        test_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        test_img = cv2.resize(test_img, dsize=(64, 64), interpolation=cv2.INTER_CUBIC)
        thresh = 250
        test_img = cv2.threshold(test_img, thresh, 255, cv2.THRESH_BINARY)[1]
        test_img = test_img.reshape((1, size, size, 1)).astype(np.float32)/255

        print(test_img)
        return test_img

    def save_drawing_score(self, user, quiz, marks):
        """ Stores the marks for a quiz """

        obj = UserQuizMark.objects.create(user=user, quiz=quiz, marks=marks*10)
        return obj

    def post(self, request, format=None):
        sketch_name = self.get_object(id=request.POST['sketch_id'])

        image = request.FILES['image']

        user = User.objects.get(id=1)

        sketch_obj = DrawnSketch.objects.create(user=user, image=request.FILES['image'], image_name=sketch_name)
        path = str(sketch_obj.image.name)
        sketch = self.get_processed_input_img(path)

        reconstructed_model = keras.models.load_model('static/model/doodle_cnn/model.h5', compile=False)
        pred = reconstructed_model.predict(sketch)
        # print('\n\n\npredictions: ',  reconstructed_model.predict_proba(sketch))
        top_3 = np.argsort(-pred)[:, 0:3].ravel()

        print('\n\n\n\n\nTop 3: ', top_3, '\n\n ravel:', top_3.ravel())

        # categories = ['airplane', 'apple', 'bus', 'flower', 'pineapple']
        # categories = ['airplane', 'alarm clock', 'ant', 'apple', 'bus', 'dog', 'face', 'fish', 'flower', 'ice cream']
        categories = ['airplane', 'ant', 'apple', 'bus', 'face', 'fish', 'guitar', 'scissors', 'sun', 't-shirt']

        sketch_index = categories.index(sketch_name.name.lower())

        print('\n\n\n', sketch_index)

        if sketch_index == top_3[0]:
            score = 0.8
            similarity = 'Similarity above 80%'
        elif sketch_index == top_3[1]:
            score = 0.6
            similarity = 'Similarity above 60%'
        elif sketch_index == top_3[2]:
            score = 0.4
            similarity = 'Similarity above 40%'
        else:
            score = 0.2
            similarity = 'Similarity bellow 40%'

        # save record
        self.save_drawing_score(user, Quiz.objects.get(name='drawing'), score)

        context = {
            'score': score,
            'detail': similarity
        }

        return Response(context, status=status.HTTP_201_CREATED)
