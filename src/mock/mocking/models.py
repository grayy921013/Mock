from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Language(models.Model):
    name = models.CharField(max_length=50)


class Profile(models.Model):
    user = models.OneToOneField(User)
    rating = models.FloatField(null=True)
    age = models.IntegerField(null=True)
    major = models.CharField(null=True, max_length=30)
    school = models.CharField(null=True, max_length=30)
    occupation = models.CharField(null=True, max_length=50)
    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True)
    status = models.IntegerField(null=True)
    language = models.ForeignKey(Language, null=True)


class ProblemCategory(models.Model):
    name = models.CharField(max_length=50)


class Problem(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    difficulty = models.IntegerField()
    category = models.ForeignKey(ProblemCategory)


class Interview(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # code = models.FileField()
    # duration = models.TimeField()
    # active = models.BooleanField()
    # matched = models.BooleanField()
    # problem = models.ForeignKey(Problem)
    interviewer = models.ForeignKey(User, related_name="interviewer")
    # interviewee = models.ForeignKey(User, related_name="interviewee")