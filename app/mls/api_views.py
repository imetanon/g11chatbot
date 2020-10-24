from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core import serializers
from django.db.models import Q
from functools import reduce

from places.models import Place, Category, SubCategory, User, SubCategoryKeyword
from places.serializers import PlaceSerializer, CategorySerializer, SubCategorySerializer
from places.utils import place_flex, category_flex, sub_category_flex

import pandas as pd
import numpy as np
# import sefr_cut
import pythainlp
from pythainlp import sent_tokenize, word_tokenize
from pythainlp.corpus import thai_stopwords

from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import MinMaxScaler

import geopandas as gpd
from shapely.geometry import Point
from math import sin, cos, sqrt, atan2, radians
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def get_subcategory_from_sentence(sentence):

    word_split = word_tokenize(sentence, engine='newmm', keep_whitespace=False)
    word_split_lower = [word.lower() for word in word_split]
    word_split_list = pd.Series(word_split_lower).unique().tolist()
    word_split_clean = []
    
    for word in word_split_list:
        if word not in thai_stopwords():
            if word not in [' ','/','\'','-','.','108','11','7','','ๆ','ฯ']:
                word_split_clean.append(word)
    
    
    sub_category_keyword_list = SubCategoryKeyword.objects.filter(reduce(lambda x, y: x | y, [Q(
        keyword__contains=word) for word in word_split_clean])).order_by().values_list('sub_category__id', flat=True).distinct()
    
 
    print(word_split_clean)
    # print(sub_category_keyword_list)
    if sub_category_keyword_list.count() > 0:
        print(sub_category_keyword_list)
        return list(sub_category_keyword_list)

    return False


@api_view(['GET'])
def recommend_place(request):
    if request.method == 'GET':
        line_user_id = request.query_params.get('customer_id', None)
        keyword = request.query_params.get('keyword', None)
        sub_category = str(request.query_params.get('sub_category', None)).strip()
        
        if sub_category[0] == '#':
            sub_category = sub_category[1:].split('#')[1]
            
        if keyword[0] == '#':
            sub_category = keyword[1:].split('#')[1]
        
        place_list = Place.objects.filter(sub_category__sub_category_type=0,sub_category__name=sub_category).order_by('-review_count')[:5]

        print(len(place_list))

        bubble_carousel = []
        for place in place_list:
            bubble_carousel.append(place_flex(request, place.id, line_user_id))

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
            "line_payload": [message]
        }

        return Response(payload, headers=headers, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)

def get_recommend_nearest_place(place_name):
    df_prep = pd.DataFrame.from_records(
        Place.objects.filter(sub_category__sub_category_type=0).values('name', 'category__name', 'sub_category__name',
                                   'review_score', 'review_count', 'latitude', 'longitude')
    )
    
    # print(df_prep)

    df_prep["category__name"] = df_prep["category__name"].astype('category')
    df_prep["sub_category__name"] = df_prep["sub_category__name"].astype(
        'category')

    df = one_hot_encoder(df_prep)

    df_value = df.drop(columns='name')

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler = scaler.fit(df_value)
    df_scale = scaler.transform(df_value)

    df_distance = pd.DataFrame(euclidean_distances(df_scale), columns=df.reset_index()['name'], index=df.reset_index()['name'])

    # print(df_distance[place_name])
    recommend_nearest_place = df_distance[place_name].sort_values()[1:6].index.tolist()

    return recommend_nearest_place


def one_hot_encoder(dataframe):
    # Select category columns
    cat_df = dataframe.select_dtypes(include=['category']).columns.to_list()

    # Convert to one-hot dataframe
    one_hot_df = pd.get_dummies(dataframe, columns=cat_df, drop_first=True)

    return one_hot_df


@api_view(['GET'])
def show_category(request):

    if request.method == 'GET':
        
        line_user_id = request.query_params.get('customer_id', None)

        categories = Category.objects.all()

        bubble_carousel = []

        for category in categories:
            bubble_carousel.append(category_flex(request, category.id, line_user_id))

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
            "line_payload": [message]
        }

        return Response(payload, headers=headers, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def show_sub_category(request):

    if request.method == 'GET':
        
        category = request.query_params.get('category', None)
        line_user_id = request.query_params.get('customer_id', None)
        keyword = request.query_params.get('keyword', None)
        
        if category[0] == '#':
            category = category[1:].split('#')[1]
            
        if keyword[0] == '#':
            category = keyword[1:].split('#')[1]
            
        sub_categories = Place.objects.filter(
            category__name=category, sub_category__sub_category_type=0).values_list('sub_category__name', flat=True)

        if len(sub_categories) > 0:

            sub_categories = list(set(sub_categories))

            if len(sub_categories) > 5:
                sub_categories_list = [sub_categories[i:i + 5]
                                       for i in range(0, len(sub_categories), 5)]
            else:
                sub_categories_list = [sub_categories]

            bubble_carousel = []

            for sub_categories in sub_categories_list:
                bubble_carousel.append(sub_category_flex(
                    request, sub_categories, line_user_id))

            headers = {
                'Response-Type': 'object'
            }

            message = {
                "type": "flex",
                "altText": f"โปรดเลือกประเภทสถานที่",
                "contents":
                    {
                        "type": "carousel",
                        "contents": bubble_carousel
                    }
            }

            payload = {
                "line_payload": [message]
            }

            return Response(payload, headers=headers, status=status.HTTP_200_OK)
        else:
            headers = {
                'Response-Type': 'intent'
            }
            return Response({'intent':'intent_inputerror'}, headers=headers, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)


def get_recommend_place_by_location(line_user_id, sub_category_list, latitude, longitude, radius = 5):

    if len(sub_category_list) > 0 and sub_category_list != None:
        place_list = Place.objects.filter(sub_category__in=sub_category_list).values('id', 'display_name', 'category__name', 'review_count', 'latitude', 'longitude')
    else:
        place_list = Place.objects.all().values('id', 'display_name', 'category__name', 'review_count', 'latitude', 'longitude')
        
    place_df = pd.DataFrame.from_records(place_list)
    
    # Transform Dataframe to GeoDataframe

    place_df['geometry'] = place_df.apply(lambda x: Point(
        (float(x.longitude), float(x.latitude))), axis=1)

    place_geo_df = gpd.GeoDataFrame(place_df, geometry='geometry')
    place_geo_df.set_crs(epsg=4326, inplace=True)
    # print(place_geo_df.crs)

    input_from_line = [
        {'user': 'user', 'latitude': latitude, 'longitude': longitude}]
    user_location_df = pd.DataFrame.from_dict(input_from_line)
    user_location_df['geometry'] = Point(
        float(user_location_df.longitude), float(user_location_df.latitude))

    user_location_geo_df = gpd.GeoDataFrame(
        user_location_df, geometry='geometry')
    user_location_geo_df.set_crs(epsg=4326, inplace=True)

    user_location_geo_df['geometry'] = user_location_geo_df.geometry.buffer(
        radius/100)
    user_location_geo_df = user_location_geo_df.to_crs(epsg=4326)
    
    # Used Spartial Join to match Point to Polygon

    intersect_place_df = gpd.sjoin(
        user_location_geo_df, place_geo_df, how="left", op="contains")

    intersect_place_df["rank"] = intersect_place_df.groupby(
        ['category__name'])["review_count"].rank("dense", ascending=False)
    
    # intersect_place_list = intersect_place_df[intersect_place_df['rank']==1]['display_name'].tolist()
    # print(intersect_place_list)
    
    print(len(sub_category_list))
    
    if len(sub_category_list) <= 2 and len(sub_category_list) > 0 and len(sub_category_list) is not None:
        intersect_place_df = intersect_place_df[(intersect_place_df['rank'] == 1) | (intersect_place_df['rank'] == 2) | (intersect_place_df['rank'] == 3)]
    else:
        intersect_place_df = intersect_place_df[(intersect_place_df['rank'] == 1)]
    
    intersect_place_df = intersect_place_df[['display_name', 'latitude_right', 'longitude_right']].rename(
        columns={'latitude_right': 'latitude', 'longitude_right': 'longitude'})
    user_location_df = user_location_df[['user', 'longitude', 'latitude']].rename(
        columns={'user': 'display_name'})

    intersect_place_df = pd.concat(
        [user_location_df, intersect_place_df], axis=0)
    intersect_place_df['longitude'] = intersect_place_df['longitude'].apply(
        lambda x: float(x))
    intersect_place_df['latitude'] = intersect_place_df['latitude'].apply(
        lambda x: float(x))
    
    intersect_place_df = intersect_place_df.drop_duplicates(subset=['display_name'])

    return intersect_place_df, user_location_df
    
def get_trip_plan(intersect_place_df):
    
    distance_matrix_df = create_distance_matrix_df(intersect_place_df)

    data_model = {
        'distance_matrix': distance_matrix_df.values,
        'num_vehicles': 1,
        'depot': 0
    }

    plan_output, distance_list, total_distance = vehicle_route(data_model)

    place_list = intersect_place_df['display_name'].tolist()
    dictOfWords = {i: place_list[i] for i in range(0, len(place_list))}

    recommend_place_route = list(map(dictOfWords.get, plan_output))
    
    if len(recommend_place_route) > 2:
        return recommend_place_route, distance_list, total_distance

    return False, False, False


def distance_2point(point1, point2):
    # approximate radius of earth in km
    point_lat1 = point1['latitude']
    point_long1 = point1['longitude']
    point_lat2 = point2['latitude']
    point_long2 = point2['longitude']

    R = 6373.0
    lat1 = radians(point_lat1)
    lon1 = radians(point_long1)
    lat2 = radians(point_lat2)
    lon2 = radians(point_long2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance


def create_distance_matrix_df(place_df):

    place_df_copy = place_df.copy()
    matrix_distance_df = pd.DataFrame()

    for i in range(len(place_df)):
        distance_diff_app = []
        for j in range(len(place_df_copy)):
            distance_diff = round(distance_2point(
                place_df.iloc[i], place_df_copy.iloc[j]), 4)
            distance_diff_app.append(distance_diff)
            if(j == (len(place_df)-1)):
                matrix_distance_df2 = pd.DataFrame(
                    distance_diff_app, columns=[i])
                break
        matrix_distance_df = pd.concat(
            [matrix_distance_df, matrix_distance_df2], axis=1)

    place_list = place_df['display_name'].tolist()

    dictOfWords = { i : place_list[i] for i in range(0, len(place_list) ) }
    matrix_distance_df.rename(columns=dictOfWords,index=dictOfWords,inplace=True)

    return matrix_distance_df


def vehicle_route(data):
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        10000000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)
    if assignment:
        total_distance = 0
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            plan_output = []
            route_distance = 0
            distance_list = []
            plan_text = 'Route for vehicle {}:\n'.format(vehicle_id)
            while not routing.IsEnd(index):
                plan_text += ' {} -> '.format(manager.IndexToNode(index))
                plan_output.append(manager.IndexToNode(index))
                previous_index = index
                index = assignment.Value(routing.NextVar(index))
                distance = routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)
                route_distance += distance
                distance_list.append(distance)
            plan_output.append(manager.IndexToNode(index))
            
            plan_text += ' {}\n'.format(manager.IndexToNode(index))
            plan_text += 'Distance of the route: {}km\n'.format(route_distance)
            print(plan_text)

            total_distance += route_distance
        
        print(distance_list)
        print('Total Distance of all routes: {}km'.format(total_distance))

        return plan_output, distance_list, total_distance
