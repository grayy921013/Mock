from django.shortcuts import render
from mocking.forms import *
from django.contrib.auth import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import *
from django.http import *

# Create your views here.
def user_register(request):

    # validate
    form = RegistrationForm(request.POST)

    if not form.is_valid():
        return JsonResponse(dict(result=404))

    # create new user
    new_user = User.objects.create_user(username=form.cleaned_data["username"],
                                        password=form.cleaned_data["pwd"],
                                        first_name=form.cleaned_data["first_name"],
                                        last_name=form.cleaned_data["last_name"],
                                        email=form.cleaned_data["email"],
                                        is_active=False)

    profile = Profile()
    new_user.profile = profile
    profile.save()
    new_user.save()

    return JsonResponse(dict(result=404))



def user_login(request):

    if request.user.is_authenticated():
        return JsonResponse(dict(result=200))
    # validate
    form = LoginForm(request.POST)

    if not form.is_valid():
        return JsonResponse(dict(result=404))

    username = form.cleaned_data["username"]
    password = form.cleaned_data["pwd"]
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse(dict(result=200))
    else:
        return JsonResponse(dict(result=404, data="Username or password incorrect"))