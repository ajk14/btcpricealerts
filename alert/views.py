from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from alert.models import RegistrationForm, AUser, AlertForm
from django.contrib.auth import authenticate, login 
from django.contrib import messages
import requests
import json

REQUEST_URL = "http://alerts.btcpricealerts.com:9876/alerts"
ALERT_SUCCESS = "You've created a new alert!"
ALERT_FAILURE = "Your alert failed to be created. Please try again later."
MAX_OUTSTANDING_ALERTS = 10
MAX_ALERTS_EXCEEDED = "Sorry, you can't create more than " + str(MAX_OUTSTANDING_ALERTS) + " alerts."

def loadAlerts(user):
    payload = {'user_id' : user}
    try:
        r = requests.get(REQUEST_URL, data=payload)
    except requests.RequestException:
        return None
    alertList = json.loads(r.content)
    return alertList['alerts']

def home(request):
    context = {}
    form = AlertForm()
    context['form'] = form
    context['myAlerts'] = loadAlerts(request.user)
    return render_to_response("home.html", context, context_instance=RequestContext(request))

def delete(request):
    context = {}
    id = request.GET['id']
    url = REQUEST_URL + "/" + id
    try:
        r = requests.delete(url)
    except requests.RequestException:
        return redirect("/")
    return redirect("/")

def alert(request):
    context = {}
    form = AlertForm(request.POST)
    context['form'] = form
    if form.is_valid():
        if len(loadAlerts(request.user)) >= MAX_OUTSTANDING_ALERTS:
            messages.error(request, MAX_ALERTS_EXCEEDED)
            return redirect("/")
        if request.POST['delivery_type'] == 'SMS':
            destination = request.POST['phone']
        else:
            destination = request.user
        payload = {'delivery_type' : request.POST['delivery_type'], 
                   'destination' : destination,
                   'threshold' : request.POST['threshold'], 
                   'alert_when' : request.POST['alert_when'], 
                   'user_id' : str(request.user)}
        try:
            r = requests.post(REQUEST_URL, data=payload)
        except requests.RequestException:
            messages.error(request, ALERT_FAILURE)
            return redirect("/")
        messages.success(request, ALERT_SUCCESS)
    else:
        context['myAlerts'] = loadAlerts(request.user)
        return render_to_response("home.html", context, context_instance=RequestContext(request))
    return redirect("/") 

def myLogin(request):
    context = {}
    if request.POST:
        username = request.POST['Email']
        password = request.POST['Password']
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
            m.create_user(request.POST["email"], request.POST["password"], is_active=False)
            user = authenticate(username=request.POST["email"], password=request.POST["password"])
            login(request, user)
            return redirect("/")    
        else:
            context['form'] = form
    return render_to_response("register.html", context, context_instance=RequestContext(request))
