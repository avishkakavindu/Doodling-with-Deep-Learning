from datetime import datetime
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class UserAccountManager(BaseUserManager):
    """ UserAccountManager - handles actions of User model """

    def create_user(self, username, email, password=None, **kwargs):
        if username is None:
            raise TypeError('User need to have username!')
        if email is None:
            raise TypeError('User need to have Email!')

        user = self.model(username=username, email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password, **kwargs):
        if password is None:
            raise TypeError("Password shouldn't be None!")

        user = self.create_user(username, email, password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        # activate super-user
        s_user = User.objects.get(email=email)
        s_user.is_active = True
        s_user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """ User model - stores user data """

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email


class Quiz(models.Model):
    """ Quiz model - stores quiz data """

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class UserQuizMark(models.Model):
    """ UserQuiz model - the pivot table of Quiz and User models """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    marks = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    timestamp = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return '{} - {}'.format(self.user, self.quiz)


class QuizQuestion(models.Model):
    """ QuizQuestion model - stores questions that belongs to a quiz"""

    quiz = models.ForeignKey(Quiz, null=False, blank=False, on_delete=models.CASCADE, related_name='question_set')
    question = models.CharField(max_length=255)
    image = models.ImageField(upload_to='quiz_images/', null=True, blank=True)
    dummy_answer1 = models.CharField(max_length=255)
    dummy_answer2 = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)

    def __str__(self):
        return 'Question{}'.format(self.quiz, self.question)


class Sketch(models.Model):
    """ Sketch model - stores sketch pictures that need to draw """

    image = models.ImageField(upload_to='quiz_images')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class DrawnSketch(models.Model):
    """ DrawnSketch model - stores sketches drawn by the user """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    marks = models.ForeignKey(UserQuizMark, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='sketches')
    image_name = models.ForeignKey(Sketch, on_delete=models.CASCADE)
    
    def __str__(self):
        return '{}-{}'.format(self.user, self.image_name)