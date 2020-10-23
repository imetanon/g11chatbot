from django.shortcuts import redirect
from django.http import HttpResponse

from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Place, Category, SubCategory, BusinessHour, PlaceAction, User
from .serializers import PlaceSerializer, CategorySerializer, SubCategorySerializer

import datetime


class PlaceList(generics.ListCreateAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer


class PlaceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer


class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubCategoryList(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


class SubCategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


@api_view(['GET'])
def place_action(request):
    if request.method == 'GET':
        place = request.query_params.get('place', None)
        line_user_id = request.query_params.get('customer_id', None)
        action = request.query_params.get('action', None)
        target = request.query_params.get('target', None)

        place = Place.objects.get(pk=place)
        
        try:
          user = User.objects.get(line_user_id=line_user_id)
        except User.DoesNotExist:
          user = User.objects.create(line_user_id=line_user_id, birth_year=1984)

        if action == 'online_link':
            place_act = PlaceAction.objects.create(
                user=user, place=place, action="online_link")
            return redirect(target or 'https://www.google.com')
        elif action == 'phone_number':
            place_act = PlaceAction.objects.create(
                user=user, place=place, action="phone_number")
            return Response(headers={'Cache-Control': 'no-cache', 'location': f'tel:{target}'}, status=status.HTTP_301_MOVED_PERMANENTLY)
        elif action == 'map_link':
            place_act = PlaceAction.objects.create(
                user=user, place=place, action="maps_link")
            return redirect(place.map_link)

    return Response(status=status.HTTP_404_NOT_FOUND)
