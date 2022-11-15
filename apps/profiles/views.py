#general
from django.views.generic import TemplateView, View
from django.http import HttpResponse
from django.core import serializers
import json
import time

#model
from django.contrib.auth.models import Group
from .models import Person, User

#form
from .forms import PersonForm

class Person(TemplateView):
    template_name = 'users/index.html'
    def get_context_data(self, **kwargs):
        eid=self.request.session['system']['eid']
        context = super().get_context_data(**kwargs)
        context['form'] = PersonForm
        context['eid'] = eid
        return context