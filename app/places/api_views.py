from django.shortcuts import redirect
from django.http import HttpResponse

from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Place
from .serializers import PlaceSerializer

import datetime

class PlaceList(generics.ListCreateAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer


class PlaceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer

@api_view(['GET'])
def place_action(request):
    if request.method == 'GET':
        action=request.query_params.get('action',None)
        target=request.query_params.get('target',None)
        
        if action == 'online_link':
            return redirect(target or 'https://www.google.com')
        elif action == 'call':
            return Response(headers={'location':f'tel:{target}'}, status=status.HTTP_301_MOVED_PERMANENTLY)
    return Response(None,status=status.HTTP_200_OK)
            
@api_view(['GET'])
def place_flex(request, pk):
    
    now = datetime.datetime.now()
    print(now.strftime("%A"))
    print(now.weekday())
    # datetime.datetime.today().weekday()
    try:
        place = Place.objects.get(pk=pk)
    except Place.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        
        print(place.business_hours.values().get(day=7))

        review_stars = []
        
        if place.review_score is not None:
            for gold_star in range(int(place.review_score)):
                gold_star = {
                    "type": "icon",
                    "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png",
                    "size": "sm"
                }
                review_stars.append(gold_star)

            for gray_star in range(5-int(place.review_score)):
                gray_star = {
                    "type": "icon",
                    "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png",
                    "size": "sm"
                }
                review_stars.append(gray_star)
       
            review_contents = [
                {
                    "type": "text",
                    "text": f"{place.review_score or 0} ({place.review_count or 0})",
                    "size": "sm",
                    "color": "#999999",
                    "flex": 0,
                    "margin": "md",
                    "contents": []
                }
            ]

            review_contents = review_stars + review_contents
        else:
            review_contents = [
                {
                    "type": "text",
                    "text": "ไม่มีคะแนนรีวิว",
                    "size": "sm",
                    "color": "#999999",
                    "flex": 0,
                    "margin": "md",
                    "contents": []
                }
            ]

        contents = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                # "action": {
                #     "type": "uri",
                #     "label": "Line",
                #     "uri": "https://linecorp.com/"
                # }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": place.display_name,
                        "weight": "bold",
                        "size": "xl",
                        "contents": []
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "margin": "md",
                        "contents": review_contents
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Place",
                                        "size": "sm",
                                        "color": "#AAAAAA",
                                        "flex": 1,
                                        "contents": []
                                    },
                                    {
                                        "type": "text",
                                        "text": place.location,
                                        "size": "sm",
                                        "color": "#666666",
                                        "flex": 5,
                                        "wrap": True,
                                        "contents": []
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Time",
                                        "size": "sm",
                                        "color": "#AAAAAA",
                                        "flex": 1,
                                        "contents": []
                                    },
                                    {
                                        "type": "text",
                                        "text": "10:00 - 23:00",
                                        "size": "sm",
                                        "color": "#666666",
                                        "flex": 5,
                                        "wrap": True,
                                        "contents": []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "flex": 0,
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "CALL",
                            "uri": request.build_absolute_uri(f'action/?action=call&target={place.phone_number or "0874797686"}')
                        },
                        "height": "sm",
                        "style": "link"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "WEBSITE",
                            "uri": request.build_absolute_uri(f'action/?action=online_link&target={place.online_link}')
                        },
                        "height": "sm",
                        "style": "link"
                    },
                    {
                        "type": "spacer",
                        "size": "sm"
                    }
                ]
            }
        }

        message = {
            "type": "flex",
            "altText": "this is a flex message",
            "contents": contents
        }

        data = {
            "line_payload": [message]
        }

        headers = {
            'reply-by-object': True
        }

        return Response(data, headers=headers, status=status.HTTP_200_OK)
