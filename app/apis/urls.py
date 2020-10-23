from django.urls import path, re_path

from users import api_views as user_views
from chats import api_views as chat_views
from places import api_views as place_views
from mls import api_views as ml_views
from places.api_views import PlaceList, CategoryList, CategoryDetail, SubCategoryList, SubCategoryDetail

urlpatterns = [
    path('users/', user_views.user_list),
    path('users/create/', user_views.user_create),
    re_path(r'^users/(?P<line_user_id>U[0-9a-f]{32})', user_views.user_detail),
    path('users/check/', user_views.check),
    
    path('places/', PlaceList.as_view()),
    path('places/category/', CategoryList.as_view()),
    path('places/subcategory/', SubCategoryList.as_view()),
    path('places/category/<int:pk>/', CategoryDetail.as_view()),
    path('places/subcategory/<int:pk>/', SubCategoryDetail.as_view()),
    
    path('places/flex/action/', place_views.place_action),
    
    path('chats/logs/', chat_views.log_list),
    # re_path(r'^chats/logs/create/(?P<line_user_id>U[0-9a-f]{32})', chat_views.log_create),
    path('chats/logs/create/', chat_views.log_create),
    path('chats/intent/check/', chat_views.check_intent),
    path('chats/location/check/', chat_views.check_location),
    
    path('mls/place/recommend/', ml_views.recommend_place),
    path('mls/place/category/', ml_views.show_category),
    path('mls/place/subcategory/', ml_views.show_sub_category)
    
]