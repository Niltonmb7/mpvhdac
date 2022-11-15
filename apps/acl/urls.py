from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views import Security, Roles, Role, Access, Menus, SubMenus, Rolepermission, People, RolesUser, RestPass, importLolcli,importUsers

app_name = "acl"

urlpatterns = [
    path('', views.SecLogin.as_view(), name='login_security'),
    path('home/', login_required(views.HomeSecurity.as_view()), name='home_security'),
    path('home_security/', login_required(views.Security.as_view()), name='index_security'),
    path('logout/', login_required(views.logoutSec), name='logoutsec'),

    path('roles/', login_required(views.Roles.as_view()), name='roles'),
    path('roles/role/', Role.as_view(), name='role'),
    path('roles/access/', Access.as_view(), name='access'),
    path('roles/rolepermission/', Rolepermission.as_view(), name='rolepermission'),

    path('modules/', login_required(views.Modules.as_view()), name='modules'),
    path('modules/access/', Access.as_view(), name='access'),
    path('modules/menu/', Menus.as_view(), name='menu'),
    path('modules/submenu/', SubMenus.as_view(), name='submenu'),
    path('modules/ordersubmenu/', views.SaveOrderSubMenu, name='ordersubmenu'),

    path('users/', login_required(views.Users.as_view()), name='users'),
    path('users/people/', People.as_view(), name='people'),
    path('users/roles/', RolesUser.as_view(), name='rolesuser'),
    path('users/restpass/', RestPass.as_view(), name='restpass'),
    path('users/importLolcli/', importLolcli.as_view(), name='importLolcli'),
    path('users/importUsers/', importUsers.as_view(), name='importUsers'),
]
