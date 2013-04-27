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
import requests, json, hmac, registration, alert

@login_required
def phone_confirmation(request, context):
    try:
        supplied_id = int(request.POST['confirmation'])
    except ValueError:
        context['confirmation_failed'] = True
        return render_to_response("home.html", context, 
                                  context_instance=RequestContext(request))
    if supplied_id == request.user.phone_activation_code:
        request.user.phone_is_active = True
        request.user.save()
        context['successfully_confirmed_phone'] = True
        return render_to_response("home.html", context, 
                                  context_instance=RequestContext(request))
    else:
        context['confirmation_failed'] = True
    return render_to_response("home.html", context, 
                              context_instance=RequestContext(request))

@login_required
def phone(request, context):
    form = PhoneForm(request.POST)
    context['phone_form'] = form
    if form.is_valid():
        id = randint(10000000, 99999999) #8 digit numbers w/o leading 0
        user = request.user
        user.phone_activation_code = id
        user.phone_is_active = False
        user.phone = request.POST["phone"]
        user.save()
        client = TwilioRestClient(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.sms.messages.create(body=settings.CONFIRMATION_PROMPT 
                                             + str(id) + settings.CONFIRMATION_NEXT,
                                             to=request.POST["phone"],
                                             from_=settings.TWILIO_NUMBER)
        context['confirm_phone'] = True
        return render_to_response("home.html", context, context_instance=RequestContext(request))
    else:
        return render_to_response("home.html", context, context_instance=RequestContext(request))

    context['form'] = PhoneForm()
    return render_to_response("phone.html", context, context_instance=RequestContext(request))

def home(request):
    context = {}
    form = AlertForm()
    registration_form = RegistrationForm()
    phone_form = PhoneForm()

    context['form'] = form
    context['registration_form'] = registration_form
    context['phone_form'] = phone_form
    context['myAlerts'], status  = getAlerts(request.user)

    if request.POST:
        if "registration_form" in request.POST:

            return registration.views.register(request, "registration.backends.default.DefaultBackend", template_name="home.html", form_class=alert.forms.RegistrationForm, extra_context=context)
        elif "phone_form" in request.POST:
            return phone(request, context)
        elif "confirm_phone" in request.POST:
            return phone_confirmation(request, context)
        else:
            form = AlertForm(request.POST, request=request)
            if form.is_valid():
                status = createAlert(request.user, request.POST['delivery_type'],
                                     request.POST['alert_when'], 
                                     request.POST['threshold'])
                if status == requests.codes.ok:
                    context['alert_succeeded'] = True
                else: context['alert_failed'] = True

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

def register(request, context):
    form = RegistrationForm(request.POST)
    context['registration_form'] = form
    if form.is_valid():
        m = AUser.objects
        m.create_user(request.POST["email"], 
                      request.POST["password"], 
                      is_active=False)
        user = authenticate(username=request.POST["email"], 
                            password=request.POST["password"])
        login(request, user)
        return render_to_response("registration/registration_complete.html", context, context_instance=RequestContext(request))
    else:
        context['registration_form'] = form
        return render_to_response("home.html", context, context_instance=RequestContext(request))
