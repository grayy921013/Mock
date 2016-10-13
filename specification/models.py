from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Language(models.Model):
    name = models.CharField(max_length=50)


class Profile(models.Model):
    user = models.OneToOneField(User)
    rating = models.FloatField()
    age = models.IntegerField()
    major = models.CharField(max_length=30)
    school = models.CharField(max_length=30)
    occupation = models.CharField(max_length=50)
    bio = models.TextField()
    avatar = models.ImageField()
    status = models.IntegerField()
    language = models.ForeignKey(Language)


class ProblemCategory(models.Model):
    name = models.CharField(max_length=50)


class Problem(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    difficulty = models.IntegerField()
    category = models.ForeignKey(ProblemCategory)


class Interview(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.FileField()
    duration = models.TimeField()
    active = models.BooleanField()
    matched = models.BooleanField()
    problem = models.ForeignKey(Problem)
    interviewer = models.ForeignKey(User, related_name="interviewer")
    interviewee = models.ForeignKey(User, related_name="interviewee")
