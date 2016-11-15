"""mock URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
import django.contrib.auth.views
import mocking.views

urlpatterns = [
    url(r'^square$', mocking.views.square, name='square'),
    url(r'^interview/(?P<interview_id>\d+)$', mocking.views.interview, name='main'),
    url(r'^login$', mocking.views.user_login,  name='login'),
    url(r'^logout$', django.contrib.auth.views.logout_then_login, name='logout'),
    url(r'^register$', mocking.views.user_register, name='register'),
    url(r'^create_interview$', mocking.views.create_interview, name='create_interview'),
    url(r'^get_interview_list', mocking.views.get_interview_list, name='get_interview_list'),
    url(r'^add_problem', mocking.views.add_problem, name = 'add_problem'),
    url(r'^get_problem_list', mocking.views.get_problem_list, name='get_problem_list'),
    url(r'^match_test', mocking.views.match_test, name='match_test'),
]
