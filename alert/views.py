from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from alert.models import AUser
from alert.forms import RegistrationForm, AlertForm, PhoneForm
from django.contrib.auth import authenticate, login 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from alert.messages import getAlerts, deleteAlert, createAlert
from alert.phone import phone, phone_confirmation
import requests, json, hmac, registration, alert


def home(request):
    context = {}
    alert_form = AlertForm()
    registration_form = RegistrationForm()
    phone_form = PhoneForm()

    context['alert_form'] = alert_form
    context['registration_form'] = registration_form
    context['phone_form'] = phone_form
    context['myAlerts'], status  = getAlerts(request.user)

    if request.POST:
        if "registration_form" in request.POST:
            form_class = RegistrationForm
            backend = "registration.backends.default.DefaultBackend"
            return registration.views.register(request, backend,
                                               template_name="home.html", 
                                               form_class=form_class, 
                                               extra_context=context)
        elif "phone_form" in request.POST:
            return phone(request, context)
        elif "confirm_phone" in request.POST:
            return phone_confirmation(request, context)
        elif "alert_form" in request.POST:
            return alert(request, context)
    return render_to_response("home.html", context, context_instance=RequestContext(request))

def alert(request, context):
    form = AlertForm(request.POST, request=request)
    if form.is_valid():
        status = createAlert(request.user, request.POST['delivery_type'],
                             request.POST['alert_when'],
                             request.POST['threshold'])
        if status == requests.codes.ok:
            context['alert_succeeded'] = True
        else: context['alert_failed'] = True
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
