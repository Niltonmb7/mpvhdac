from django import forms
from django.contrib.auth.forms import AuthenticationForm

from apps.profiles.models import Person

from django.contrib.auth import get_user_model
User = get_user_model()

class LoginFormSec(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginFormSec,self).__init__(*args,**kwargs)
        self.fields['username'].widget.attrs['class']='form-control'
        self.fields['username'].widget.attrs['placeholder']='Usuario'
        self.fields['password'].widget.attrs['class']='form-control'
        self.fields['password'].widget.attrs['placeholder']='Contraseña'

    def clean(self):
        user_found = User.objects.filter(username = self.cleaned_data['username']).exists()
        if not user_found:
            self.add_error('username', 'Usuario no encontrado.')
        else:
            user = User.objects.get(username = self.cleaned_data['username'])
            if  not user.check_password(self.cleaned_data['password']):
                self.add_error('password', 'Contraseña incorrecta.')

class formPerson(forms.ModelForm):
    class Meta:
        model = Person
        fields  = '__all__'
        widgets = {
            'eid': forms.TextInput(attrs={
                'class': 'form-control',
                'v-model': 'form.eid',
                'id':'id_entity',
            }),
            'docid' : forms.TextInput(attrs={
                'type': 'number',
                'class' : 'form-control ',
                'v-model': 'form.docid'
            }),
            'typedoc': forms.Select(attrs={
                'class': 'form-control show-tick',
                'v-model': 'form.typedoc',
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
                'class': 'form-control',
                'v-model': 'form.birthday',
            }),
            'sex': forms.Select(attrs={
                'class': 'form-control show-tick',
                'v-model': 'form.sex',
            }),
            'civil': forms.Select(attrs={
                'class': 'form-control show-tick',
                'v-model': 'form.civil',
                'data-placeholder':"Seleccione",
                'style':"width:100%"
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
            'r_department': forms.Select(attrs={
                'class': 'form-control show-tick',
                'v-model': 'form.department',
                'data-placeholder':"Escoja",
                'style':"width: 100%;"
            }),
            'r_province': forms.Select(attrs={
                'class': 'form-control show-tick',
                'v-model': 'form.province',
                'data-placeholder':"Escoja",
                'style':"width: 100%;"
            }),
            'r-district': forms.Select(attrs={
                'class': 'form-control show-tick',
                'v-model': 'form.district',
                'data-placeholder':"Escoja",
                'style':"width: 100%;"
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control ',
                'v-model': 'form.address'
            }),
        }