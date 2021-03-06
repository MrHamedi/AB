from django.shortcuts import redirect, render , reverse ,redirect ,get_object_or_404
from .models import Question 
from django.views.generic import ListView,DetailView,CreateView 
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CommentForm,QuestionForm
from django.urls import reverse
from .models import Comment
from django.contrib.auth.decorators import login_required
from .utility import like_status_finder
from django.db.models import Q
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger


def HomePageView(request,search=None):
    """
        This is the view of the homepage
    """
    search=request.GET.get("search")
    if(search):
        questions=Question.objects.filter(Q(title__icontains=search) | Q(body__icontains=search))
    else:
        questions=Question.objects.all()
    paginator=Paginator(questions,5)
    page=request.GET.get('page')
    try:
        questions=paginator.page(page)
    except PageNotAnInteger:
        #if page not an integer deliver the first page 
        questions=paginator.page(1)
    except EmptyPage:
        #if page is out of range deliver the last past
        questions=paginator.page(paginator.num)
    page_obj = paginator.get_page(page)
    return(render(request,"question/homepage.html",{"questions":questions,"page_obj":page_obj}))


@login_required
def question_detail_view(request,pk): 
    """
        This view will display the question detail and its comments with a form for makeing comment on question
    """
    question=get_object_or_404(Question,pk=pk)
    account=request.user.profile
    status=like_status_finder(account,question)
    comment_form=CommentForm()    
    return(render(request,"question/questionDetail.html",{"question":question,"comment_form":comment_form,"status":status}))


@login_required
def comment_form(request,pk):
    """
        This view will  save the client comment and redirect client to question 
    """
    question=Question.objects.get(id=pk)
    if(request.method=="POST"):
        form=CommentForm(data=request.POST)
        if(form.is_valid()):
            new_comment=form.save(commit=False)
            new_comment.author=request.user 
            new_comment.question=question
            new_comment.score=0
            new_comment.save()

    else:
        form=CommentForm()
    return(redirect("question:questionDetail",question.id))


class QuestionFormView(LoginRequiredMixin,CreateView):
    """
        This view will display a form for user to fill with his question.
    """
    model=Question
    form_class=QuestionForm
    template_name="question/question_form.html" 

    def form_valid(self, form):
        m_tags = form.cleaned_data['tags']
        obj = form.save(commit=False)
        obj.author= self.request.user
        obj.slug=obj.slug_maker()
        obj.save()        
        obj.tags.add(*m_tags)
        obj.save()
        return(redirect(obj.get_absolute_url()))

@login_required
def liker_view(request,order,pk):
    """
        This view will change the interest status of user to question. 
    """
    account=request.user.profile 
    question=get_object_or_404(Question,pk=pk)
    dislikers=question.disliked_by.all()
    likers=question.liked_by.all()
    if(order=="liked"):        
        if(account in likers):
            question.liked_by.remove(account)          
        elif(account in dislikers):
            question.disliked_by.remove(account)  
            question.liked_by.add(account)
        else:
            question.liked_by.add(account)
        if(account in dislikers):
            question.disliked_by.remove(account)          
    elif(order=="disliked"):
        if(account in dislikers):
            question.disliked_by.remove(account)
        elif(account in likers):
            question.liked_by.remove(account)
            question.disliked_by.add(account)
        else:
            question.disliked_by.add(account)

    return(redirect("question:questionDetail",question.id))

            

@login_required
def comment_liker_view(request,order,pk):
    """
        This view will change the interest status of user to question. 
    """
    account=request.user.profile 
    comment=get_object_or_404(Comment,pk=pk)
    dislikers=comment.disliked_by.all()
    likers=comment.liked_by.all()
    if(order=="liked"):        
        if(account in likers):
            comment.liked_by.remove(account)          
        elif(account in dislikers):
            comment.disliked_by.remove(account)  
            comment.liked_by.add(account)
        else:
            comment.liked_by.add(account)
        if(account in dislikers):
            comment.disliked_by.remove(account)          
    elif(order=="disliked"):
        if(account in dislikers):
            comment.disliked_by.remove(account)
        elif(account in likers):
            comment.liked_by.remove(account)
            comment.disliked_by.add(account)
        else:
            comment.disliked_by.add(account)

    return(redirect("question:questionDetail",comment.question.id))




