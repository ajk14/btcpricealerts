from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from alert.models import AUser
from alert.forms import RegistrationForm, AlertForm, PhoneForm
from django.contrib.auth import authenticate, login 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from twilio.rest import TwilioRestClient
from random import randint
from hashlib import sha1
from urllib import urlencode
from alert.messages import getAlerts, deleteAlert, createAlert
import requests, json, hmac

@login_required
def phone_confirmation(request):
    context = {}
    if request.POST:
        supplied_id = int(request.POST['confirmation'])
        if supplied_id == request.user.phone_activation_code:
            request.user.phone_is_active = True
            request.user.save()
            return render_to_response("phone_confirm_success.html", context, context_instance=RequestContext(request))
        else:
            context['confirmation_failed'] = True
    return render_to_response("phone_confirm.html", context, context_instance=RequestContext(request))

@login_required
def phone(request):
    context = {}
    if request.POST:
        form = PhoneForm(request.POST)
        context['form'] = form
        if form.is_valid():
            id = randint(10000000, 99999999) #8 digit numbers w/o leading 0
            user = request.user
            user.phone_activation_code = id
            user.phone_is_active = False
            user.phone = request.POST["phone"]
            user.save()
            client = TwilioRestClient(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.sms.messages.create(body=settings.CONFIRMATION_PROMPT + str(id) + settings.CONFIRMATION_NEXT,
                                                 to=request.POST["phone"],
                                                 from_=settings.TWILIO_NUMBER)
            return redirect("/phone/confirmation/")
        else:
            return render_to_response("phone.html", context, context_instance=RequestContext(request))
    else:
        context['form'] = PhoneForm()
    return render_to_response("phone.html", context, context_instance=RequestContext(request))

def home(request):
    context = {}
    form = AlertForm()
    if request.POST:
        form = AlertForm(request.POST, request=request)
        if form.is_valid():
            createAlert(request.user, request.POST['delivery_type'],
                    request.POST['alert_when'], request.POST['threshold'])

    context['form'] = form
    context['myAlerts'], status  = getAlerts(request.user)
    return render_to_response("home.html", context, context_instance=RequestContext(request))

@login_required
def delete(request):
    context = {}
    status = deleteAlert(request.GET['id'], request.user)
    if status == requests.codes.ok:
        return redirect("/")
    return HttpResponse("Unauthorized", status=status)

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
