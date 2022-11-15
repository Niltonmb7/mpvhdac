from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = "expedient"

urlpatterns = [
    path('register/', login_required(views.registerExpedient.as_view()), name='register_expedient'),
    path('register/api/', login_required(views.apiExpedient.as_view()), name='api_expedient'),
    path('register/reniec/', views.reniec, name='reniec'),
    path('list/', login_required(views.listExpedient.as_view()), name='list_expedient'),
    path('list/api/', login_required(views.apiListExpedient.as_view()), name='api_list_expedient'),
    path('list/filterDate/', login_required(views.filterDate), name='filter_date'),
    path('list/getCorrect/', login_required(views.getCorrect), name='get_correct'),
    path('list/sendMail/', login_required(views.sendMailSGD), name='send_mail'),
    # path('report/', login_required(views.reportExpedient.as_view()), name='reportes'),
    # path('report/datos/', login_required(views.getDataReport), name='report_data'),
    path('error404/', views.error404.as_view(), name='error404'),
    path('error500/', views.error500.as_view(), name='error500'),
]