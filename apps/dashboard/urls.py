from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = "dashboard"

urlpatterns = [
    path('newuser/', views.Newuser.as_view(), name='newuser'),
    path('validation/',views.validation, name='validation'),
    path('verify/',views.verify_user, name='verify_user'),
    path('logout/', login_required(views.logoutUser), name='logout'),
    #agregar Login y comentar
    # TUCI
    # path('', views.TUCILogin.as_view(), name='login'),
    # path('signup/', views.TUCISignup.as_view(), name='signup'),
    # path('home/', login_required(views.Home.as_view()), name='home'),
    # path('reniec/',views.reniec_tuci,name='reniec'),
    # MPV
    path('', views.MPVLogin.as_view(), name='login'),
    path('signup/', views.MPVSignup.as_view(), name='signup'),
    path('home/', login_required(views.MPVHome.as_view()), name='index_mpv'),
    path('home/datos/', login_required(views.getDataReport), name='report_data'),
    path('reniec/',views.reniec_mpv,name='reniec'),
    path('restorepass/',views.MPVRestorePass.as_view(),name='restore_pass'),
    path('profile/',login_required(views.MPVDataProfile.as_view()),name='profile'),
]
