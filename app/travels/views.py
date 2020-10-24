from django.shortcuts import render
from .models import TripPlan
import json


def index(request):
    trip_plan_id = request.GET.get('planId',1)
    trip_plan = TripPlan.objects.get(pk=trip_plan_id)
    context = {
        'trip_plan': trip_plan.get_json_data
    }
    
    return render(request, 'travels/index.html', context)
