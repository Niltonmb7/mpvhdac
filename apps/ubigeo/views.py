#Django
from django.http import JsonResponse
#Models
from .models import Department, Province, District

def json_response(items):
    result = []
    for item in items:
        result.append({
            'id': item.id,
            'name': item.name
        })
    return JsonResponse(result, safe=False)

def department(request, id):
    return json_response(Department.objects.filter(country__id=id))


def province(request, id):
    return json_response(Province.objects.filter(departament__id=id))


def district(request, id):
    return json_response(District.objects.filter(province__id=id))
