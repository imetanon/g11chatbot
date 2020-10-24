from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import LogSerializer
from .models import Log, ChatState
from places.models import Place, Category, SubCategory, BusinessHour, PlaceAction, User
from travels.models import TripPlan
from mls.api_views import get_recommend_nearest_place, get_recommend_place_by_location, get_trip_plan, create_distance_matrix_df, get_subcategory_from_sentence
from places.utils import place_flex, trip_flex
from .utils import create_log
import json


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
        response_status = status.HTTP_200_OK
        intent = 'intent_none'
        
        keyword = request.query_params.get('keyword', None)
        line_user_id = request.query_params.get('customer_id', None)
        create_log(line_user_id, keyword)
        if keyword is not None and keyword[0] == '#':
            intent, target = keyword[1:].split('#')
            print(f'Intent: {intent}, Target: {target}')
            if intent == 'command-แนะนำสถานที่ใกล้เคียง':
                place = Place.objects.filter(display_name=target)

                if place.count() > 0:
                    nearest_place_list = get_recommend_nearest_place(target)
                    bubble_carousel = []
                    for nearest_place in nearest_place_list:
                        place = Place.objects.filter(
                            display_name=nearest_place)
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
            elif intent == 'command-ข้อมูลสถานที่':
                place = Place.objects.filter(display_name=target)

                if place.count() > 0:
                    bubble_carousel = []
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
            elif intent == 'activity':
                intent = 'intent_asksubcategory'
            elif intent == 'place':
                intent = 'intent_recommendplace'
            elif intent == 'command-จัดทริป':
                intent = 'DL_askplan'
            elif intent == 'command-ค้นหาสถานที่ใกล้ตัว':
                intent = 'intent_searchbylocation'

            return handle_intent_chat_state(line_user_id, intent, keyword)
        else:
            if 'ทริป' in keyword.lower() or 'trip' in keyword.lower() or 'แผน' in keyword.lower() or 'plan' in keyword.lower() or 'แพลน' in keyword.lower():
                intent = 'DL_askplan'
                return handle_intent_chat_state(line_user_id, intent, keyword)
    headers = {
        'Response-Type': 'intent'
    }
    
    return Response({'intent': 'default_reply'}, headers=headers, status=response_status)

def handle_intent_chat_state(line_user_id, intent, keyword):
    try:
        user = User.objects.get(line_user_id=line_user_id, status=1)
        print(f'Intent: {intent}')
        chat_state = ChatState.objects.filter(user=user).update(intent=intent, target=keyword)
        headers = {
            'Response-Type': 'intent'
        }
        return Response({'intent': intent}, headers=headers, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        user = User.objects.update_or_create(line_user_id=line_user_id, defaults={'line_user_id': line_user_id, 'birth_year': 1984})
        chat_state = ChatState.objects.update_or_create(user=user[0], defaults={'intent': intent, 'target': keyword})
        response = {
            'message': 'User Does not exist.',
            'intent': "intent_createuser"
        }
        headers = {
            'Response-Type': 'intent'
        }
        return Response(response, headers=headers, status=status.HTTP_200_OK)

@api_view(['GET'])
def check_location(request):
    location_state = request.query_params.get('location_state', None)
    sentence = request.query_params.get('sentence', None)
    line_user_id = request.query_params.get('customer_id', None)
    p_latitude = request.query_params.get('p_latitude', None)
    p_longitude = request.query_params.get('p_longitude', None)
    p_address = request.query_params.get('p_address', None)
    keyword = request.query_params.get('keyword', None)
    
    user = User.objects.get(line_user_id=line_user_id)
    chat_state = ChatState.objects.get(user=user)
    print(chat_state.intent, sentence)
    if chat_state.intent == 'DL_askplan':
        sub_category_list = get_subcategory_from_sentence(sentence)
        if sub_category_list != False:
            
            intersect_place_df, user_location_df = get_recommend_place_by_location(line_user_id, sub_category_list, p_latitude, p_longitude, 15)
            recommend_place_route, distance_list, total_distance = get_trip_plan(intersect_place_df)
            
            if recommend_place_route != False:
                share_plan = {
                    "type": "flex",
                    "altText": "แผนการท่องเที่ยว",
                    "contents": trip_flex(request, line_user_id, recommend_place_route, distance_list, total_distance, p_address, share=True)
                }

                del share_plan['contents']['header']['contents'][-1]

                user = User.objects.get(line_user_id=line_user_id)
                trip_plan = TripPlan.objects.create(user=user, data=share_plan)

                bubble = trip_flex(request, line_user_id, recommend_place_route,
                                    distance_list, total_distance, p_address, share_plan_id=trip_plan.id)

                headers = {
                    'Response-Type': 'object'
                }

                message = {
                    "type": "flex",
                    "altText": "แผนการท่องเที่ยว",
                    "contents": bubble

                }

                payload = {
                    "line_payload": [message],
                }

                return Response(payload, headers=headers, status=status.HTTP_200_OK)

        # No match sub-cat or no in area
        headers = {
            'Response-Type': 'intent'
        }
        return Response({'intent': 'intent_error_trip'}, headers=headers, status=status.HTTP_200_OK)
    elif chat_state.intent == 'intent_searchbylocation':
        intersect_place_df, user_location_df = get_recommend_place_by_location(line_user_id, [], p_latitude, p_longitude)
        distance_matrix_df = create_distance_matrix_df(intersect_place_df)

        nearest_place_dict = distance_matrix_df['user'].to_dict()

        if len(nearest_place_dict) > 1:
            nearest_place_tuple_sorted = sorted(
                nearest_place_dict.items(), key=lambda x: x[1])

            bubble_carousel = []
            for nearest_place in nearest_place_tuple_sorted:
                if nearest_place[0] != 'user':
                    place = Place.objects.filter(
                        display_name=nearest_place[0])
                    bubble_carousel.append(place_flex(
                        request, place[0].id, line_user_id, distance=nearest_place[1]))

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
            return Response({'intent': 'intent_nearest_notfound'}, headers=headers, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)
