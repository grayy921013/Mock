from mocking.forms import *
from django.contrib.auth import *
from django.contrib.auth.decorators import login_required
from django.http import *
from django.shortcuts import *
from datetime import *
from django.db.models import Q
from django.utils import timezone

from mimetypes import guess_type


# Create your views here.
def user_register(request):
    context = {}
    # ensure post method
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'register2.html', context)

    # validate
    form = RegistrationForm(request.POST)

    context['form'] = form
    if not form.is_valid():
        return render(request, 'register2.html', context)

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
        return render(request, 'login2.html', context)

    if request.user.is_authenticated():
        return redirect(reverse("square"))
    # validate
    form = LoginForm(request.POST)

    if not form.is_valid():
        context['form'] = form
        return render(request, 'login2.html', context)

    username = form.cleaned_data["username"]
    password = form.cleaned_data["pwd"]
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect(reverse("square"))
    else:
        context['form'] = form
        form.add_error(None, "Username or password incorrect")
        return render(request, 'login2.html', context)


@login_required
def create_interview(request):
    interview = Interview(interviewer=request.user, interviewee=request.user)
    interview.save()
    print(interview.interviewee.username)

    return JsonResponse(dict(result=200, data=interview.pk))


@login_required
def get_interview_list(request):
    now = timezone.now()
    start_time = now - timedelta(minutes=45)
    # filter interviews that start more than 45 mins ago, which have already ended
    interviews = Interview.objects.filter(created_at__lt=start_time). \
        filter(Q(interviewee=request.user) | Q(interviewer=request.user)).order_by('-created_at')
    list = []
    for interview in interviews:
        element = {}
        element['id'] = interview.pk
        element['interviewer_name'] = interview.interviewer.username
        element['interviewee_name'] = interview.interviewee.username
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
    context['user_name'] = request.user.username

    context['user_id'] = request.user.pk
    if interview.interviewee_id == request.user.pk:
        context['peer_id'] = interview.interviewer_id
    else:
        context['peer_id'] = interview.interviewee_id
    problem = Problem.objects.get(name=interview.problem)
    context['problem_name'] = problem.name
    context['problem_description'] = problem.description
    context['problem_difficulty'] = problem.difficulty
    context['problem_category'] = problem.category
    context['messages'] = ChatMessage.objects.filter(interview=interview).order_by('created_at')
    languages = Language.objects.all()
    context['language'] = languages
    return render(request, "room.html", context)


@login_required
def square(request):
    return render(request, "square.html")


@login_required
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

    ca = ProblemCategory.objects.get(name=form.cleaned_data["category"])
    # create problem
    new_problem = Problem(name=form.cleaned_data["name"],
                          description=form.cleaned_data["description"],
                          solution=form.cleaned_data["solution"],
                          difficulty=form.cleaned_data["difficulty"],
                          category=ca,
                          )
    new_problem.save()
    return redirect(reverse("add_problem"))


@login_required
def add_category(request):
    context = {}
    if request.method == 'GET':
        context['form'] = AddProblemCategoryForm()
        return render(request, 'category.html', context)

    form = AddProblemCategoryForm(request.POST)

    context['form'] = form
    if not form.is_valid():
        return render(request, 'category.html', context)

    new_category = ProblemCategory(name=form.cleaned_data["name"], )
    new_category.save()
    categories = ProblemCategory.objects.all()
    context = {'categories': categories, 'form': form}
    return render(request, 'category.html', context)


@login_required
def add_language(request):
    context = {}
    if request.method == 'GET':
        context['form'] = AddLanguageForm()
        return render(request, 'language.html', context)

    form = AddLanguageForm(request.POST)

    context['form'] = form
    if not form.is_valid():
        return render(request, 'language.html', context)

    new_language = Language(name=form.cleaned_data["name"], );
    new_language.save()
    languages = Language.objects.all()
    context = {'languages': languages, 'form': form}
    return render(request, 'language.html', context)


@login_required
def get_problem_list(request):
    problems = Problem.objects.all()
    list = []
    for problem in problems:
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
def get_problem(request, pid):
    problem = Problem.objects.get(id=pid)
    element = {}
    element['id'] = problem.pk
    element['name'] = problem.name
    element['description'] = problem.description
    element['solution'] = problem.solution
    element['difficulty'] = problem.difficulty
    element['category'] = problem.category.name

    return JsonResponse(dict(result=200, data=element))


@login_required
def choose_role(request):
    now = timezone.now()
    start_time = now - timedelta(minutes=45)
    interviews = Interview.objects.filter(created_at__gt=start_time). \
        filter(Q(interviewee=request.user) | Q(interviewer=request.user)).order_by('-created_at')
    if len(interviews) > 0:
        # ongoing interviews
        return redirect(reverse("main", args=(interviews[0].pk,)))
    context = {}
    context['form'] = ChooseRoleForm()
    context['language'] = request.user.profile.language
    context['interview_credit'] = request.user.profile.interview_credit
    context['bio'] = request.user.profile.bio
    context['occupation'] = request.user.profile.occupation
    context['rating'] = request.user.profile.rating
    context['occupation'] = request.user.profile.occupation
    context['first_name'] = request.user.profile.user.first_name
    context['id'] = request.user.profile.user.pk
    context['last_name'] = request.user.profile.user.last_name
    context['age'] = request.user.profile.age
    return render(request, 'choose_role.html', context)


@login_required
def rate(request):
    parameters = {}
    for key in request.POST:
        parameters[key] = request.POST[key]
    parameters["rated_by"] = request.user.pk
    form = RateForm(parameters)
    if not form.is_valid():
        return JsonResponse(dict(result=404, data=form.errors))
    record = RateRecord(rated_on_id=form.cleaned_data["rated_on"], rated_by_id=form.cleaned_data["rated_by"],
                        interview_id=form.cleaned_data["interview"], rate=form.cleaned_data["rate"])
    record.save()
    new_count = RateRecord.objects.filter(rated_on_id=form.cleaned_data["rated_on"]).count()
    profile = User.objects.get(pk=form.cleaned_data["rated_on"]).profile
    if not profile.rating:
        profile.rating = record.rate
    else:
        profile.rating = (profile.rating * (new_count - 1) + record.rate) / new_count
    profile.save()
    return JsonResponse(dict(result=200))


@login_required
def edit_profile(request):
    context = {}
    profile_to_edit = get_object_or_404(Profile, user=request.user)
    if request.method == 'GET':
        context['form'] = ProfileForm(instance=profile_to_edit, initial={'first_name': request.user.first_name, \
                                                                         'last_name': request.user.last_name})
        return render(request, 'edit_profile.html', context)

    form = ProfileForm(request.POST, request.FILES, instance=profile_to_edit)

    if not form.is_valid():
        context['form'] = ProfileForm(instance=profile_to_edit)
        return render(request, 'edit_profile.html', context)

    form.save()
    request.user.first_name = form.cleaned_data['first_name']
    request.user.last_name = form.cleaned_data['last_name']
    request.user.save()

    return redirect(reverse("edit_profile"))


@login_required
def get_avatar(request, userid):
    user = get_object_or_404(User, id=userid)
    profile = get_object_or_404(Profile, user=user)
    if not profile.avatar:
        raise Http404
    content_type = guess_type(profile.avatar.name)
    return HttpResponse(profile.avatar, content_type=content_type)


@login_required
def get_profile(request, proid):
    profile = Profile.objects.get(id=proid)

    context = {"profile": profile}
    return render(request, 'view_profile.html', context)


@login_required
def get_rate_board(request):
    profiles = Profile.objects.order_by('-rating').filter(rating__isnull=False)
    list = []
    for profile in profiles:
        element = {}
        element['userid'] = profile.user.id
        element['id'] = profile.id
        element['first_name'] = profile.user.first_name
        element['last_name'] = profile.user.last_name
        element['rating'] = "%.2f" % profile.rating
        element['major'] = profile.major
        # element['language'] = profile.language.name
        list.append(element)
    return JsonResponse(dict(result=200, data=list))


@login_required
def rate_board(request):
    return render(request, 'rate_board.html')


@login_required
def get_rate_record(request):
    parameters = {}
    for key in request.GET:
        parameters[key] = request.GET[key]
    parameters["rated_by"] = request.user.pk
    form = GetRateForm(parameters)
    if not form.is_valid():
        return JsonResponse(dict(result=404, data=form.errors))
    query = RateRecord.objects.filter(interview_id=form.cleaned_data['interview'],
                                      rated_by_id=form.cleaned_data['rated_by'])
    if query.count() > 0:
        return JsonResponse(dict(result=200, data=query[0].rate))
    else:
        return JsonResponse(dict(result=404, data="not rated yet"))
