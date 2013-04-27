from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from alert.forms import PhoneForm
from twilio.rest import TwilioRestClient
from random import randint

#
# View to confirm a phone number by verfiying user-supplied code matches
# the code sent.
#
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


#
# View to text a user an activation code.
#
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

