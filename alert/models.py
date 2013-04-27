from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.mail import send_mail
import datetime

# Class to manage the creation of new users and superusers    
class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, is_active=False):
        if not email:
            raise ValueError(settings.MISSING_EMAIL)
 
        user = self.model(
            email=MyUserManager.normalize_email(email),
        )
        user.date_joined = datetime.datetime.now() 
        user.set_password(password)
        user.save(using=self._db)
        return user
 
    def create_superuser(self, email, password):
        user = self.create_user(email,
            password=password,
        )
        user.is_active = True
        user.is_admin = True
        user.save(using=self._db)
        return user

# Abstraction of User, where identifier is e-mail instead of user ID
class AUser(AbstractBaseUser):        
    email = models.EmailField(max_length=254, unique=True, db_index=True)
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    objects = MyUserManager()
    date_joined = models.DateTimeField()
    phone_is_active = models.BooleanField(default=False)
    phone_activation_code = models.IntegerField(null=True)
    
    # Special field to be compatible with built in Auth model
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
    
    def email_user(self, subject, message, from_address):
        print "Sending Mail"
        send_mail(subject, message, from_address, [self.email], fail_silently=False)
        return True
 
    @property
    def is_staff(self):
        # Handle whether the user is a member of staff?"
        return self.is_admin




