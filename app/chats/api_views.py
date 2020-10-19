from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import LogSerializer
from .models import Log
from places.models import Place, Category, SubCategory, BusinessHour, PlaceAction, User
from mls.api_views import get_recommend_nearest_place, get_recommend_place_by_location, get_subcategory_from_sentence
from places.utils import place_flex, trip_flex
from .utils import create_log


@api_view(['GET'])
def log_list(request):
    """
    List all users, or create a new user.
    """
    if request.method == 'GET':
        logs = Log.objects.all()
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def log_create(request):
    if request.method == 'GET':
        params = Log._meta.fields
        for param in params:
            param = param.get_attname()
            if param == 'line_user_id':
                request.data[param] = request.query_params.get(
                    'customer_id', None)
            else:
                request.data[param] = request.query_params.get(param, None)

        serializer = LogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def check_intent(request):
    if request.method == 'GET':
        keyword = request.query_params.get('keyword', None)
        line_user_id = request.query_params.get('customer_id', None)
        if keyword is not None and keyword[0] == '#':
            intent, target = keyword[1:].split('#')
            if intent == 'command-แนะนำสถานที่ใกล้เคียง':
                place = Place.objects.filter(display_name=target)
                
                if place.count() > 0: 
                
                    nearest_place_list = get_recommend_nearest_place(target)

                    bubble_carousel = []
                    for nearest_place in nearest_place_list:
                        place = Place.objects.filter(display_name=nearest_place)
                        bubble_carousel.append(place_flex(
                            request, place[0].id, line_user_id))

                    headers = {
                        'Response-Type': 'object'
                    }

                    message = {
                        "type": "flex",
                        "altText": f"ข้อมูลสถานที่",
                        "contents":
                            {
                                "type": "carousel",
                                "contents": bubble_carousel
                            }
                    }

                    payload = {
                        "line_payload": [message],
                    }

                    return Response(payload, headers=headers, status=status.HTTP_200_OK)
            elif intent == 'command-จัดทริป':
                print('trip-plan')
            elif intent == 'command-ข้อมูลสถานที่':
                place = Place.objects.filter(display_name=target)

                if place.count() > 0:
                    bubble_carousel = []
                    bubble_carousel.append(place_flex(request, place[0].id, line_user_id))

                    headers = {
                        'Response-Type': 'object'
                    }

                    message = {
                        "type": "flex",
                        "altText": f"ข้อมูลสถานที่",
                        "contents":
                            {
                                "type": "carousel",
                                "contents": bubble_carousel
                            }
                    }

                    payload = {
                        "line_payload": [message],
                    }

                    return Response(payload, headers=headers, status=status.HTTP_200_OK)
        
        else:
            headers = {
                'Response-Type': 'intent'
            }

            return Response({'intent': 'default_reply'}, headers=headers, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def check_location(request):
    if request.method == 'GET':
        location_state = request.query_params.get('location_state', None)
        sentence = request.query_params.get('sentence', None)
        line_user_id = request.query_params.get('customer_id', None)
        p_latitude = request.query_params.get('p_latitude', None)
        p_longitude = request.query_params.get('p_longitude', None)
        p_address = request.query_params.get('p_address', None)

        print(location_state, sentence)

        if location_state == 'DL_askplan' or location_state == '{{intent_select_travel_category}}':
            create_log(request, line_user_id, f'#DL_askplan#{sentence}')
            sub_category_list = get_subcategory_from_sentence(sentence)
            if sub_category_list != False:
                recommend_place_route, distance_list, total_distance = get_recommend_place_by_location(
                    line_user_id, sub_category_list, p_latitude, p_longitude)
                
                if recommend_place_route != False:
                    
                    bubble_carousel = []
                    bubble_carousel.append(trip_flex(request, line_user_id, recommend_place_route, distance_list, total_distance, p_address))

                    headers = {
                        'Response-Type': 'object'
                    }

                    message = {
                        "type": "flex",
                        "altText": f"ข้อมูลสถานที่",
                        "contents":
                            {
                                "type": "carousel",
                                "contents": bubble_carousel
                            }
                    }

                    payload = {
                        "line_payload": [message],
                    }

                    return Response(payload, headers=headers, status=status.HTTP_200_OK)
               
            #No match sub-cat or no in area 
            headers = {
                'Response-Type': 'intent'
            }
            return Response({'intent':'intent_error_trip'}, headers=headers, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)
