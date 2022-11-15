from django.urls import path
from .views import Person
from django.contrib.auth.decorators import login_required
from apps.acl.views import group_required

app_name='profiles'
urlpatterns = [
    path('', login_required(group_required('ADMIN', login_url='/home/')( Person.as_view())), name='index_person'),
]