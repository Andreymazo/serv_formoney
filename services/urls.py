from django.urls import path
from services.apps import ServicesConfig
from services.views import item_detail, pars_wb, get_category_from_search


app_name = ServicesConfig.name

urlpatterns = [
    path('get_category_from_search/', get_category_from_search, name='get_category_from_search'),
    path('pars_wb/<str:category>/<int:num>', pars_wb, name='pars_wb'),
    path('item_detail/<int:item_pk>', item_detail, name='item_detail'),


]