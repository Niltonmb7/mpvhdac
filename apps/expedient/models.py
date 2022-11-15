from django.db import models
from datetime import datetime
# Models
from apps.ubigeo.models import Department, Province, District
from apps.default.models import Entity

# Create your models here.
class Expedient(models.Model):
    CHOICES_TYPE_PERSON = (
        ('N', 'Natural'),
        ('J', 'Jurídica'),
    )

    CHOICES_STATE_EXPEDIENT = (
        ('SGD', 'Registrado en SGD'),
        ('OBS', 'Observado'),
        ('EMP', 'Enviado a Mesa de Partes'),
    )

    expedient_id        = models.CharField(max_length=150, primary_key=True)
    entity              = models.ForeignKey(Entity, on_delete=models.PROTECT)
    type_person         = models.CharField(max_length=1, choices=CHOICES_TYPE_PERSON)
    j_ruc               = models.CharField(max_length=11, blank=True, null=True)
    j_business_name     = models.CharField(max_length=250, blank=True, null=True)
    j_address           = models.CharField(max_length=250, blank=True, null=True)
    n_person_id         = models.CharField(max_length=50)
    n_dni               = models.CharField(max_length=8)
    n_last_name0        = models.CharField(max_length=80)
    n_last_name1        = models.CharField(max_length=80)
    n_first_name        = models.CharField(max_length=100)
    n_cellphone         = models.CharField(max_length=9)
    n_email             = models.CharField(max_length=100)
    state               = models.CharField(max_length=3, choices=CHOICES_STATE_EXPEDIENT)
    date_register       = models.DateTimeField(auto_now_add=True)
    sgd_expedient       = models.CharField(max_length=50, blank=True, null=True)
    sgd_date_register   = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    number              = models.IntegerField()
    notified            = models.BooleanField(blank=True, null=True)

    user_create         = models.CharField(max_length=15)
    user_update         = models.CharField(max_length=15, null=True,blank=True)
    date_create         = models.DateTimeField(auto_now_add=True)
    date_update         = models.DateTimeField(auto_now=True, blank=True, null=True)

    def natural_key(self):
        formatedDate = self.date_register.strftime("%Y-%m-%d %H:%M:%S")
        if self.sgd_date_register:
            SGDformatedDate = self.sgd_date_register.strftime("%Y-%m-%d %H:%M:%S")
        else:
            SGDformatedDate = ''
        return { 'expedient_id': self.expedient_id, 'type_person': self.get_type_person_display(), 'j_ruc': self.j_ruc, 
                'j_business_name': self.j_business_name, 'j_address': self.j_address,
                'n_person_id': self.n_person_id, 'n_dni': self.n_dni, 'n_last_name0': self.n_last_name0,
                'n_last_name1': self.n_last_name1, 'n_first_name': self.n_first_name, 
                'n_cellphone': self.n_cellphone, 'n_email': self.n_email, 'state': self.state, 
                'date_register': formatedDate, 'sgd_expedient': self.sgd_expedient, 
                'sgd_date_register': SGDformatedDate, 'notified': self.notified }

    class Meta:
        db_table = u'"mpv\".\"expedient"'


class TypeDocument(models.Model):
    CHOICES_STATE_TYPE = (
        ('A', 'Activo'),
        ('I', 'Inactivo'),
    )

    name                = models.CharField(max_length=50)
    state               = models.CharField(max_length=1, choices=CHOICES_STATE_TYPE)

    def __str__(self):
        return self.name
    
    def natural_key(self):
        return { 'pk': self.pk, 'name': self.name }

    class Meta:
        db_table = u'"mpv\".\"type_document"'


class Document(models.Model):
    CHOICES_TYPE = (
        ('S', 'Subsanar'),
        ('P', 'Principal'),
    )

    document_id         = models.CharField(max_length=200, primary_key=True)
    type_document       = models.ForeignKey(TypeDocument, on_delete=models.PROTECT)
    expedient           = models.ForeignKey(Expedient, on_delete=models.PROTECT, related_name='documents')
    number              = models.CharField(max_length=50)
    folio               = models.CharField(max_length=3)
    document_name       = models.CharField(max_length=80)
    subject             = models.TextField()
    observation         = models.TextField(null=True, blank=True)
    type_documentation  = models.CharField(max_length=1, choices=CHOICES_TYPE)
    attached_name       = models.CharField(max_length=250)
    attached_route      = models.CharField(max_length=250)

    user_create         = models.CharField(max_length=15)
    user_update         = models.CharField(max_length=15, null=True, blank=True)
    date_create         = models.DateTimeField(auto_now_add=True)
    date_update         = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    def natural_key(self):
        formatedDate = self.date_update.strftime("%Y-%m-%d %H:%M:%S")
        print(formatedDate)
        return { 'document_id': self.document_id, 'document_name': self.document_name, 
                'number': self.number, 'folio': self.folio,
                'subject': self.subject, 'observation': self.observation,
                'attached_name': self.attached_name, 'attached_route': self.attached_route,
                'type_documentation': self.type_documentation, 'date_update': formatedDate }
    
    class Meta:
        db_table = u'"mpv\".\"document"'


class Adjunct(models.Model):

    adjunct_id          = models.CharField(max_length=250, primary_key=True)
    document            = models.ForeignKey(Document, on_delete=models.PROTECT)
    name                = models.CharField(max_length=250)
    route               = models.CharField(max_length=250)

    user_create         = models.CharField(max_length=15)
    user_update         = models.CharField(max_length=15, null=True, blank=True)
    date_create         = models.DateTimeField(auto_now_add=True)
    date_update         = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    
    def natural_key(self):
        return { 'adjunct_id': self.adjunct_id, 'name': self.name, 'route': self.route }
    
    class Meta:
        db_table = u'"mpv\".\"adjunct"'