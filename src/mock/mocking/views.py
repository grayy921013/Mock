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
    #interview = Interview.objects.all()
    #interview.delete()
    #x = ProblemCategory(name = "Array")
    #x.save()

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
        form.add_error(None, "Username or password incorrect")
        return render(request, 'login.html', context)

@login_required
def create_interview(request):
    interview = Interview(interviewer=request.user, interviewee=request.user)
    interview.save()
    print(interview.interviewee.username)

    return JsonResponse(dict(result=200, data=interview.pk))

@login_required
def get_interview_list(request):
    interviews = Interview.objects.all().order_by('-created_at')
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
    context['owner_id'] = interview.interviewee.pk
    context['user_id'] = request.user.pk
    context['messages'] = ChatMessage.objects.filter(interview=interview).order_by('created_at')
    return render(request, "room.html", context)

@login_required
def square(request):
    return render(request, "Square.html")

def enter_interview_room(request):
    return render(request, "room.html")

def add_problem(request):
    context = {}
    # ensure post method
    if request.method == 'GET':
        context['form'] = AddProblemForm()
        return render(request, 'problem.html', context)

    # validate
    form = AddProblemForm(request.POST)

    context['form'] = form
    if not form.is_valid():
        return render(request, 'problem.html', context)

    ca = ProblemCategory.objects.get(name = form.cleaned_data["category"])
    # create problem
    new_problem = Problem(name=form.cleaned_data["name"],
                          description=form.cleaned_data["description"],
                          solution=form.cleaned_data["solution"],
                          difficulty=form.cleaned_data["difficulty"],
                          category=ca,
                          )
    new_problem.save()
    return redirect(reverse("square"))

def get_problem_list(request):
    problems = Problem.objects.all()
    list = []
    for  problem in problems:
        element = {}
        element['id'] = problem.pk
        element['name'] = problem.name
        element['description'] = problem.description
        element['solution'] = problem.solution
        element['difficulty'] = problem.difficulty
        element['category'] = problem.category.name
        list.append(element)

    return JsonResponse(dict(result=200, data=list))

@login_required
def match_test(request):
    return render(request, "match_test.html")
