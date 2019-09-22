from django.shortcuts import render
from django.http import HttpResponse
from .models import Question
from django.template import loader

# Create your views here.
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    #template = loader.get_template('polls/index.html')
    context = {'latest_question_list': latest_question_list,}
    #return HttpResponse(template.render(context, request))
    #Here's cool shortcut. Render returns HttpRequest object as well with given context and template
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    return HttpResponse("Yor're looking at the question %s." % question_id)

def results(request, question_id):
    response = "You're looking at the result of the question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on the question %s." % question_id)
