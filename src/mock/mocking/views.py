from mocking.forms import *
from django.contrib.auth import *
from django.contrib.auth.decorators import login_required
from django.http import *
from django.shortcuts import *

# Create your views here.
def user_register(request):
    # clean all data for debug
    #user = User.objects.all()
    #user.delete()
    #user1 = Profile.objects.all()
    #user1.delete()

    context = {}
    # ensure post method
    if request.method == 'GET':
        context['form']  = RegistrationForm()
        return render(request, 'register.html',context)

    # validate
    form = RegistrationForm(request.POST)

    context['form'] = form
    if not form.is_valid():
        return render(request, 'register.html', context)

    # create new user
    new_user = User.objects.create_user(username=form.cleaned_data["username"],
                                        password=form.cleaned_data["pwd"],
                                        first_name=form.cleaned_data["first_name"],
                                        last_name=form.cleaned_data["last_name"],
                                        email=form.cleaned_data["email"])
    profile = Profile()
    new_user.profile = profile
    new_user.save()
    profile.save()
    user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["pwd"])
    login(request, user)
    return redirect(reverse("square"))



def user_login(request):
    context = {}

    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'login.html',context)

    if request.user.is_authenticated():
        return redirect(reverse("square"))
    # validate
    form = LoginForm(request.POST)

    if not form.is_valid():
        context['form'] = form
        return render(request, 'login.html', context)

    username = form.cleaned_data["username"]
    password = form.cleaned_data["pwd"]
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect(reverse("square"))
    else:
        context['form'] = form
        return render(request, 'login.html', context)

@login_required
def create_interview(request):
    interview = Interview(interviewer=request.user)
    interview.save()
    return JsonResponse(dict(result=200, data=interview.pk))

@login_required
def get_interview_list(request):
    interviews = Interview.objects.all()
    list = []
    for interview in interviews:
        element = {}
        element['id'] = interview.pk
        element['userid'] = interview.interviewer.pk
        element['username'] = interview.interviewer.username
        element['content'] = interview.content
        list.append(element)

    return JsonResponse(dict(result=200, data=list))

@login_required
def interview(request, interview_id):
    context = {}
    try:
        interview = Interview.objects.get(pk=interview_id)
    except Interview.DoesNotExist:
        raise Http404
    context['content'] = interview.content
    context['interview_id'] = interview.pk
    context['user_id'] = request.user.pk
    return render(request, "interview.html", context)

@login_required
def square(request):
    return render(request, "Square.html")

def enter_interview_room(request):
    return render(request, "room.html")