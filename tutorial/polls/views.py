#Interesting class named 'shortcuts' contains well shortucts like returning render instead of HttpResponse and get_object_or_404 method
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from .models import Question,Choice
from django.template import loader
from django.urls import reverse
from django.db.models import F
from django.views import generic

# Create your views here.
#Old view without generic
"""def index(request):
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    #template = loader.get_template('polls/index.html')
    #context = {'latest_question_list': latest_question_list,}
    #return HttpResponse(template.render(context, request))
    #Here's cool shortcut. Render returns HttpRequest object as well with given context and template
    #return render(request, 'polls/index.html', context)"""
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'
    
    def get_queryset(self):
        """Return the last five questions"""
        return Question.objects.order_by('-pub_date')[:5]

#Old view
"""def detail(request, question_id):
    #Rewritten using get_object_or_404 method
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question doesn't exist")
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question':question})"""
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


#Old view
"""def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/result.html', {'question':question})"""
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/result.html'

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, "polls/detail.html", {'question':question, 'error_message':"You didn't select a choice"})
    else:
        #selected_choice.votes += 1 -- old typical variant
        #using F to avoid race condition
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
