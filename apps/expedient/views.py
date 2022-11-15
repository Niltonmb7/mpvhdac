from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.views import View
from django.db.models import Max, Count
from django.db.models.functions import TruncMonth
from django.contrib.auth import get_user_model
from django.core import serializers
from django.contrib.auth.decorators import login_required
from urllib.request import urlopen
from datetime import datetime

from .forms import ExpedientForm, DocumentForm
from .models import Expedient, Entity, TypeDocument, Document, Adjunct
from apps.profiles.models import Person

# Clients
from apps.clients.views import sendMail, sendMsg
from django.conf import settings
from shutil import copyfile

import json

User = get_user_model()


class registerExpedient(TemplateView):
    template_name = 'expedient/register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ExpedientForm
        context['form_document'] = DocumentForm
        context['quantity_adjunt'] = settings.QUANTITY_ADJUNT
        return context
    
    def render_to_response(self, context, **response_kwargs):
        DataUser = User.objects.get(username=self.request.user)
        if DataUser:
            if not DataUser.docid.mail or not DataUser.docid.cellphone:
                return redirect(reverse('dashboard:profile'))
        return super(registerExpedient, self).render_to_response(context, **response_kwargs)


class apiExpedient(View):
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = ExpedientForm(request.POST)
            form_document = DocumentForm(request.POST)
            
            if request.FILES:
                if 'file_' in request.FILES:
                    path = settings.TMP_DIR_DOCS_ATTACHED + str(request.FILES['file_'])

                    with open(path, 'wb') as f:
                        f.write(request.FILES['file_'].read())
                        f.close()
                    
                    data_response = json.dumps({
                        'file_url': path,
                        'filename': str(request.FILES['file_'])
                    })
                
                    return HttpResponse(data_response, content_type='application/json')
                else:
                    return HttpResponse(status=500)
            else:
                if form.is_valid() and form_document.is_valid():
                    ent = Entity.objects.get(pk='1')

                    # year of expedient
                    date_now = datetime.now()
                    max_expedient = Expedient.objects.filter(expedient_id__startswith=str(date_now.year))

                    if max_expedient:
                        max_expedient = max_expedient.latest('number')
                    
                    id_expedient = ''
                    number = 0
                    if(max_expedient):
                        n = str(int(max_expedient.expedient_id[5:11]) + 1)
                        number = int(n)
                        id_expedient = str(date_now.year) + '-' + n.zfill(6)
                    else:
                        n = '1'
                        number = int(n)
                        id_expedient = str(date_now.year) + '-' + n.zfill(6)

                    # create expedient
                    data_create = form.save(commit=False)
                    data_create.expedient_id = id_expedient
                    data_create.entity = ent
                    data_create.number = number
                    data_create.user_create = str(request.user)
                    data_create.state = 'EMP'
                    data_create.save()

                    id_document = id_expedient + '-001'
                    # create document
                    data_create_document = form_document.save(commit=False)
                    data_create_document.document_id = id_document
                    data_create_document.expedient = data_create
                    data_create_document.document_name = str(data_create_document.type_document.name) + ' ' + str(data_create_document.number)
                    data_create_document.user_create = str(request.user)
                    data_create_document.type_documentation = 'P'

                    name_file_principal = id_document + '.pdf'
                    copyfile(data_create_document.attached_route, settings.DIR_DOCS_ATTACHED + name_file_principal)
                    data_create_document.attached_name = name_file_principal
                    data_create_document.attached_route = settings.ROUTE_DOCS_ATTACHED + name_file_principal
                    data_create_document.save()

                    # create attached anexo
                    file_anexo = json.loads(request.POST['file_anexo'])
                    if file_anexo:
                        i = 1
                        for anexo in file_anexo:
                            nn = str(i)
                            name_file_anexo = id_document + '-' + nn.zfill(3) + '.pdf'
                            copyfile(anexo['file_url'], settings.DIR_DOCS_ATTACHED + name_file_anexo)
                            f_anexo = Adjunct()
                            f_anexo.adjunct_id = id_document + '-' + nn.zfill(3)
                            f_anexo.name = name_file_anexo
                            f_anexo.route = settings.ROUTE_DOCS_ATTACHED + name_file_anexo
                            f_anexo.type_attached = 'A'
                            f_anexo.user_create = str(request.user)
                            f_anexo.document = data_create_document
                            f_anexo.save()
                            i = i + 1
                    

                    DataPerson = Person.objects.get(docid = request.user)
                    mail = DataPerson.mail
                    name = DataPerson.first_name.upper()
                    number = DataPerson.cellphone

                    subject = 'Confirmación de registro de expediente MPV - HRDAC - PASCO'
                    message = 'Hola! {}, se registró el expediente en el sistema de mesa de partes virtual con nombre de documento {}'.format(name,data_create_document.document_name)
                    sendMail(mail, subject, message)

                    message_text = 'Hola+se+registro+su+expediente+en+la+Mesa+de+Partes+Virtual+HRDAC+PASCO+con+nombre+de+documento+' + str(data_create_document.document_name)
                    sendMsg(number, message_text)
                    
                    format_data = serializers.serialize('json', [data_create])
                    return HttpResponse(format_data, content_type='application/json')
                else:
                    return HttpResponse(status=500)
        else:
            return HttpResponse(status=500)


class listExpedient(TemplateView):
    template_name = 'expedient/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_document'] = DocumentForm
        context['quantity_adjunt'] = settings.QUANTITY_ADJUNT
        return context
    
    def render_to_response(self, context, **response_kwargs):
        DataUser = User.objects.get(username=self.request.user)
        if DataUser:
            if not DataUser.docid.mail or not DataUser.docid.cellphone:
                return redirect(reverse('dashboard:profile'))
        return super(listExpedient, self).render_to_response(context, **response_kwargs)


class apiListExpedient(View):

    def get(self, request, *args, **kwargs):
        if request.GET and request.GET['id']:
            attacheds = Adjunct.objects.filter(document=request.GET['id']).order_by('adjunct_id')

            data_attached = serializers.serialize('json', attacheds, indent=2, 
                        use_natural_foreign_keys=True, use_natural_primary_keys=True)
            return HttpResponse(data_attached, content_type='application/json')
        else:
            now = datetime.now()

            if self.request.session['rol_active']['pk'] == 8:
                documents = Document.objects.filter(expedient__date_register__month=now.month, type_documentation='P', expedient__user_create=request.user.username)\
                                                    .select_related('expedient').order_by('-expedient__date_register')
            elif self.request.session['rol_active']['pk'] == 3:
                documents = Document.objects.filter(expedient__date_register__month=now.month, type_documentation='P')\
                                                    .select_related('expedient').order_by('-expedient__date_register')
            expedients = serializers.serialize('json', documents, indent=2, 
                        use_natural_foreign_keys=True, use_natural_primary_keys=True)
            return HttpResponse(expedients, content_type='application/json')
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            if request.FILES:
                if 'file_' in request.FILES:
                    path = settings.TMP_DIR_DOCS_ATTACHED + str(request.FILES['file_'])

                    with open(path, 'wb') as f:
                        f.write(request.FILES['file_'].read())
                        f.close()
                    
                    data_response = json.dumps({
                        'file_url': path,
                        'filename': str(request.FILES['file_'])
                    })
                
                    return HttpResponse(data_response, content_type='application/json')
                else:
                    return HttpResponse(status=500)
            else:
                if request.POST['type_post'] == 'MP':
                    if request.POST['state'] == 'OBS':
                        obj_format = get_object_or_404(Document, pk=request.POST['document_id'])
                        obj_expedient = get_object_or_404(Expedient, pk=request.POST['expedient_id'])
                        
                        if obj_format and obj_expedient:
                            obj_format.state = request.POST['state']
                            obj_format.observation = request.POST['observation']
                            obj_format.user_update = request.user.username
                            obj_format.save()

                            obj_expedient.state = request.POST['state']
                            obj_expedient.user_update = request.user.username
                            obj_expedient.save()

                            documents = Document.objects.filter(expedient__expedient_id=request.POST['expedient_id'], type_documentation='P').select_related('expedient')
                            expedient = serializers.serialize('json', documents, indent=2, 
                                        use_natural_foreign_keys=True, use_natural_primary_keys=True)
                            return HttpResponse(expedient, content_type='application/json')

                    elif request.POST['state'] == 'SGD':
                        obj_format = get_object_or_404(Expedient, pk=request.POST['expedient_id'])
                        
                        if obj_format:
                            obj_format.state = request.POST['state']
                            obj_format.sgd_expedient = request.POST['sgd_expedient']
                            obj_format.sgd_date_register = request.POST['sgd_date_register']
                            obj_format.user_update = request.user.username
                            obj_format.save()

                            documents = Document.objects.filter(expedient__expedient_id=request.POST['expedient_id'], type_documentation='P').select_related('expedient')
                            expedient = serializers.serialize('json', documents, indent=2, 
                                        use_natural_foreign_keys=True, use_natural_primary_keys=True)
                            return HttpResponse(expedient, content_type='application/json')
                        else:
                            return HttpResponse(status=500)
                    else:
                            return HttpResponse(status=500)
                elif request.POST['type_post'] == 'AD':
                    form_document = DocumentForm(request.POST)
                    obj_expedient = get_object_or_404(Expedient, pk=request.POST['expedient_id'])

                    if form_document.is_valid():
                        documents = Document.objects.filter(expedient__expedient_id=request.POST['expedient_id'])
                        documents.update(type_documentation='S')

                        if documents:
                            documents = documents.latest('date_create')
                        
                        id_document = ''
                        if(documents):
                            n = str(int(documents.document_id[12:]) + 1)
                            id_document = str(request.POST['expedient_id']) + '-' + n.zfill(3)
                        
                        # create document
                        data_create_document = form_document.save(commit=False)
                        data_create_document.document_id = id_document
                        data_create_document.expedient_id = request.POST['expedient_id']
                        data_create_document.document_name = str(data_create_document.type_document.name) + ' ' + str(data_create_document.number)
                        data_create_document.user_create = request.user.username
                        data_create_document.type_documentation = 'P'

                        name_file_principal = id_document + '.pdf'
                        copyfile(data_create_document.attached_route, settings.DIR_DOCS_ATTACHED + name_file_principal)
                        data_create_document.attached_name = name_file_principal
                        data_create_document.attached_route = settings.ROUTE_DOCS_ATTACHED + name_file_principal
                        data_create_document.save()

                        # create attached anexo
                        file_anexo = json.loads(request.POST['file_anexo'])
                        if file_anexo:
                            i = 1
                            for anexo in file_anexo:
                                nn = str(i)
                                name_file_anexo = id_document + '-' + nn.zfill(3) + '.pdf'
                                copyfile(anexo['file_url'], settings.DIR_DOCS_ATTACHED + name_file_anexo)
                                f_anexo = Adjunct()
                                f_anexo.adjunct_id = id_document + '-' + nn.zfill(3)
                                f_anexo.name = name_file_anexo
                                f_anexo.route = settings.ROUTE_DOCS_ATTACHED + name_file_anexo
                                f_anexo.type_attached = 'A'
                                f_anexo.user_create = request.user.username
                                f_anexo.document = data_create_document
                                f_anexo.save()
                                i = i + 1
                        
                        obj_expedient.state = 'EMP'
                        obj_expedient.user_update = request.user.username
                        obj_expedient.save()

                        DataPerson = Person.objects.get(docid = request.user)
                        mail = DataPerson.mail
                        name = DataPerson.first_name.upper()
                        number = DataPerson.cellphone

                        subject = 'Confirmación de registro de documento MPV - HRDAC - PASCO'
                        message = 'Hola! {}, se registró el documento en el sistema de mesa de partes virtual con nombre de documento {}'.format(name,data_create_document.document_name)
                        sendMail(mail, subject, message)

                        message_text = 'Hola+se+registro+su+documento+en+la+Mesa+de+Partes+Virtual+HRDAC+PASCO+con+número+de+registro+' + str(data_create_document.document_name)
                        sendMsg(number, message_text)
                        
                        documents_ = Document.objects.filter(expedient__expedient_id=request.POST['expedient_id'], type_documentation='P').select_related('expedient')
                        expedient = serializers.serialize('json', documents_, indent=2, 
                                    use_natural_foreign_keys=True, use_natural_primary_keys=True)
                        return HttpResponse(expedient, content_type='application/json')
                else:
                    return HttpResponse(status=500)
        else:
            return HttpResponse(status=500)


class reportExpedient(TemplateView):
    template_name = 'expedient/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def render_to_response(self, context, **response_kwargs):
        DataUser = User.objects.get(username=self.request.user)
        if DataUser:
            if not DataUser.docid.mail or not DataUser.docid.cellphone:
                return redirect(reverse('dashboard:profile'))
        return super(reportExpedient, self).render_to_response(context, **response_kwargs)

@login_required()
def getDataReport(request):
    if request.method == 'POST':
        date_now = datetime.now()
        total_emp = Expedient.objects.filter(state='EMP', date_register__year=date_now.year).annotate(month=TruncMonth('date_register')).values('month').annotate(total=Count('expedient_id'))
        total_obs = Expedient.objects.filter(state='OBS', date_register__year=date_now.year).annotate(month=TruncMonth('date_register')).values('month').annotate(total=Count('expedient_id'))
        total_sgd = Expedient.objects.filter(state='SGD', date_register__year=date_now.year).annotate(month=TruncMonth('date_register')).values('month').annotate(total=Count('expedient_id'))

        if request.POST['date_begin'] and request.POST['date_end']:
            total = len(Expedient.objects.filter(date_register__range=[request.POST['date_begin'], request.POST['date_end']], state='SGD'))

            data_state = Expedient.objects.filter(date_register__range=[request.POST['date_begin'], request.POST['date_end']])\
                        .values('state').annotate(cant=Count('state'))

            data_type_doc = Document.objects.filter(expedient__date_register__range=[request.POST['date_begin'], request.POST['date_end']],
                            type_documentation='P', expedient__state='SGD').values('type_document').annotate(cant=Count('type_document'))
            
            data_type_person = Expedient.objects.filter(date_register__range=[request.POST['date_begin'], request.POST['date_end']], state='SGD')\
                        .values('type_person').annotate(cant=Count('type_person'))
        else:
            if request.POST['date_begin']:
                total = len(Expedient.objects.filter(date_register__gte=request.POST['date_begin'], state='SGD'))

                data_state = Expedient.objects.filter(date_register__gte=request.POST['date_begin'])\
                            .values('state').annotate(cant=Count('state'))
                
                data_type_doc = Document.objects.filter(expedient__date_register__gte=request.POST['date_begin'],
                                type_documentation='P', expedient__state='SGD').values('type_document').annotate(cant=Count('type_document'))
                
                data_type_person = Expedient.objects.filter(date_register__gte=request.POST['date_begin'], state='SGD')\
                                    .values('type_person').annotate(cant=Count('type_person'))
            elif request.POST['date_end']:
                total = len(Expedient.objects.filter(date_register__lte=request.POST['date_end'], state='SGD'))

                data_state = Expedient.objects.filter(date_register__lte=request.POST['date_end'])\
                            .values('state').annotate(cant=Count('state'))
                
                data_type_doc = Document.objects.filter(expedient__date_register__lte=request.POST['date_end'],
                                type_documentation='P', expedient__state='SGD').values('type_document').annotate(cant=Count('type_document'))
                
                data_type_person = Expedient.objects.filter(date_register__lte=request.POST['date_end'], state='SGD')\
                                    .values('type_person').annotate(cant=Count('type_person'))
            else:
                total = len(Expedient.objects.filter(state='SGD'))
                
                data_state = Expedient.objects.all().values('state').annotate(cant=Count('state'))
                
                data_type_doc = Document.objects.filter(type_documentation='P', expedient__state='SGD')\
                                .values('type_document').annotate(cant=Count('type_document'))
                
                data_type_person = Expedient.objects.filter(state='SGD')\
                                    .values('type_person').annotate(cant=Count('type_person'))
        
        data_return = {}

        if data_state:
            dict_state = [sta for sta in data_state]
            data_return['data_state'] = dict_state
        else:
            data_return['data_state'] = []

        if data_type_doc:
            tmp_data = []
            for typ in data_type_doc:
                td_data = TypeDocument.objects.get(pk=typ['type_document'])
                tmp_data.append({'type_document': td_data.name, 'cant': typ['cant'], 'percent': round((int(typ['cant']) * 100) / int(total), 1)})
            data_return['data_type_document'] = tmp_data
        else:
            data_return['data_type_document'] = []
        
        if data_type_person:
            tmp_datas = []
            for typ in data_type_person:
                tmp_datas.append({'type_person': 'Natural' if typ['type_person'] == 'N' else 'Jurídica', 'cant': typ['cant'], 'percent': round((int(typ['cant']) * 100) / int(total), 1)})
            data_return['data_type_person'] = tmp_datas
        else:
            data_return['data_type_person'] = []

        months = [1 ,2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        
        if total_emp:
            tmp_emp = []
            for emp in total_emp:
                for i in months:
                    tmp_emp.append({ 'month': i, 'total': emp['total'] }) if i == emp['month'].month else tmp_emp.append({ 'month': i, 'total': 0 })
        else:
            tmp_emp = [{ 'month': i, 'total': 0 } for i in months]
        
        if total_obs:
            tmp_obs = []
            for obs in total_obs:
                for i in months:
                    tmp_obs.append({ 'month': i, 'total': obs['total'] }) if i == obs['month'].month else tmp_obs.append({ 'month': i, 'total': 0 })
        else:
            tmp_obs = [{ 'month': i, 'total': 0 } for i in months]
        
        if total_sgd:
            tmp_sgd = []
            for sgd in total_sgd:
                for i in months:
                    tmp_sgd.append({ 'month': i, 'total': sgd['total'] }) if i == sgd['month'].month else tmp_sgd.append({ 'month': i, 'total': 0 })
        else:
            tmp_sgd = [{ 'month': i, 'total': 0 } for i in months]

        data_return['data_long_emp'] = tmp_emp
        data_return['data_long_obs'] = tmp_obs
        data_return['data_long_sgd'] = tmp_sgd

        return HttpResponse(json.dumps(data_return), content_type='application/json')

@login_required()
def filterDate(request):
    if request.method == 'POST':
        if request.session['rol_active']['pk'] == 8:
            if request.POST['date_begin'] and request.POST['date_end']:
                documents = Document.objects.filter(expedient__date_register__range=[request.POST['date_begin'], request.POST['date_end']], type_documentation='P', expedient__user_create=request.user.username).select_related('expedient').order_by('-expedient__date_register')
                expedients = serializers.serialize('json', documents, indent=2, 
                            use_natural_foreign_keys=True, use_natural_primary_keys=True)
                return HttpResponse(expedients, content_type='application/json')
            else:
                if request.POST['date_begin']:
                    documents = Document.objects.filter(expedient__date_register__gte=request.POST['date_begin'], type_documentation='P', expedient__user_create=request.user.username).select_related('expedient').order_by('-expedient__date_register')
                elif request.POST['date_end']:
                    documents = Document.objects.filter(expedient__date_register__lte=request.POST['date_end'], type_documentation='P', expedient__user_create=request.user.username).select_related('expedient').order_by('-expedient__date_register')
                else:
                    documents = Document.objects.filter(type_documentation='P', expedient__user_create=request.user.username).select_related('expedient').order_by('-expedient__date_register')
                    
                expedients = serializers.serialize('json', documents, indent=2, 
                            use_natural_foreign_keys=True, use_natural_primary_keys=True)
                return HttpResponse(expedients, content_type='application/json')
        elif request.session['rol_active']['pk'] == 3:
            if request.POST['date_begin'] and request.POST['date_end']:
                documents = Document.objects.filter(expedient__date_register__range=[request.POST['date_begin'], request.POST['date_end']], type_documentation='P').select_related('expedient').order_by('-expedient__date_register')
                expedients = serializers.serialize('json', documents, indent=2, 
                            use_natural_foreign_keys=True, use_natural_primary_keys=True)
                return HttpResponse(expedients, content_type='application/json')
            else:
                if request.POST['date_begin']:
                    documents = Document.objects.filter(expedient__date_register__gte=request.POST['date_begin'], type_documentation='P').select_related('expedient').order_by('-expedient__date_register')
                elif request.POST['date_end']:
                    documents = Document.objects.filter(expedient__date_register__lte=request.POST['date_end'], type_documentation='P').select_related('expedient').order_by('-expedient__date_register')
                else:
                    documents = Document.objects.filter(type_documentation='P').select_related('expedient').order_by('-expedient__date_register')
                    
                expedients = serializers.serialize('json', documents, indent=2, 
                            use_natural_foreign_keys=True, use_natural_primary_keys=True)
                return HttpResponse(expedients, content_type='application/json')
        else:
            return HttpResponse(status=500)
    else:
        return HttpResponse(status=500)

@login_required()
def getCorrect(request):
    if request.method == 'POST':
        document_correct = Document.objects.filter(expedient=request.POST['expedient_id'], type_documentation='S').order_by('-document_id')

        data_correct = serializers.serialize('json', document_correct, indent=2, 
                    use_natural_foreign_keys=True, use_natural_primary_keys=True)
        return HttpResponse(data_correct, content_type='application/json')
    else:
        return HttpResponse(status=500)

@login_required()
def sendMailSGD(request):
    if request.method == 'POST':
        obj_expedient = get_object_or_404(Expedient, pk=request.POST['expedient_id'])

        if obj_expedient:
            DataPerson = Person.objects.get(docid = obj_expedient.user_create)
            mail = DataPerson.mail
            name = DataPerson.first_name.upper()
            number = DataPerson.cellphone

            subject = 'Mensaje de Confirmación SGD - HRDAC - PASCO'
            message = 'Hola! {}, se registró su expediente {}, en el Sistema de Gestión Documental con número de registro {} y fecha de registro {}.'\
                        .format(name, request.POST['document_name'], request.POST['sgd_expedient'], request.POST['sgd_date_register'])
            sendMail(mail, subject, message)

            message_text = 'Hola+se+registro+su+expediente+en+el+Sistema+de+Gestión+Documental+HRDAC+PASCO+con+numero+de+registro+' + str(request.POST['sgd_expedient'])
            sendMsg(number, message_text)

            obj_expedient.notified = True
            obj_expedient.save()

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=200)
    else:
        return HttpResponse(status=500)

@login_required()
def reniec(request):
    data = json.loads(request.body)
    if (data['type'] == 'search'):
        dni = data['dni']
    else:
        dni = request.user

    DataPerson = Person.objects.filter(docid = dni)

    if DataPerson:
        data_response = json.dumps(
            {
                'dni': DataPerson[0].docid,
                'name': DataPerson[0].first_name.upper(),
                'first_name': DataPerson[0].last_name0.upper(),
                'last_name': DataPerson[0].last_name1.upper(),
                'cellphone': DataPerson[0].cellphone,
                'mail': DataPerson[0].mail
            })
        return HttpResponse(data_response, content_type='application/json')
    else:
        url = "https://dni.optimizeperu.com/api/persons/" + dni + "?format=json"
        response = urlopen(url)
        
        if response.status == 200:
            return HttpResponse(json.dumps(json.loads(response.read())), content_type='application/json')
        else:
            return HttpResponse(status=500)


def handler404(request, exception):
    if not request.user.is_authenticated:
        return redirect(reverse('expedient:error404'))
    else:
        return redirect(reverse('dashboard:home'))

def handler500(request, exception):
    if not request.user.is_authenticated:
        return redirect(reverse('expedient:error500'))
    else:
        return redirect(reverse('dashboard:home'))


class error404(TemplateView):
    template_name = '404.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class error500(TemplateView):
    template_name = '500.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context