from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from alert.models import RegistrationForm, AUser, AlertForm
from django.contrib.auth import authenticate, login 
from django.contrib import messages
import requests
import ast

def home(request):
    context = {}
    form = AlertForm()
    context['form'] = form
    payload = {'user_id' : request.user}
    r = requests.get("http://198.211.103.89:9876/alerts", data=payload)
    alertList = ast.literal_eval(r.content)
    context['myAlerts'] = alertList
    for alert in alertList:
        print alert['alert_when']
    return render_to_response("home.html", context, context_instance=RequestContext(request))

def alert(request):
    context = {}
    form = AlertForm(request.POST)
    context['form'] = form
    if form.is_valid():
        payload = {'delivery_type' : request.POST['delivery_type'], 
                   'destination' : request.POST['phone'], 
                   'threshold' : request.POST['threshold'], 
                   'alert_when' : request.POST['alert_when'], 
                   'user_id' : str(request.user)}
        print payload
        r = requests.post("http://198.211.103.89:9876/alerts", data=payload)
        print r
        if r.status_code == requests.codes.ok:
            messages.add_message(request, messages.INFO, 'You added an alert successfully.')
        else:
            messages.add_message(request, messages.INFO, 'You failed to createyour alert. Please try again later.')
    return redirect("/") 

def myLogin(request):
    context = {}
    if request.POST:
        username = request.POST['Email']
        print username
        password = request.POST['Password']
        print password
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect("/") 
        else:
            context['formErrors'] = True 
    return render_to_response("home.html", context, context_instance=RequestContext(request))

def register(request):
    context = {}
    context['form'] = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            m = AUser.objects
            m.create_user(request.POST["email"], request.POST["password"])
            user = authenticate(username=request.POST["email"], password=request.POST["password"])
            if user is not None:
                login(request, user)
                return render_to_response("home.html", context, context_instance=RequestContext(request))
            else:
                print "Error logging in message"
        else:
            context['form'] = form
        
    return render_to_response("register.html", context, context_instance=RequestContext(request))
