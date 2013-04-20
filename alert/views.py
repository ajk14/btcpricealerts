from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from alert.models import RegistrationForm, AUser, AlertForm
from django.contrib.auth import authenticate, login 
from django.contrib import messages
import requests
import json

REQUEST_URL = "http://alerts.btcpricealerts.com:9876/alerts"

def loadAlerts(context, user):
    payload = {'user_id' : user}
    r = requests.get(REQUEST_URL, data=payload)
    print r.status_code
    print r.content
    alertList = json.loads(r.content)
    context['myAlerts'] = alertList['alerts']
    return context

def home(request):
    context = {}
    form = AlertForm()
    context['form'] = form
    context = loadAlerts(context, request.user)
    return render_to_response("home.html", context, context_instance=RequestContext(request))

def delete(request):
    context = {}
    id = request.GET['id']
    url = REQUEST_URL + "alerts/" + id
    r = requests.delete(url)
    print r.status_code
    return redirect("/")


def alert(request):
    context = {}
    form = AlertForm(request.POST)
    context['form'] = form
    if form.is_valid():
        if request.POST['delivery_type'] == 'SMS':
            destination = request.POST['phone']
        else:
            destination = request.user
        payload = {'delivery_type' : request.POST['delivery_type'], 
                   'destination' : destination,
                   'threshold' : request.POST['threshold'], 
                   'alert_when' : request.POST['alert_when'], 
                   'user_id' : str(request.user)}
        print payload
        r = requests.post(REQUEST_URL, data=payload)
        print r
        if r.status_code == requests.codes.ok:
            messages.add_message(request, messages.INFO, 'You added an alert successfully.')
        else:
            messages.add_message(request, messages.INFO, 'You failed to createyour alert. Please try again later.')
    else:
        context = loadAlerts(context, request.user)
        return render_to_response("home.html", context, context_instance=RequestContext(request))
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
                return redirect("/")    
            #return render_to_response("home.html", context, context_instance=RequestContext(request))
            else:
                print "Error logging in message"
        else:
            context['form'] = form
        
    return render_to_response("register.html", context, context_instance=RequestContext(request))
