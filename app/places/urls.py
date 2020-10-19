from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('province/', views.province, name='province'),
    path('poss/', views.possible_word, name='poss'),
]