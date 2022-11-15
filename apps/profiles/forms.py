#Django
from django import forms

#Models
from .models import Person

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = '__all__'
        widgets= {
            'eid': forms.TextInput(attrs={
                'class': 'form-control ',
                'v-model': 'form.eid'
            }),
            'typedoc': forms.Select(attrs={
                'class': 'form-control custom-select',
                'v-model': 'form.typedoc'
            }),
            'sex': forms.Select(attrs={
                'class': 'form-control custom-select',
                'v-model': 'form.sex'
            }),
            'civil': forms.Select(attrs={
                'class': 'form-control custom-select',
                'v-model': 'form.civil'
            }),
            'docid' : forms.TextInput(attrs={
                'type': 'number',
                'class' : 'form-control',
                'v-model': 'form.docid'
            }),
            'last_name0': forms.TextInput(attrs={
                'class': 'form-control',
                'v-model': 'form.last_name0'
            }),
            'last_name1': forms.TextInput(attrs={
                'class': 'form-control',
                'v-model': 'form.last_name1'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'v-model': 'form.first_name'
            }),
            'birthday': forms.TextInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'v-model': 'form.birthday',

            }),
            'mail': forms.TextInput(attrs={
                'class': 'form-control ',
                'v-model': 'form.mail'
            }),
          
            'cellphone': forms.TextInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'v-model': 'form.cellphone'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control ',
                'v-model': 'form.address'
            }),
        }


