from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator


from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView, FormView, View
from .forms import LoginFormSec

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.http import JsonResponse, HttpResponse
from django.core import serializers 
import json

from .forms import formPerson

# permisos por rol
import six

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

#Models
from django.contrib.auth.models import Permission, ContentType, Group
from apps.default.models import Entity
from apps.profiles.models import Person
from .models import Permissionmenu, Menu

User = get_user_model()

import requests

#por mejorar
def group_required(*group, login_url=None, raise_exception=False):
    def check_permissions(user):
        if isinstance(group, six.string_types):
            groups = (group, )
        else:
            groups = group
        if user.groups.filter(name__in=groups).exists():
            return True
        if raise_exception:
            raise PermissionDenied
        return False
    return user_passes_test(check_permissions, login_url=login_url)

def handler404(request, exception):
    if not request.user.is_authenticated:
        return redirect(reverse('dashboard:login'))
    else:
        return redirect(reverse('dashboard:home'))

#Login área seguridad
class SecLogin(FormView):
    template_name = 'security/login.html'
    form_class = LoginFormSec
    success_url = reverse_lazy('security:home_security')

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)

    #verifica la petición
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(SecLogin, self).dispatch(request, *args, **kwargs)

    # valida el formulario
    def form_valid(self, form):
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        login(self.request, user)
        
        try:
            ObjPerson = Person.objects.get(pk=user.docid.id)
            self.request.session['system'] = {
                'full_name': ObjPerson.last_name0+' '+ObjPerson.last_name1+', '+ObjPerson.first_name.title(),
                'eid': ObjPerson.eid.eid,
            }
        except:
            print("Hay un error en los valores de entrada")
        return super(SecLogin, self).form_valid(form)

def logoutSec(request):
    logout(request)
    return HttpResponseRedirect('/security')

class HomeSecurity(TemplateView):
    template_name = 'security/index.html'
    def active_rol(self, request, rol_active):
        if request.user.is_authenticated:
            self.request.session['rol_active'] = rol_active

        permissions_rolactive =Group.objects.get(pk=rol_active['pk']).permissions.all()
            
        self.request.session['menu'] = {}
        permiso_menu=[]
        for permissions in permissions_rolactive:
            # DataMenu = Menu.objects.get
            ObjpermMenu = Permissionmenu.objects.filter(pk=permissions.pk)
            if(ObjpermMenu):
                permiso_menu.append({'name': permissions.name,
                                    'app': permissions.content_type.app_label,
                                    'cod_name': permissions.codename,
                                    'link': str(permissions.content_type.app_label + ':' + permissions.codename),
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

            SubMenus = Permissionmenu.objects.filter(menu=menu['id']).order_by('order').exclude(permission__codename__icontains='index')
            SubMenus = serializers.serialize('json', SubMenus, indent=2, use_natural_foreign_keys=True)
            SubMenus = json.loads(SubMenus)
            for sm in SubMenus:
                name_sb = Permission.objects.get(pk=sm['pk'])
                sm['fields']['name'] = name_sb.name
                sm['fields']['route'] = name_sb.content_type.app_label +':'+name_sb.codename
            for per in permiso_menu:
                if(menu['id'] == per['menu_id']):
                    permisos[index]=per
                    index = index + 1
            self.request.session['menu'][y]={'menu':menu['name'],'icon':menu['icon'],'permisos':permisos,'submenus':SubMenus}
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

            return render(request, 'security/index.html')

class Security(TemplateView):
    template_name = 'security/index.html'
    def get_context_data(self, **kwargs):
        eid=self.request.session['system']['eid']
        context = super().get_context_data(**kwargs)
        return context

class Roles(TemplateView):
    template_name = 'security/roles/index.html'
    def get_context_data(self, **kwargs):
        eid=self.request.session['system']['eid']
        context = super().get_context_data(**kwargs)
        context['app']  = ContentType.objects.filter().order_by('app_label').distinct('app_label')

        return context

class Role(View):
    def get(self, request, *args, **kwargs):
        DataRole= Group.objects.filter().order_by('pk')
        DataRole = serializers.serialize('json', DataRole, indent=2, use_natural_foreign_keys=True)
        DataRole = json.loads(DataRole)

        for rol in DataRole:
            DataPerm = Group.objects.get(pk=rol['pk']).permissions.filter(codename__icontains='index')
            DataPerm = serializers.serialize('json', DataPerm, indent=2, use_natural_foreign_keys=True)
            DataPerm = json.loads(DataPerm)

            for perm in DataPerm:
                try:
                    DataPermMenu = Permissionmenu.objects.get(pk=perm['pk'])
                    rol['fields']['menu'] = DataPermMenu.menu.name
                except:
                    rol['fields']['menu'] = ''

            rol['fields']['permisos'] = DataPerm
           
        return HttpResponse(json.dumps(DataRole), content_type='application/json')

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':

            data = Group()
            data.name = request.POST['name']
            
            if request.POST['pk']:
                data.pk=request.POST['pk']
                              
            data.save()
                
            DataRole= Group.objects.filter(pk = data.pk) 
            DataRole = serializers.serialize('json', DataRole, indent=2, use_natural_foreign_keys=True)
            DataRole = json.loads(DataRole)
            for rol in DataRole:
                DataPerm = Group.objects.get(pk=rol['pk']).permissions.filter(codename__icontains='index')
                DataPerm = serializers.serialize('json', DataPerm, indent=2, use_natural_foreign_keys=True)
                DataPerm = json.loads(DataPerm)

                for perm in DataPerm:
                    try:
                        DataPermMenu = Permissionmenu.objects.get(pk=perm['pk'])
                        rol['fields']['menu'] = DataPermMenu.menu.name
                    except:
                        rol['fields']['menu'] = ''

                rol['fields']['permisos'] = DataPerm

            return HttpResponse(json.dumps(DataRole), content_type='application/json')           

    def delete(self, request, *args, **kwargs):
        data_request = json.loads(request.body.decode('UTF-8'))

        if request.method == 'DELETE':
            Datarole = Group.objects.get(pk = data_request['pk']) 
            Datarole.delete()
            return HttpResponse(status=200)

class Access(View):
    def get(self, request, *args, **kwargs):
        Data = Permission.objects.filter(codename__icontains='index')
        Data = serializers.serialize('json', Data, indent=2, use_natural_foreign_keys=False)
        Data = json.loads(Data)

        for module in Data:
            DataM = Menu.objects.get(name=module['fields']['name'])
            module['fields']['menu'] = DataM.pk
        return HttpResponse(json.dumps(Data), content_type='application/json')

    def post(self, request, *args, **kwargs):   
        if request.method == 'POST':
            DataPermission= Permission.objects.filter(codename = request.POST['acl'],content_type=request.POST['app']) 
            if  DataPermission: 
                DataPermission = []
            else:     
                data = Permission()
                data.name = request.POST['name_module']
                # data.name = request.POST['submenu']
                data.codename = request.POST['acl']
                data.content_type = ContentType.objects.get(pk=request.POST['app'])                            
                data.save()
                
                DataPermission= Permission.objects.filter(pk = data.pk) 
                DataPermission = serializers.serialize('json', DataPermission, indent=2, use_natural_foreign_keys=False)
                DataPermission = json.loads(DataPermission)
                
                datamenu = Menu()
                datamenu.state = 'A'
                datamenu.order = 1
                datamenu.name = request.POST['name_module']
                datamenu.save()

                datamenuper = Permissionmenu()
                datamenuper.permission = Permission.objects.get(pk = data.pk) 
                datamenuper.order = 1
                datamenuper.menu = Menu.objects.get(pk = datamenu.id) 
                datamenuper.save()
                

                for module in DataPermission:
                    DataM = Menu.objects.get(name=module['fields']['name'])
                    module['fields']['menu'] = DataM.pk
            
            return HttpResponse(json.dumps(DataPermission), content_type='application/json')   

    def put(self, request, *args, **kwargs):   
        if request.content_type.startswith('multipart'):
            put, files = request.parse_file_upload(request.META, request)
            request.FILES.update(files)
            request.PUT = put.dict()
        else:
            request.PUT = QueryDict(request.body).dict()

        DataOld= Permission.objects.filter(pk = request.PUT['pk']) 
        DataOld = serializers.serialize('json', DataOld, indent=2, use_natural_foreign_keys=False)
        DataOld = json.loads(DataOld)

        DataPermission = []

        data = Permission.objects.get(pk = request.PUT['pk']) 
        data.name = request.PUT['name_module']
        data.codename = request.PUT['acl']
        data.content_type = ContentType.objects.get(pk=request.PUT['app'])                            
        data.save()
        
        DataPermission= Permission.objects.filter(pk = data.pk) 
        DataPermission = serializers.serialize('json', DataPermission, indent=2, use_natural_foreign_keys=False)
        DataPermission = json.loads(DataPermission)

        datamenu = Menu.objects.get(name = DataOld[0]['fields']['name'])
        datamenu.state = 'A'
        datamenu.order = 1
        datamenu.name = request.PUT['name_module']
        datamenu.save()

        datamenuper = Permissionmenu.objects.get(pk = request.PUT['pk'])
        datamenuper.permission = Permission.objects.get(pk = data.pk) 
        datamenuper.order = 1
        datamenuper.menu = Menu.objects.get(pk = datamenu.id) 
        datamenuper.save()
        
        for module in DataPermission:
            DataM = Menu.objects.get(name=module['fields']['name'])
            module['fields']['menu'] = DataM.pk
        return HttpResponse(json.dumps(DataPermission), content_type='application/json')

    def delete(self, request, *args, **kwargs):
        data_request = json.loads(request.body.decode('UTF-8'))

        if request.method == 'DELETE':
            DataMenuPer = Permissionmenu.objects.get(permission_id = data_request['pk']) 
            DataMenuPer.delete()
            DataModule = Permission.objects.get(pk = data_request['pk']) 
            DataModule.delete()
            DataMenu = Menu.objects.get(name = DataModule.name) 
            DataMenu.delete()
            return HttpResponse(status=200)

class Menus(View):
    def get(self, request, *args, **kwargs):
        Data = Menu.objects.filter(state='A').order_by('order')
        Data = serializers.serialize('json', Data, indent=2, use_natural_foreign_keys=True)
        return HttpResponse(Data, content_type='application/json')

class SubMenus(View):
    def get(self, request, *args, **kwargs):
        Data = Permissionmenu.objects.filter(menu=request.GET['menu']).order_by('order').exclude(permission__codename__icontains='index')
        Data = serializers.serialize('json', Data, indent=2, use_natural_foreign_keys=True)
        Data = json.loads(Data)
        for d in Data:
            DataSM = Permission.objects.filter(pk=d['pk'])
            DataSM = serializers.serialize('json', DataSM, indent=2, use_natural_foreign_keys=False)
            DataSM = json.loads(DataSM)
            d['submenus'] = DataSM[0]
            
        return HttpResponse(json.dumps(Data), content_type='application/json')
    def post(self, request, *args, **kwargs):   
        if request.method == 'POST':
            DataSubMenu = []
            DataPermission= Permission.objects.filter(codename = request.POST['acl'],content_type=request.POST['app']) 
            if  DataPermission: 
                DataPermission = []
            else:     
                data = Permission()
                data.name = request.POST['submenu']
                data.codename = request.POST['acl']
                data.content_type = ContentType.objects.get(pk=request.POST['app'])                            
                data.save()
                
                DataPermission= Permission.objects.filter(pk = data.pk) 
                DataPermission = serializers.serialize('json', DataPermission, indent=2, use_natural_foreign_keys=False)
                DataPermission = json.loads(DataPermission)
                
                datamenuper = Permissionmenu()
                datamenuper.permission = Permission.objects.get(pk = data.pk) 
                datamenuper.order = request.POST['ordensub']
                datamenuper.menu = Menu.objects.get(pk = request.POST['menu']) 
                datamenuper.save()
                
                DataSubMenu= Permissionmenu.objects.filter(pk = datamenuper.pk) 
                DataSubMenu = serializers.serialize('json', DataSubMenu, indent=2, use_natural_foreign_keys=False)
                DataSubMenu = json.loads(DataSubMenu)
                for d in DataSubMenu:
                    DataSM = Permission.objects.filter(pk=d['pk'])
                    DataSM = serializers.serialize('json', DataSM, indent=2, use_natural_foreign_keys=True)
                    DataSM = json.loads(DataSM)
                    d['submenus'] = DataSM[0]
                
            return HttpResponse(json.dumps(DataSubMenu), content_type='application/json')   

    def put(self, request, *args, **kwargs):   
        if request.content_type.startswith('multipart'):
            put, files = request.parse_file_upload(request.META, request)
            request.FILES.update(files)
            request.PUT = put.dict()
        else:
            request.PUT = QueryDict(request.body).dict()

        DataOld= Permission.objects.filter(pk = request.PUT['pk']) 
        DataOld = serializers.serialize('json', DataOld, indent=2, use_natural_foreign_keys=False)
        DataOld = json.loads(DataOld)

        DataPermission = []

        data = Permission.objects.get(pk = request.PUT['pk']) 
        data.name = request.PUT['submenu']
        data.codename = request.PUT['acl']
        data.content_type = ContentType.objects.get(pk=request.PUT['app'])                            
        data.save()
        
        DataPermission= Permission.objects.filter(pk = data.pk) 
        DataPermission = serializers.serialize('json', DataPermission, indent=2, use_natural_foreign_keys=False)
        DataPermission = json.loads(DataPermission)

        datamenuper = Permissionmenu.objects.get(pk = request.PUT['pk'])
        datamenuper.permission = Permission.objects.get(pk = data.pk) 
        datamenuper.order = request.PUT['ordensub']
        datamenuper.menu = Menu.objects.get(pk = request.PUT['menu']) 
        datamenuper.save()
        
        DataSubMenu= Permissionmenu.objects.filter(pk = datamenuper.pk) 
        DataSubMenu = serializers.serialize('json', DataSubMenu, indent=2, use_natural_foreign_keys=False)
        DataSubMenu = json.loads(DataSubMenu)
        for d in DataSubMenu:
            DataSM = Permission.objects.filter(pk=d['pk'])
            DataSM = serializers.serialize('json', DataSM, indent=2, use_natural_foreign_keys=True)
            DataSM = json.loads(DataSM)
            d['submenus'] = DataSM[0]
        return HttpResponse(json.dumps(DataSubMenu), content_type='application/json')

    def delete(self, request, *args, **kwargs):
        data_request = json.loads(request.body.decode('UTF-8'))

        if request.method == 'DELETE':
            DataMenuPer = Permissionmenu.objects.get(permission_id = data_request['pk']) 
            DataMenuPer.delete()
            DataModule = Permission.objects.get(pk = data_request['pk']) 
            DataModule.delete()
            return HttpResponse(status=200)


class Rolepermission(View):
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            #varios valores
            Data = dict(request.POST)
            very_rol=[]
            for id in Data['roles']:
                Datarole = Group.objects.get(pk = id) 
                if not Datarole.permissions.filter(pk = request.POST['access']):
                    very_rol.append(id)
                    Datarole.permissions.add(request.POST['access'])

            #enviando a la vista permisos que solo faltan crear
            DataRole= Group.objects.filter(pk__in=very_rol).order_by('pk')
            DataRole = serializers.serialize('json', DataRole, indent=2, use_natural_foreign_keys=True)
            DataRole = json.loads(DataRole)

            for rol in DataRole:
                DataPerm = Group.objects.get(pk=rol['pk']).permissions.filter(pk = request.POST['access'])
                DataPerm = serializers.serialize('json', DataPerm, indent=2, use_natural_foreign_keys=True)
                DataPerm = json.loads(DataPerm)
                for perm in DataPerm:
                    DataPermMenu = Permissionmenu.objects.get(pk=perm['pk'])
                    perm['fields']['menu'] = DataPermMenu.menu.name

                rol['fields']['permisos'] = DataPerm

            return HttpResponse(json.dumps(DataRole), content_type='application/json')   

    def delete(self, request, *args, **kwargs):
        data_request = json.loads(request.body.decode('UTF-8'))
        if request.method == 'DELETE':
            DataPerm = Permission.objects.get(pk=data_request['pk_perm'])
            Datarole = Group.objects.get(pk = data_request['pk_rol']) 
            Datarole.permissions.remove(DataPerm)
            return HttpResponse(status=200)

class Modules(TemplateView):
    template_name = 'security/modules/index.html'
    def get_context_data(self, **kwargs):
        eid=self.request.session['system']['eid']
        context = super().get_context_data(**kwargs)
        context['app']  = ContentType.objects.filter().order_by('app_label').distinct('app_label')

        return context

class Users(TemplateView):
    template_name = 'security/users/index.html'
    def get_context_data(self, **kwargs):
        eid=self.request.session['system']['eid']
        context = super().get_context_data(**kwargs)
        context['form'] = formPerson
        context['eid'] = eid
        return context

class People(View):
    def get(self, request, *args, **kwargs):
        Data = Person.objects.all()
        Data = serializers.serialize('json', Data, indent=2, use_natural_foreign_keys=False)
        Data = json.loads(Data)
        for person in Data:
            try:
                DataUser = User.objects.get(docid = person['pk'])
                DataGroupUser = DataUser.groups.filter()
                DataGroupUser = serializers.serialize('json', DataGroupUser, indent=2, use_natural_foreign_keys=False)
                DataGroupUser = json.loads(DataGroupUser)
                person['fields']['roles'] = DataGroupUser
                modules = []
                for group in DataGroupUser:
                    Datarole = Group.objects.get(pk = group['pk']) 
                    PermissionsGroup = Datarole.permissions.filter(codename__icontains='index')
                    PermissionsGroup = serializers.serialize('json', PermissionsGroup, indent=2, use_natural_foreign_keys=False)
                    PermissionsGroup = json.loads(PermissionsGroup)
                    for perGroup in PermissionsGroup:
                        if not perGroup['fields']['name'].upper() in modules:
                            modules.append(perGroup['fields']['name'].upper())
                person['fields']['modules'] = modules
                    
            except:
                datauser = User.objects.create(
                    username = person['fields']['docid'] ,
                    docid = Person.objects.get(pk = person['pk'])
                )
                datauser.set_password(person['fields']['docid'])
                datauser.save()
                DataGroupUser = datauser.groups.filter()
                DataGroupUser = serializers.serialize('json', DataGroupUser, indent=2, use_natural_foreign_keys=False)
                DataGroupUser = json.loads(DataGroupUser)
                person['fields']['roles'] = DataGroupUser
        return HttpResponse(json.dumps(Data), content_type='application/json')

    def post(self, request, *args, **kwargs):
        person = Person()
        person.docid = request.POST['docid']
        person.last_name0 = request.POST['last_name0']
        person.last_name1 = request.POST['last_name1']
        person.first_name = request.POST['first_name']
        # person.birthday = request.POST['birthday']
        # person.cellphone = request.POST['cellphone']
        person.mail_person = request.POST['mail']
        person.civil = request.POST['civil']
        person.sex = request.POST['sex']
        entity = Entity.objects.get(pk=self.request.session['system']['eid'])
        person.eid = entity
        person.save()
        DataPerson = Person.objects.filter(pk = person.id)
        DataPerson = serializers.serialize('json', DataPerson, indent=2, use_natural_foreign_keys=True)
        return HttpResponse(DataPerson, content_type='application/json')

class RolesUser(View):
    def get(self, request, *args, **kwargs):
        person_id = request.GET['person_id']

        DataGroupall = Group.objects.filter()
        DataGroupall = serializers.serialize('json', DataGroupall, indent=2, use_natural_foreign_keys=True)
        DataGroupall = json.loads(DataGroupall)
        person = Person.objects.get(pk = person_id)


        DataUser = User.objects.get(docid = person.pk)
        DataGroupUser = DataUser.groups.filter()
       
        for allg in DataGroupall:
            data_user = User.objects.get(docid = person.pk)
            allg['fields']['user']= data_user.pk
            DataRoleMenu = Group.objects.filter(pk = allg['pk']) 
            if DataRoleMenu:
                allg['fields']['name']= DataRoleMenu[0].name.upper()
            else:
                allg['fields']['name']= allg['fields']['name'].upper()


            allg['fields']['access']= False
            if Group.objects.get(pk=allg['pk']) in DataGroupUser:
                allg['fields']['access']=True
                
        return HttpResponse(json.dumps(DataGroupall), content_type='application/json')
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            data_request= json.loads(request.body.decode('utf-8'))

            group = Group.objects.get(pk=data_request['accid'])
            dataUser = User.objects.get(pk=data_request['uid'])

            if data_request['very']:
                dataUser.groups.remove(group)
            else:
                dataUser.groups.add(group)

            return HttpResponse(status=200, content_type='application/json')

class RestPass(View):
    def get(self, request, *args, **kwargs):
        person_id = request.GET['person_id']
        person = Person.objects.get(pk = person_id)

        try:
            DataUser = User.objects.get(docid = person.pk)
            DataUser.set_password(person.docid)
            DataUser.save()
        except:
            datauser = User.objects.create(
                username=person.docid,
                docid=person
            )
            datauser.set_password(person.docid)
            datauser.save()
                
        return HttpResponse(status=200, content_type='application/json')

class importLolcli(View):
    def get(self, request, *args, **kwargs):
        headers = {'Content-Type':'application/json', 'Authorization':'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNjRmNDQ3NzQyZTUyMzVkYjFiZDMxYzdmNzIxMDJhNDE2ZDMxNjRkZjI0OWYyYTJhMTE5MDUwZmM1MThlYzUxYjFhNDk1YzVkNDg1N2U2N2MiLCJpYXQiOjE2MDU1NTU2NDksIm5iZiI6MTYwNTU1NTY0OSwiZXhwIjoxNjM3MDkxNjQ5LCJzdWIiOiIxIiwic2NvcGVzIjpbXX0.CZoFXQuif42sZwlsHpNbXQ0EEDvuHfVnoOY93Lb5T-U8ZL3XRaTPqGN6ThfFyoMEswrhOnwckln0sRP55VgGxB38uAs3vwHBrD0WhebJQT1cWKyvRdBcH7lSerOeXkEwyoKAOPE6OEZ9KpgCnmwtPVB000yurAvOzm2szX9kmAfGQcUI4rbN-PKviAwmmzeuB-DwQUtaIV1Xz0dRvDdFczA-KkxcVRnEGLVqebGqAYFVYLmsyhItG16f9IX6faOAxbOMpsKqTlh2p6z2DJPrr7yl1o_mpjkORvw2kVVebOjC8cFysfV7NZWJ25EjHimq_KjIlGZWflQnXVUbqqxuiiBfuEYZlqxrTZSLJZUGKFzJPMeqDzHbRoRseyDjqWhtO-nueplQKLIOBUeqJrFfeJEsXveIuwJzhU-rdkT5C1KR5N998nNLvCmjJ_VsG6vmKZIH55p8q2Pd4Y5mSg2ly_NWR_ckSSASNcfhqC-EkXCbWT5tcciJCToFqML0rG80IfgYhwI_1RHOXfUOGsbYdwSzQSItSXNZFM75ouUxuq0t5VCIK9VkxNzibeQtujCUrpK3PNrlCZbqqlQbQaUgwTgfMTbwyNSkGV6YiUa6jWO6BwDMxk8R7V6KeWOIaRuyZxGKAxITfB-SOpG-2WXYkhE0z6Or9ACdtBBCCTAXDfY'}
        response = requests.get("http://200.60.4.197/lolcliusers",headers = headers)
        data_lolcli = response.json()

        data_person = Person.objects.all()
        data_person = serializers.serialize('json', data_person, indent=2, use_natural_foreign_keys=False)
        data_person = json.loads(data_person)
        doc_people = []
        for person in data_person:
            doc_people.append(person['fields']['docid'])
        people_save = []
        for data in data_lolcli['data']:
            if not data['documento'] in doc_people:
                name_complete = data['nombre'].split(' ',2)
                person = Person()
                person.last_name0 = name_complete[0]
                try:
                    person.last_name1 = name_complete[1]
                except:
                    person.last_name1 = name_complete[0]
                finally:
                    try:
                        person.first_name = name_complete[2]
                    except:
                        person.first_name = name_complete[0]
                    finally:
                        pass
                person.docid = data['documento']
                entity = Entity.objects.get(pk=self.request.session['system']['eid'])
                person.eid = entity
                person.save()
                DataPerson = Person.objects.filter(pk = person.id)
                DataPerson = serializers.serialize('json', DataPerson, indent=2, use_natural_foreign_keys=True)
                DataPerson = json.loads(DataPerson)
                people_save.append(DataPerson[0])
        return HttpResponse(json.dumps(people_save), content_type='application/json')
        

class importUsers(View):
    def get(self, request, *args, **kwargs):
        person_id = request.GET['person_id']
        person = Person.objects.get(pk = person_id)
        datauser = User.objects.create(
            username=person.docid,
            docid=person
        )
        datauser.set_password(person.docid)
        datauser.save()
        return HttpResponse(status=200, content_type='application/json')
        
def SaveOrderSubMenu(request, *args, **kwargs):
    if request.method == 'POST':
        codep = request.POST
        elementos_menu = codep.dict()
        elementmenu_separate_comma = []
        for submenu in elementos_menu:
            elementmenu_separate_comma = json.loads(submenu)
        for index, elementmenu in enumerate(elementmenu_separate_comma, start=1):     
            Permissionmenu.objects.filter(pk = elementmenu['id']).update(order=index)  

        return HttpResponse(status=200, content_type='application/json')
    else:
        return HttpResponse(status=500)