from django.urls import path
from . import views
urlpatterns = {
    path('', views.index),
    path('supermag', views.download_data_from_sm),
    path('kriging', views.kriging),
}
