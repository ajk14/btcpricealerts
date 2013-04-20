from django.db import models
from django.forms import ModelForm, IntegerField, EmailField, CharField, PasswordInput, ValidationError, Form, ChoiceField, RadioSelect
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.localflavor.us.forms import USPhoneNumberField
from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

DELIVERY_CHOICES = [('SMS', 'Text Message'), ('EMAIL', 'E-mail')]
ALERT_CHOICES = [('OVER', 'Above'), ('UNDER', 'Below')]

class AlertForm(Form):
    delivery_type = ChoiceField(choices=DELIVERY_CHOICES, widget=RadioSelect())
    phone = USPhoneNumberField()
    alert_when = ChoiceField(choices=ALERT_CHOICES, widget=RadioSelect())
    threshold = IntegerField()
    
class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
 
        user = self.model(
            email=MyUserManager.normalize_email(email),
        )
 
        user.set_password(password)
        user.save(using=self._db)
        return user
 
    def create_superuser(self, email, password):
        user = self.create_user(email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
 
 
class AUser(AbstractBaseUser):        
    email = models.EmailField(max_length=254, unique=True, db_index=True)
    phone = USPhoneNumberField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    objects = MyUserManager()

    USERNAME_FIELD = 'email'
 
    def get_full_name(self):
        # For this case we return email. Could also be User.first_name User.last_name if you have these fields
        return self.email
 
    def get_short_name(self):
        # For this case we return email. Could also be User.first_name if you have this field
        return self.email
 
    def __unicode__(self):
        return self.email
 
    def has_perm(self, perm, obj=None):
        # Handle whether the user has a specific permission?"
        return True
 
    def has_module_perms(self, app_label):
        # Handle whether the user has permissions to view the app `app_label`?"
        return True
 
    @property
    def is_staff(self):
        # Handle whether the user is a member of staff?"
        return self.is_admin


class RegistrationForm(ModelForm):
    confirm_password = CharField(widget=PasswordInput())
    class Meta:
        model = AUser
        fields = ("email", "password", "confirm_password")
        widgets = {
            'password': PasswordInput(),
        }


    def clean(self):
        super(RegistrationForm, self).clean()
        if self.cleaned_data['confirm_password']!=self.cleaned_data['password']:
            raise ValidationError("Passwords don't match")
        return self.cleaned_data


