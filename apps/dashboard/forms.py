from django import forms
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth import get_user_model
User = get_user_model()

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm,self).__init__(*args,**kwargs)
        self.fields['username'].widget.attrs['class']='form-control onlynumber'
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