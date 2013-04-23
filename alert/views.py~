from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from alert.models import RegistrationForm, AUser, AlertForm, PhoneForm
from django.contrib.auth import authenticate, login 
from django.contrib import messages
from twilio.rest import TwilioRestClient
from random import randint
import requests
import json
from hashlib import sha1
import hmac
from urllib import urlencode

REQUEST_URL = "http://alerts.btcpricealerts.com:9876"
REQUEST_EXTENSION = "/alerts"
ALERT_SUCCESS = "You've created a new alert!"
ALERT_FAILURE = "Your alert failed to be created. Please try again later."
MAX_OUTSTANDING_ALERTS = 10
MAX_ALERTS_EXCEEDED = "Sorry, you can't create more than " + str(MAX_OUTSTANDING_ALERTS) + " alerts."

CONFIRMATION_PROMPT = "Your BTC Price Alerts verification code is: "
CONFIRMATION_NEXT = ". If you did not request this message, please ignore."

TEST_KEY = "uZBawWwUPRkKAiJXVGk0"
SECRET_KEY = settings.SECRET_KEY_SIGN

def phone_confirmation(request):
    context = {}
    if request.POST:
        supplied_id = int(request.POST['confirmation'])
        print supplied_id
        print request.user.phone_activation_code
        if supplied_id == request.user.phone_activation_code:
            request.user.phone_is_active = True
            request.user.save()
            return render_to_response("phone_confirm_success.html", context, context_instance=RequestContext(request))
        else:
            context['confirmation_failed'] = True
    return render_to_response("phone_confirm.html", context, context_instance=RequestContext(request))

def phone(request):
    context = {}
    if request.POST:
        form = PhoneForm(request.POST)
        context['form'] = form
        if form.is_valid():
            id = randint(10000000, 99999999) #8 digit numbers w/o leading 0
            user = request.user
            user.phone_activation_code = id
            user.phone = request.POST["phone"]
            user.save()
            client = TwilioRestClient(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.sms.messages.create(body=CONFIRMATION_PROMPT + str(id) + CONFIRMATION_NEXT,
                                                 to=request.POST["phone"],
                                                 from_=settings.TWILIO_NUMBER)
            print message.sid
            print "Send text message and add phone number to user model"
            return redirect("/phone/confirmation/")
        else:
            return render_to_response("phone.html", context, context_instance=RequestContext(request))
    else:
        context['form'] = PhoneForm()
    return render_to_response("phone.html", context, context_instance=RequestContext(request))

def createSignature(method, path, body):
    message = method+path+body
    hashed = hmac.new(SECRET_KEY, message, sha1)
    print "--------------"
    print message
    print hashed.hexdigest()
    print "---------------"
    return hashed.hexdigest()

def isValidSignature (method, path, body, signature):
    return createSignature(method,path,body) == signature

def loadAlerts(user):
    payload = {}
    payload["user_id"] = str(user)
    signVal = "?" + urlencode(payload)
    signature = createSignature("GET", REQUEST_EXTENSION, signVal)
    try:
        r = requests.get(REQUEST_URL + REQUEST_EXTENSION, params=payload, headers={'X-Signature':signature})
    except requests.RequestException:
        print "error"
        return None
    #print r.headers
    if "X-Signature" in r.headers:
        if not isValidSignature("GET", REQUEST_EXTENSION, str(r.content), r.headers["X-Signature"]):
            print "Signature failed to validate, ignore"
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
    urlExt = REQUEST_EXTENSION + "/" + id
    url = REQUEST_URL + urlExt
    signature = createSignature("DELETE", urlExt, "")
    try:
        r = requests.delete(url, headers={'X-Signature':signature})
    except requests.RequestException:
        return redirect("/")
    return redirect("/")

def alert(request):
    context = {}
    form = AlertForm(request.POST)
    context['form'] = form
    context['phone_number'] = str(request.user.phone)
    print "PHONE: "+ request.user.phone
    if form.is_valid():
        # Ensure phone number verified if type = SMS
        if request.POST['delivery_type'] == 'SMS':
            if not request.user.phone:
                print "PHONE UNPROVIDED"
                context['phone_unprovided'] = True
                context['myAlerts'] = loadAlerts(request.user)
                return render_to_response("home.html", context, context_instance=RequestContext(request))
        if len(loadAlerts(request.user)) >= MAX_OUTSTANDING_ALERTS:
            messages.error(request, MAX_ALERTS_EXCEEDED)
            return redirect("/")
        if request.POST['delivery_type'] == 'SMS':
            destination = request.user.phone
        else:
            destination = request.user
   
        payload = {'delivery_type' : str(request.POST['delivery_type']), 
                   'destination' : str(destination),
                   'threshold' : str(request.POST['threshold']), 
                   'alert_when' : str(request.POST['alert_when']), 
                   'user_id' : str(request.user)}
   
        signature = createSignature("POST", REQUEST_EXTENSION, json.dumps(payload))
        try:
            r = requests.post(REQUEST_URL + REQUEST_EXTENSION, json.dumps(payload), headers={'X-Signature':signature})
            print r.status_code
            print r.content
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
