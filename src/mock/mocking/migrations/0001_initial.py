# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-20 14:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content', models.CharField(max_length=50)),
                ('handle', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content', models.CharField(default='', max_length=500)),
                ('active', models.BooleanField(default=True)),
                ('interviewee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interviewee', to=settings.AUTH_USER_MODEL)),
                ('interviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interviewer', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=500)),
                ('solution', models.CharField(max_length=500)),
                ('difficulty', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ProblemCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.FloatField(null=True)),
                ('age', models.IntegerField(null=True)),
                ('major', models.CharField(max_length=30, null=True)),
                ('school', models.CharField(max_length=30, null=True)),
                ('occupation', models.CharField(max_length=50, null=True)),
                ('bio', models.TextField(null=True)),
                ('avatar', models.ImageField(null=True, upload_to='')),
                ('status', models.IntegerField(null=True)),
                ('language', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mocking.Language')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='problem',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mocking.ProblemCategory'),
        ),
        migrations.AddField(
            model_name='interview',
            name='problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mocking.Problem'),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='interview',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mocking.Interview'),
        ),
    ]
