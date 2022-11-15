from django import forms
from .models import Expedient, Document, TypeDocument


class ExpedientForm(forms.ModelForm):
    
    class Meta:
        model = Expedient
        fields = '__all__'
        exclude = ['user_create', 'date_create', 'date_register', 'state', 'n_person_id', 'entity', 'expedient_id', 'number', 'sgd_expedient', 'sgd_date_register']
        widgets = {
            'type_person': forms.Select(attrs={
                'class': 'form-control show-tick z-index',
                'v-model': 'form.type_person',
                'v-on:change': 'changeTypePerson'
            }),
            'j_ruc': forms.TextInput(attrs={
                'class': 'form-control',
                'v-model': 'form.j_ruc',
                'v-on:keypress': 'isNumber'
            }),
            'j_business_name': forms.TextInput(attrs={
                'class': 'form-control',
                'v-model': 'form.j_business_name'
            }),
            'j_address': forms.TextInput(attrs={
                'class': 'form-control',
                'v-model': 'form.j_address'
            }),
            'n_dni': forms.TextInput(attrs={
                'class': 'form-control',
                'v-model': 'form.n_dni',
                'v-on:keyup': 'changeDni',
                'v-on:keypress': 'isNumber'
            }),
            'n_last_name0': forms.TextInput(attrs={
                'class': 'form-control',
                'v-model': 'form.n_last_name0',
                'readonly': True
            }),
            'n_last_name1': forms.TextInput(attrs={
                'class': 'form-control',
                'v-model': 'form.n_last_name1',
                'readonly': True
            }),
            'n_first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'v-model': 'form.n_first_name',
                'readonly': True
            }),
            'n_cellphone': forms.TextInput(attrs={
                'class': 'form-control',
                'v-model': 'form.n_cellphone',
                'v-on:keypress': 'isNumber'
            }),
            'n_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'v-model': 'form.n_email'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(ExpedientForm, self).__init__(*args, **kwargs)
        self.initial['type_person'] = 'N'


class DocumentForm(forms.ModelForm):
    
    class Meta:
        model = Document
        fields = '__all__'
        exclude = ['user_create', 'date_create', 'expedient', 'type_documentation', 'document_name', 'document_id']
        widgets = {
            'type_document': forms.Select(attrs={
                'class': 'form-control show-tick z-index',
                'v-model': 'form_document.type_document'
            }),
            'number': forms.TextInput(attrs={
                'class': 'form-control',
                'v-model': 'form_document.number',
                'v-on:keyup': 'isMayus'
            }),
            'folio': forms.TextInput(attrs={
                'class': 'form-control',
                'v-model': 'form_document.folio',
                'v-on:keypress': 'isNumber'
            }),
            'attached_name': forms.HiddenInput(attrs={
                'class': 'form-control',
                'v-model': 'form_document.attached_name'
            }),
            'attached_route': forms.HiddenInput(attrs={
                'class': 'form-control',
                'v-model': 'form_document.attached_route'
            }),
            'subject': forms.Textarea(attrs={
                'class': 'form-control',
                'v-model': 'form_document.subject',
                'rows': '4'
            }),
            'observation': forms.Textarea(attrs={
                'class': 'form-control',
                'v-model': 'form_document.observation',
                'rows': '4'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.fields['type_document'].queryset = TypeDocument.objects.filter(state='A')
