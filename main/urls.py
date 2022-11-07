from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('watch/<int:id>/<str:title>/', TagView.as_view(), name='tag'),
]
