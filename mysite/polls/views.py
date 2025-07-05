from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin #flaw 1: Use this to make login more secure
from .forms import RegisterForm

from .models import Choice, Question, Vote


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.filter(
        pub_date__lte=timezone.now()
         ).order_by('-pub_date')[:5]

class DetailView(LoginRequiredMixin, generic.DetailView): #flaw2
    model = Question
    template_name = 'polls/detail.html'
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(LoginRequiredMixin, generic.DetailView): #flaw2
    model = Question
    template_name = 'polls/results.html'

def login_view(request): #flaw1
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("polls:index") 
        else:
            return render(request, "polls/login.html", {"error": "Virheellinen tunnus tai salasana"})
    return render(request, "polls/login.html") 

def logout_view(request):
    logout(request)
    return redirect("polls:index")

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            return redirect("polls:login") 
    else:
        form = RegisterForm()
    return render(request, "polls/register.html", {"form": form})

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('polls/index.html')
    context = {
        'latest_question_list': latest_question_list,
    }
    return HttpResponse(template.render(context, request))

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    if Vote.objects.filter(user=request.user, question=question).exists():#flaw3
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You have already voted on this question.",
        })

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a valid choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()

        Vote.objects.create(user=request.user, question=question) #flaw3

        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))