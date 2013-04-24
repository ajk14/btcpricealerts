from django.conf import settings
from django.db import models
from django import forms
from django.contrib.localflavor.us.forms import USPhoneNumberField
from alert.models import AUser

class PhoneForm(forms.Form):
    phone = USPhoneNumberField()

class AlertForm(forms.Form):
    delivery_type = forms.ChoiceField(choices=settings.DELIVERY_CHOICES, widget=forms.RadioSelect())
    alert_when = forms.ChoiceField(choices=settings.ALERT_CHOICES, widget=forms.RadioSelect())
    threshold = forms.FloatField()

class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = AUser
        fields = ("email", "password", "confirm_password")
        widgets = {
            'password': forms.PasswordInput(),
        }


    def clean(self):
        super(RegistrationForm, self).clean()
        if self.cleaned_data['confirm_password']!=self.cleaned_data['password']:
            raise ValidationError("Passwords don't match")
        return self.cleaned_data
