from django.contrib.sitemaps.views import sitemap
from django.urls import path
from .views import *
from . import views

sitemaps = {
    'posts': PostSitemap,
}

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('watch/<int:id>/<str:title>/', TagView.as_view(), name='tag'),
    path('search/<str:slug>/', SearchView.as_view(), name='search'),
    path('q/', search_people, name='search_people'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
]
