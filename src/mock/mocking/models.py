from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import *


# Create your models here.
class Language(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()
        
class Profile(models.Model):
    user = models.OneToOneField(User)
    rating = models.FloatField(null=True)
    age = models.IntegerField(null=True)
    major = models.CharField(null=True, max_length=30)
    school = models.CharField(null=True, max_length=30)
    occupation = models.CharField(null=True, max_length=50)
    bio = models.TextField(null=True)
    avatar = models.ImageField(upload_to = 'img', null=True)
    status = models.IntegerField(null=True)
    language = models.ForeignKey(Language, null=True)
    interview_credit = models.IntegerField(default=10)


class ProblemCategory(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()


class Problem(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    solution = models.CharField(max_length=500)
    difficulty = models.IntegerField()
    category = models.ForeignKey(ProblemCategory)

    def __str__(self):
        return self.name


class Interview(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=500, default='')
    active = models.BooleanField(default=True)
    problem = models.ForeignKey(Problem)
    interviewer = models.ForeignKey(User, related_name="interviewer")
    interviewee = models.ForeignKey(User, related_name="interviewee")


class ChatMessage(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=50)
    handle = models.CharField(max_length=50)
    interview = models.ForeignKey(Interview)

    @property
    def formatted_timestamp(self):
        return localtime(self.created_at).strftime('%b %-d %-I:%M %p')


class RateRecord(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    rate = models.IntegerField()
    rated_on = models.ForeignKey(User, related_name="rater_on")
    rated_by = models.ForeignKey(User, related_name="rater_by")
    interview = models.ForeignKey(Interview)
