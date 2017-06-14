# simple forms to display and edit a domain's data

from django import forms
from django.forms.widgets import Textarea
from .formsextlang import RRField

class DomainForm(forms.Form):
    """
    simple form to edit the rrs for a domain
    """

    domain = forms.CharField(label='Domain name', max_length=64)
    owner = forms.CharField(label='User name', max_length=20, required=False)
    rrs = RRField(label='Records')

class ShortDomainForm(forms.Form):
    """
    simple form to create a new domain
    when editing, view code handles the individual records
    """

    domain = forms.CharField(label='Domain name', max_length=64)
    owner = forms.CharField(label='User name', max_length=20, required=False)

class DomainEditForm(forms.Form):
    """
    simple form to edit a domain
    when editing, view code handles the individual records
    """

    domain = forms.CharField(label='Domain name', max_length=64)
    owner = forms.CharField(label='User name', max_length=20)
