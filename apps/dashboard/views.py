from django.shortcuts import render, get_object_or_404, redirect
from django.core import serializers

from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator

from django.db.models import Max, Count
from django.db.models.functions import TruncMonth

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView, FormView, View

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import JsonResponse, HttpResponse

from urllib.request import urlopen
from datetime import datetime

# Settings
from django.conf import settings

#form
from .forms import LoginForm
from apps.profiles.forms import PersonForm

#Models
from django.contrib.auth.models import Group
from apps.default.models import Entity
from apps.profiles.models import Person
from apps.acl.models import Permissionmenu, Menu, Modules, ModuleGroup
from apps.expedient.models import Expedient, Document, TypeDocument

# Clients
from apps.clients.views import sendMail, sendMsg

import os
import random
import json

from django.urls import resolve

User = get_user_model()

class TUCILogin(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('dashboard:home')

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)

    #verifica la petición
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(TUCILogin, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        login(self.request, user)
        
        try:
            ObjPerson = Person.objects.get(pk=user.docid.id)

            self.request.session['system'] = {'full_name': ObjPerson.last_name0+' '+ObjPerson.last_name1+', '+ObjPerson.first_name.title(),
                                        'eid': ObjPerson.eid.eid,
                                         }
            
        except:
            print("Hay un error en los valores de entrada")
        
        return super(TUCILogin, self).form_valid(form)


class TUCISignup(TemplateView):
    template_name = 'signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class Home(TemplateView):
    template_name = 'base.html'
    def active_rol(self, request, rol_active):
        if request.user.is_authenticated:
            self.request.session['rol_active'] = rol_active

        permissions_rolactive =Group.objects.get(pk=rol_active['pk']).permissions.all()
            
        self.request.session['menu'] = {}
        permiso_menu=[]
        for permissions in permissions_rolactive:
            ObjpermMenu = Permissionmenu.objects.filter(pk=permissions.pk)
            if(ObjpermMenu):
                permiso_menu.append({'name': permissions.name,
                                                          'app': permissions.content_type.app_label,
                                                          'cod_name': permissions.codename,
                                                          'link': permissions.content_type.app_label + ':' + permissions.codename,
                                                          'orden': ObjpermMenu[0].order,
                                                          'menu_id': ObjpermMenu[0].menu.id,
                                                          })
        permiso_menu = sorted(permiso_menu, key=lambda x: x['orden'])


        DataMenus = Menu.objects.filter(state='A')
        menu_s=[]
        for menu in DataMenus:
            if list(filter(lambda menug: menug['menu_id'] == menu.pk, permiso_menu)):
                menu_s.append({'id':menu.pk,'name':menu.name,'icon':menu.icon,'orden':menu.order})
        menu_s = sorted(menu_s, key=lambda x: x['orden'])


        y=0
        for menu in menu_s:
            permisos={}
            index = 0
            for per in permiso_menu:
                if(menu['id'] == per['menu_id']):
                    permisos[index]=per
                    index = index + 1
            self.request.session['menu'][y]={'menu':menu['name'],'icon':menu['icon'],'permisos':permisos}
            y=y+1

    def get(self, request, *args, **kwargs):
        DataUser = User.objects.get(username=request.user)
        DataRoles =DataUser.groups.all().order_by('-pk')
        self.request.session['roles'] = {}
        if DataRoles.count()>0:
            index = 0
            for rol in DataRoles:
                self.request.session['roles'][index] = {'pk': rol.pk, 'name':rol.name }
                index = index + 1

            self.active_rol(request, {'pk':DataRoles[0].pk,'name':DataRoles[0].name })  

            return render(request, self.template_name)
        else:
            logout(request)
            return HttpResponseRedirect('/')

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            rol = request.POST['rol_id']
            DataRol = Group.objects.get(pk=rol)
            
            self.active_rol(request, {'pk':DataRol.pk,'name':DataRol.name })            

            return render(request, 'base.html')

class Newuser(View):
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            DataUser = User.objects.filter(username = request.POST['username'])
            if DataUser:
                DataUserRoles =DataUser[0].groups.filter(pk = request.POST['group'])
                if not DataUserRoles:
                    DataGroupUser = Group.objects.get(pk='2')
                    DataUser[0].groups.add(DataGroupUser)

                    DataUser[0].set_password(request.POST['new_pass'])
                    DataUser[0].save()

            else:
                DataPerson = Person.objects.filter(docid = request.POST['username'])
                if DataPerson:
                    NewUser = User()
                    NewUser.username = request.POST['username']
                    NewUser.set_password(request.POST['new_pass'])
                    NewUser.docid = Person.objects.get(docid = request.POST['username'] )                 
                    NewUser.save()

                    GroupUser = Group.objects.get(pk = request.POST['group'])
                    NewUser.groups.add(GroupUser)
                else:

                    NewPerson = Person()
                    #numero de ruc de Hospital
                    NewPerson.eid = Entity.objects.get(pk = '1' )
                    NewPerson.docid = request.POST['username']
                    NewPerson.typedoc = 'D'
                    NewPerson.first_name = request.POST['first_name']
                    NewPerson.last_name0 = request.POST['last_name0']
                    NewPerson.last_name1 = request.POST['last_name1']
                    NewPerson.birthday = '1980-09-09'
                    NewPerson.sex = 'F'
                    NewPerson.civil = 'S'
                    NewPerson.mail = request.POST['mail']
                    NewPerson.cellphone = request.POST['cellphone']
                    NewPerson.save()
                    
                    NewUser = User()
                    NewUser.username = request.POST['username']
                    NewUser.set_password(request.POST['new_pass'])
                    NewUser.docid = Person.objects.get(docid = request.POST['username'] )                 
                    NewUser.save()

                    GroupUser = Group.objects.get(pk = request.POST['group'])
                    NewUser.groups.add(GroupUser)
        

            data = User.objects.filter(username = request.POST['username'])
            format_data = serializers.serialize('json', data, indent=2, use_natural_foreign_keys=True)
            return HttpResponse(format_data, content_type='application/json')


# Functions
def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/')

def reniec_tuci(request):
    username = request.POST['username']
    group = request.POST['group']
    DataUser = User.objects.filter(username = username)
    
    if DataUser:
        DataUserRoles =DataUser[0].groups.filter(pk=group)
        if (DataUserRoles):
            return HttpResponse(json.dumps({'error':False,'status':False,'data':''}), content_type='application/json')
        else:
            DataPerson = Person.objects.get(docid = username)
            return HttpResponse(json.dumps({'error':False, 'status':True, 'data':{'dni':DataPerson.docid,'name':DataPerson.first_name.upper(),'first_name':DataPerson.last_name0.upper(),'last_name':DataPerson.last_name1.upper()}}), content_type='application/json')
    else:
        DataPerson = Person.objects.filter(docid = username)
        if DataPerson:
            return HttpResponse(json.dumps({'error':False, 'status':True, 'data':{'dni':DataPerson[0].docid,'name':DataPerson[0].first_name.upper(),'first_name':DataPerson[0].last_name0.upper(),'last_name':DataPerson[0].last_name1.upper()}}), content_type='application/json')
        else:
            url = "https://dni.optimizeperu.com/api/persons/"+username+"?format=json"
            response = urlopen(url)

            if response.status == 200:
                return HttpResponse(json.dumps({'error':False, 'status':True,'data':json.loads(response.read())}), content_type='application/json')
            else:
                return HttpResponse(json.dumps({'error':True, 'status':True,'data':''}), content_type='application/json')

# Envío de codigo de verificación al email y celular
def validation(request):
    otp = random.randint(10000,99999)
    mail = request.POST['mail']
    name = request.POST['name']
    number = request.POST['cellphone']

    subject = 'Código de Activación HRDAC - PASCO'
    message = 'Hola! {}, el código para registrarse es {}'.format(name,otp)

    sendMail(mail, subject, message)

    message_text = 'Hola+el+codigo+para+registrarse+es+' + str(otp)
    sendMsg(number, message_text)

    msz = ['Su Token a sido enviado a {} @'.format(mail),otp]
    return HttpResponse(msz)

# Login MVP
class MPVLogin(FormView):
    template_name = 'mpv/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('dashboard:index_mpv')

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)

    #verifica la petición
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(MPVLogin, self).dispatch(request, *args, **kwargs)

    # valida el formulario
    def form_valid(self, form):
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        
        # login(self.request, user)
        if user is not None:
            login(self.request, user)
        
        try:
            ObjPerson = Person.objects.get(pk=user.docid.id)
            self.request.session['system'] = {
                'full_name': ObjPerson.last_name0+' '+ObjPerson.last_name1+', '+ObjPerson.first_name.title(),
                'eid': ObjPerson.eid.eid,
            }
        except:
            print("Hay un error en los valores de entrada")
        return super(MPVLogin, self).form_valid(form)

# Sigup MPV
class MPVSignup(TemplateView):
    template_name = 'mpv/signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            DataUser = User.objects.filter(username = request.POST['username'])
            if DataUser:
                DataUserRoles =DataUser[0].groups.filter(pk = request.POST['group'])
                if not DataUserRoles:
                    DataGroupUser = Group.objects.get(pk='8')
                    DataUser[0].groups.add(DataGroupUser)

                    DataUser[0].set_password(request.POST['new_pass'])
                    DataUser[0].save()

            else:
                DataPerson = Person.objects.filter(docid = request.POST['username'])
                if DataPerson:
                    NewUser = User()
                    NewUser.username = request.POST['username']
                    NewUser.set_password(request.POST['new_pass'])
                    NewUser.docid = Person.objects.get(docid = request.POST['username'] )                 
                    NewUser.save()

                    GroupUser = Group.objects.get(pk = request.POST['group'])
                    NewUser.groups.add(GroupUser)
                else:

                    NewPerson = Person()
                    #numero de ruc de Hospital
                    NewPerson.eid = Entity.objects.get(pk = '1')
                    NewPerson.docid = request.POST['username']
                    NewPerson.typedoc = 'D'
                    NewPerson.first_name = request.POST['first_name']
                    NewPerson.last_name0 = request.POST['last_name0']
                    NewPerson.last_name1 = request.POST['last_name1']
                    NewPerson.birthday = '1980-09-09'
                    NewPerson.sex = 'F'
                    NewPerson.civil = 'S'
                    NewPerson.mail = request.POST['mail']
                    NewPerson.cellphone = request.POST['cellphone']
                    NewPerson.save()
                    
                    NewUser = User()
                    NewUser.username = request.POST['username']
                    NewUser.set_password(request.POST['new_pass'])
                    NewUser.docid = Person.objects.get(docid = request.POST['username'] )                 
                    NewUser.save()

                    GroupUser = Group.objects.get(pk = request.POST['group'])
                    NewUser.groups.add(GroupUser)
        

            data = User.objects.filter(username = request.POST['username'])
            format_data = serializers.serialize('json', data, indent=2, use_natural_foreign_keys=True)
            # return HttpResponse(format_data, content_type='application/json')
            return HttpResponseRedirect(reverse('dashboard:login'))


class MPVHome(TemplateView):
    template_name = 'mpv/base.html'

    def active_rol(self, request, rol_active):
        if request.user.is_authenticated:
            self.request.session['rol_active'] = rol_active
        roluser_current = Group.objects.get(pk=rol_active['pk'])
        modules_for_rolactive = ModuleGroup.objects.filter(group=roluser_current.pk, module__parent=None)
        modules_for_rolactive = serializers.serialize('json', modules_for_rolactive, indent=2, use_natural_foreign_keys=True)
        modules_for_rolactive = json.loads(modules_for_rolactive)

        self.request.session['menu'] = {}
        permiso_menu=[]
        for module in modules_for_rolactive:
            ObjpermMenu = Modules.objects.filter(pk=module['fields']['module'][0])

            if(ObjpermMenu):
                permiso_menu.append({'name': module['fields']['module'][1],
                                    'app': module['fields']['module'][2],
                                    'cod_name': module['fields']['module'][3],
                                    'link': str(module['fields']['module'][2]+ ':' + module['fields']['module'][3]),
                                    'orden': module['fields']['module'][4],
                                    'parent_id': module['fields']['module'][0],
                                    })

        permiso_menu = sorted(permiso_menu, key=lambda x: x['orden'])
        current_url = resolve(request.path_info).url_name
        current_acl = Modules.objects.get(route=current_url).name
        current_parent = Modules.objects.get(route=current_url).pk
        self.request.session['current'] = current_acl

        y=0
        for menu in permiso_menu:
            SubMenus = ModuleGroup.objects.filter(module__parent=menu['parent_id'], group=rol_active['pk'])
            SubMenus = serializers.serialize('json', SubMenus, indent=2, use_natural_foreign_keys=True)
            SubMenus = json.loads(SubMenus)
            for sm in SubMenus:
                sm['fields']['name'] = sm['fields']['module'][1]
                sm['fields']['link'] = sm['fields']['module'][2] +':'+sm['fields']['module'][3]
                sm['fields']['order'] = sm['fields']['module'][4]
            SubMenus = sorted(SubMenus, key=lambda x: x['fields']['order'])

            self.request.session['menu'][y]={'menu':menu['name'],'permisos':permiso_menu,'submenus':SubMenus}
            y=y+1

    def get(self, request, *args, **kwargs):
        DataUser = User.objects.get(username=request.user)
        if DataUser:
            if not DataUser.docid.mail or not DataUser.docid.cellphone:
                return redirect(reverse('dashboard:profile'))

        DataRoles =DataUser.groups.all().order_by('-pk')
        self.request.session['roles'] = {}
        
        if DataRoles.count()>0:
            index = 0
            for rol in DataRoles:
                self.request.session['roles'][index] = {'pk': rol.pk, 'name':rol.name }
                index = index + 1
            
            self.active_rol(request, {'pk':DataRoles[0].pk,'name':DataRoles[0].name})  

            if self.request.session['rol_active']['pk'] == 8:
                return redirect(reverse('expedient:register_expedient'))
            else:
                return render(request, self.template_name)
        else:
            logout(request)
            return HttpResponseRedirect('/')

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            rol = request.POST['rol_id']
            DataRol = Group.objects.get(pk=rol)
            
            self.active_rol(request, {'pk':DataRol.pk,'name':DataRol.name })            

            return render(request, 'mpv/base.html')


class MPVRestorePass(TemplateView):
    template_name = 'mpv/restore.html'

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            DataUser = User.objects.filter(username = request.POST['username'])
            print(request.POST)
            if DataUser:
                DataUser[0].set_password(request.POST['new_pass'])
                DataUser[0].save()
                return HttpResponseRedirect(reverse('dashboard:login'))


class MPVDataProfile(TemplateView):
    template_name = 'mpv/profile.html'

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            object_person = get_object_or_404(Person, pk=request.user.docid.id)
            
            if object_person:
                object_person.mail = request.POST['mail']
                object_person.cellphone = request.POST['cellphone']
                object_person.save()
                return HttpResponseRedirect(reverse('dashboard:index_mpv'))
            else:
                return HttpResponse(status=500)


# Funciones MPV
def verify_user(request):
    username = request.POST['username']
    group = ['8', '3']
    DataUser = User.objects.filter(username = username)

    if DataUser:
        DataUserRoles =DataUser[0].groups.filter(pk__in=group)
        
        if (DataUserRoles):
            DataPerson = Person.objects.get(docid = username)
            otp = random.randint(10000,99999)
            mail = DataPerson.mail
            name = DataPerson.first_name.upper()
            number = DataPerson.cellphone

            subject = 'Código de Recuperación HRDAC - PASCO'
            message = 'Hola! {}, el código para recuperar la contraseña es {}'.format(name,otp)
            sendMail(mail, subject, message)

            message_text = 'Hola+el+codigo+para+recuperar+es+' + str(otp)
            sendMsg(number, message_text)

            mail_ = mail.split('@')
            new_mail = mail_[0][:1] + '*****@' + mail_[1]
            
            return HttpResponse(json.dumps({'error':False, 'status':True, 'data':{'cellphone': '******' + number[6:], 'mail': new_mail, 'otp': otp}}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'error':False,'status':False,'data':''}), content_type='application/json')

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

def reniec_mpv(request):
    username = request.POST['username']
    group = request.POST['group']
    DataUser = User.objects.filter(username = username)
    
    if DataUser:
        DataUserRoles =DataUser[0].groups.filter(pk=group)
        if (DataUserRoles):
            return HttpResponse(json.dumps({'error':False,'status':False,'data':''}), content_type='application/json')
        else:
            DataPerson = Person.objects.get(docid = username)
            return HttpResponse(json.dumps({'error':False, 'status':True, 'data':{'dni':DataPerson.docid,'name':DataPerson.first_name.upper(),'first_name':DataPerson.last_name0.upper(),'last_name':DataPerson.last_name1.upper()}}), content_type='application/json')
    else:
        DataPerson = Person.objects.filter(docid = username)
        if DataPerson:
            return HttpResponse(json.dumps({'error':False, 'status':True, 'data':{'dni':DataPerson[0].docid,'name':DataPerson[0].first_name.upper(),'first_name':DataPerson[0].last_name0.upper(),'last_name':DataPerson[0].last_name1.upper()}}), content_type='application/json')
        else:
            url = "https://dni.optimizeperu.com/api/persons/"+username+"?format=json"
            response = urlopen(url)

            if response.status == 200:
                return HttpResponse(json.dumps({'error':False, 'status':True,'data':json.loads(response.read())}), content_type='application/json')
            else:
                return HttpResponse(json.dumps({'error':True, 'status':True,'data':''}), content_type='application/json')