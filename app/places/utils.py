from .models import Place, Category, SubCategory, BusinessHour, PlaceAction, User
import datetime
import math


def place_flex(request, id, line_user_id, distance = None):
    try:
        now = datetime.datetime.now()
        place = Place.objects.get(pk=id)
        business_hour = BusinessHour.objects.get(
            day=now.weekday(), place=place)
        if business_hour.open_time is None:
            business_hour_text = "ไม่พบข้อมูล"
        else:
            business_hour_text = f"{business_hour.open_time.strftime('%H:%M')} - {business_hour.close_time.strftime('%H:%M')}"
    except Place.DoesNotExist:
        return False

    body_header_cover = {
        "type": "image",
        "url": place.image_url,
        "size": "full",
        "aspectMode": "cover",
        "gravity": "center",
        "aspectRatio": "20:13"
    }

    body_header_gradient = {
        "type": "box",
        "layout": "vertical",
        "contents": [],
        "position": "absolute",
        "background": {
                "type": "linearGradient",
                "angle": "0deg",
                "endColor": "#00000000",
            "startColor": "#00000099"
        },
        "width": "100%",
        "height": "70%",
        "offsetBottom": "0px",
        "offsetStart": "0px",
        "offsetEnd": "0px"
    }

    review_detail = {
        "type": "box",
        "layout": "baseline",
        "contents": [],
        "spacing": "xs",
        "paddingBottom": "sm"
    }

    if place.review_score is not None:
        for gold_star in range(int(place.review_score)):
            gold_star = {
                "type": "icon",
                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png",
                "size": "sm"
            }
            review_detail['contents'].append(gold_star)

        for gray_star in range(5-int(place.review_score)):
            gray_star = {
                "type": "icon",
                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png",
                "size": "sm"
            }
            review_detail['contents'].append(gray_star)

        review_content = {
            "type": "text",
            "text": f"{place.review_score or 0} ({place.review_count or 0})",
            "color": "#ffffff",
            "size": "sm"
        }
    else:
        review_content = {
            "type": "text",
            "text": "ไม่มีคะแนนรีวิว",
            "color": "#a9a9a9",
            "size": "sm"
        }

    review_detail['contents'].append(review_content)

    body_header_detail = {
        "type": "box",
        "layout": "horizontal",
        "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": place.display_name,
                                    "size": "lg",
                                    "color": "#ffffff",
                                    "wrap": True,
                                    "weight": "bold"
                                }
                            ]
                        },
                        review_detail,
                        {
                            "type": "separator"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": business_hour.weekday[0:3],
                                            "size": "xs",
                                            "color": "#ffffff",
                                            "align": "center",
                                            "offsetTop": "1px"
                                        }
                                    ],
                                    "backgroundColor": "#ff334b",
                                    "width": "50px",
                                    "height": "20px",
                                    "cornerRadius": "18px"
                                },
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": business_hour_text,
                                            "color": "#ffffff",
                                            "size": "sm",
                                            "flex": 0,
                                            "align": "end"
                                        },
                                        {
                                            "type": "text",
                                            "text": "¥82,000",
                                            "color": "#a9a9a9",
                                            "decoration": "line-through",
                                            "size": "xs",
                                            "align": "end"
                                        }
                                    ],
                                    "flex": 0,
                                    "spacing": "lg"
                                }
                            ],
                            "spacing": "md",
                            "paddingTop": "md",
                            "alignItems": "center"
                        }
                    ],
                    "spacing": "xs"
                }
        ],
        "position": "absolute",
        "offsetBottom": "0px",
        "offsetStart": "0px",
        "offsetEnd": "0px",
        "paddingAll": "20px"
    }
    
    body_header_distance = None
    
    if distance is not None:
        body_header_distance = {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"ระยะทาง {format(distance,'.1f')} km",
                    "color": "#ffffff",
                    "size": "xs"
                }
            ],
            "position": "absolute",
            "height": "25px",
            "backgroundColor": "#ff334b",
            "offsetTop": "15px",
            "offsetEnd": "0px",
            "justifyContent": "center",
            "width": "120px",
            "alignItems": "center"
        }

    body_location_detail = {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "box",
                "layout": "baseline",
                "contents": [
                    {
                        "type": "text",
                        "text": "LOCATION",
                        "wrap": True,
                        "color": "#aaaaaa",
                        "size": "xxs",
                        "flex": 0
                    }
                ],
                "spacing": "sm"
            },
            {
                "type": "text",
                "text": place.location,
                "wrap": True,
                "size": "sm"
            }
        ],
        "paddingAll": "20px",
        "spacing": "sm"
    }

    if place.map_link is not None and str(place.map_link) != 'nan':

        body_location_detail['action'] = {
            "type": "uri",
            "label": "action",
            "uri": get_action_uri(request, line_user_id, place.id, 'map_link', None)
        }
        map_icon = {
            "type": "icon",
            "url": "https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-512.png",
            "size": "xxs"
        }

        body_location_detail['contents'][0]['contents'].append(map_icon)
        
    bubble = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [body_header_cover, body_header_gradient, body_header_detail, body_header_distance]
                },
                body_location_detail,
                {
                    "type": "separator"
                }
            ],
            "paddingAll": "0px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "filler"
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "filler"
                                },
                                {
                                    "type": "text",
                                    "text": "แนะนำสถานที่ใกล้เคียง",
                                    "margin": "sm",
                                    "offsetTop": "-1px",
                                    "flex": 0,
                                    "color": "#7F0019"
                                },
                                {
                                    "type": "filler"
                                }
                            ],
                            "spacing": "sm",
                            "flex": 0
                        },
                        {
                            "type": "filler"
                        }
                    ],
                    "spacing": "sm",
                    "borderWidth": "1px",
                    "borderColor": "#7F0019",
                    "cornerRadius": "8px",
                    "height": "40px",
                    "action": {
                        "type": "message",
                        "label": "แนะนำสถานที่ใกล้เคียง",
                        "text": f"#command-แนะนำสถานที่ใกล้เคียง#{place.display_name}"
                    }
                }
            ],
            "paddingAll": "20px",
            "spacing": "md"
        }
    }

    if place.online_link is not None and str(place.online_link) != 'nan':
        website_button = {
            "type": "button",
            "action": {
                "type": "uri",
                "label": "เว็บไซต์",
                "uri": get_action_uri(request, line_user_id, place.id, "online_link", place.online_link)
            },
            "style": "primary",
            "color": "#7F0019",
            "height": "sm"
        }
        bubble['footer']['contents'].append(website_button)

    if place.phone_number is not None and not math.isnan(float(place.phone_number)):
        phone_button = {
            "type": "button",
            "action": {
                "type": "uri",
                "label": f"โทร {place.phone_number}",
                "uri": get_action_uri(request, line_user_id, place.id, "phone_number", place.phone_number)
            },
            "style": "primary",
            "color": "#7F0019",
            "height": "sm"
        }
        bubble['footer']['contents'].append(phone_button)

    return bubble


def get_action_uri(request, line_user_id, place_id, action, target):
    uri = f'/api/v1/places/flex/action/?place={place_id}&customer_id={line_user_id}'
    uri += f'&action={action}&target={target}'
    return request.build_absolute_uri(uri)


def category_flex(request, id, line_user_id):
    try:
        category = Category.objects.get(pk=id)
    except Category.DoesNotExist:
        return False

    bubble = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "image",
                    "url": f"{category.image_url}",
                    "size": "full",
                    "aspectMode": "cover",
                    "aspectRatio": "2:3",
                    "gravity": "top"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "background": {
                        "type": "linearGradient",
                        "angle": "0deg",
                        "startColor": "#00000099",
                        "endColor": "#00000000"
                    },
                    "height": "60%",
                    "position": "absolute",
                    "width": "100%",
                    "offsetEnd": "0px",
                    "offsetBottom": "0px",
                    "offsetStart": "0px"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": category.name,
                                    "size": "xl",
                                    "color": "#ffffff",
                                    "weight": "bold",
                                    "wrap": True
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "filler"
                                },
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "contents": [
                                        {
                                            "type": "filler"
                                        },
                                        {
                                            "type": "text",
                                            "text": "เลือก",
                                            "color": "#ffffff",
                                            "flex": 0,
                                            "offsetTop": "-2px"
                                        },
                                        {
                                            "type": "filler"
                                        }
                                    ],
                                    "spacing": "sm"
                                },
                                {
                                    "type": "filler"
                                }
                            ],
                            "borderWidth": "1px",
                            "cornerRadius": "4px",
                            "spacing": "sm",
                            "borderColor": "#ffffff",
                            "margin": "xxl",
                            "height": "40px",
                            "action": {
                                "type": "message",
                                "text": category.name,
                                "label": "เลือก"
                            }
                        }
                    ],
                    "position": "absolute",
                    "offsetBottom": "0px",
                    "offsetStart": "0px",
                    "offsetEnd": "0px",
                    "paddingAll": "20px",
                    "paddingTop": "18px"
                }
            ],
            "paddingAll": "0px"
        }
    }

    return bubble


def sub_category_flex(request, sub_categories, line_user_id):
    # try:
    #     category = Category.objects.get(pk=id)
    # except Category.DoesNotExist:
    #     return False

    sub_category_contents = []

    separator_content = {"type": "separator"}

    for i, sub_category in enumerate(sub_categories):
        sub_category_content = {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": sub_category,
                    "weight": "bold",
                    "size": "sm",
                    "flex": 1,
                    "gravity": "center",
                    "wrap": True,
                    "contents": [],
                    "margin": "none",
                    "offsetEnd": "none"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "เลือก",
                        "text": sub_category
                    },
                    "style": "primary",
                    "flex": 0,
                    "color": "#7F0019"
                }
            ]
        }
        sub_category_contents.append(sub_category_content)
        if (i+1) < len(sub_categories):
            sub_category_contents.append(separator_content)

    bubble = {
        "type": "bubble",
        "size": "mega",
        "direction": "ltr",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "โปรดเลือกประเภทสถานที่",
                    "weight": "bold",
                    "size": "md",
                    "color": "#FFFFFFFF",
                    "align": "center",
                    "contents": []
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": sub_category_contents,
            "spacing": "lg"
        },
        "styles": {
            "header": {
                "backgroundColor": "#7F0019"
            }
        }
    }

    return bubble


def trip_flex(request, line_user_id, place_route_list, distance_list, total_distance, start_address):

    bubble = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "FROM",
                            "color": "#ffffff66",
                            "size": "sm"
                        },
                        {
                            "type": "text",
                            "text": f"{start_address[0:10]}",
                            "color": "#ffffff",
                            "size": "xl",
                            "flex": 4,
                            "weight": "bold"
                        }
                    ],
                    "flex": 2
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "postback",
                                "label": "แชร์",
                                "data": "hello"
                            },
                            "style": "secondary",
                            "height": "sm"
                        }
                    ]
                }
            ],
            "paddingAll": "20px",
            "spacing": "md",
            "height": "85px",
            "paddingTop": "22px",
            "backgroundColor": "#7F0019"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"Total: {total_distance} km.",
                    "color": "#b7b7b7",
                    "size": "xs"
                }
            ]
        }
    }

    for index, place in enumerate(place_route_list):
        distance = 0
        if index < len(distance_list):
            distance = distance_list[index]

        if place == 'user' and index == 0:
            place_node = {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "filler"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [],
                                    "cornerRadius": "30px",
                                    "height": "12px",
                                    "width": "12px",
                                    "borderColor": "#7F0019",
                                    "borderWidth": "2px"
                                },
                                {
                                    "type": "filler"
                                }
                            ],
                            "flex": 0
                        },
                    {
                            "type": "text",
                            "text": "Start",
                            "gravity": "center",
                            "flex": 4,
                            "size": "sm"
                            }
                ],
                "spacing": "lg",
                "cornerRadius": "30px",
                "margin": "xl"
            }
            route_line = {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "filler"
                                        },
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [],
                                            "width": "2px",
                                            "backgroundColor": "#B7B7B7"
                                        },
                                        {
                                            "type": "filler"
                                        }
                                    ],
                                    "flex": 1
                                }
                            ],
                            "width": "12px"
                        },
                    {
                            "type": "text",
                            "text": f"{distance} km.",
                            "gravity": "center",
                            "flex": 4,
                            "size": "xs",
                            "color": "#8c8c8c"
                            }
                ],
                "spacing": "lg",
                "height": "30px"
            }
            bubble['body']['contents'].append(place_node)
            bubble['body']['contents'].append(route_line)
        elif place == 'user' and index != 0:
            place_node = {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "filler"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [],
                                    "cornerRadius": "30px",
                                    "height": "12px",
                                    "width": "12px",
                                    "borderColor": "#7F0019",
                                    "borderWidth": "2px"
                                },
                                {
                                    "type": "filler"
                                }
                            ],
                            "flex": 0
                        },
                    {
                            "type": "text",
                            "text": "End",
                            "gravity": "center",
                            "flex": 4,
                            "size": "sm"
                            }
                ],
                "spacing": "lg",
                "cornerRadius": "30px"
            }
            bubble['body']['contents'].append(place_node)
        else:
            place_node = {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "filler"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [],
                                    "cornerRadius": "30px",
                                    "width": "12px",
                                    "height": "12px",
                                    "borderColor": "#6486E3",
                                    "borderWidth": "2px"
                                },
                                {
                                    "type": "filler"
                                }
                            ],
                            "flex": 0
                        },
                    {
                            "type": "text",
                            "text": place,
                            "gravity": "center",
                            "flex": 4,
                            "size": "sm",
                            "action": {
                                "type": "message",
                                "text": f"#command-ข้อมูลสถานที่#{place}"
                            }
                            }
                ],
                "spacing": "lg",
                "cornerRadius": "30px"
            }
            route_line = {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "filler"
                                        },
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [],
                                            "width": "2px",
                                            "backgroundColor": "#6486E3"
                                        },
                                        {
                                            "type": "filler"
                                        }
                                    ],
                                    "flex": 1
                                }
                            ],
                            "width": "12px"
                        },
                    {
                            "type": "text",
                            "text": f"{distance} km.",
                            "gravity": "center",
                            "flex": 4,
                            "size": "xs",
                            "color": "#8c8c8c"
                            }
                ],
                "spacing": "lg",
                "height": "30px"
            }
            bubble['body']['contents'].append(place_node)
            bubble['body']['contents'].append(route_line)

    return bubble
