import phonenumbers
from django import template

register = template.Library()

@register.filter(name='phonenumber')
def phonenumber(value, country='US'):
   parsed_number = phonenumbers.parse(value, country)
   return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
