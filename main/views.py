from django.shortcuts import render, get_object_or_404
from .models import Content, XxxHub
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView
from django.contrib.sitemaps import Sitemap

import json
import re


class HomeView(ListView):
    model = XxxHub
    template_name = 'home.html'
    context_object_name = 'news'
    queryset = Content.objects.filter(status=1).order_by('-date')[:settings.RELATED_LIMIT_PAGE]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['title'] = settings.HOME_TITLE
        context['title'] = self.request.META['HTTP_HOST']
        context['network'] = ['','']
        context['cloud_tags'] = XxxHub.objects.raw(f"SELECT * FROM main_xxxhub ORDER BY RAND() LIMIT 20")
        return context

    def get_queryset(self):
        where = f"status = 1 ORDER BY date DESC"
        # return CandyModel.objects.all().filter(adult=1).order_by('-pk')
        return XxxHub.objects.raw(f"SELECT * FROM {settings.MANTICORE_DATABASE_NAME} "
                                                       f"WHERE {where} "
                                                       f"LIMIT {settings.RELATED_LIMIT_PAGE}")


class TagView(DetailView):
    model = XxxHub
    template_name = 'tag.html'
    pk_url_kwarg = 'id'
    context_object_name = 'rows'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.object.title.replace("'", "")
        options = 'OPTION ranker=sph04, max_matches=8'
        context['description'] = f''
        # context['keywords'] = ''
        context['network'] = ['https://bighole.online', 'https://x-fantasy.online', 'https://xxxrest.online',]
        context['related_rows'] = XxxHub.objects.raw(f"SELECT * FROM main_xxxhub WHERE MATCH('\"{query}\"/0.1') AND id<>{self.object.pk} AND status=1 LIMIT 8 {options}")
        context['cloud_tags'] = XxxHub.objects.raw(f"SELECT * FROM main_xxxhub WHERE id < {self.object.pk} ORDER BY id DESC LIMIT 10")
        return context


class SearchView(ListView):
    model = XxxHub
    template_name = 'home.html'
    context_object_name = 'news'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cloud_tags'] = XxxHub.objects.raw(f"SELECT * FROM main_xxxhub ORDER BY RAND() LIMIT 20")
        return context

    def get_queryset(self):
        query = re.sub('[\W+]', ' ', re.sub('\s+', ' ', str(self.kwargs['slug'])))
        query_list = query.split()
        min_query_list = query_list[:5]
        where = f"MATCH('\"{query}\"/0.3') AND status=1"
        options = f'OPTION ranker=sph04, max_matches={settings.RELATED_LIMIT_PAGE}'
        return XxxHub.objects.raw(
            f"SELECT * FROM {settings.MANTICORE_DATABASE_NAME} "
            f"WHERE {where} "
            f"LIMIT {settings.RELATED_LIMIT_PAGE} {options}")


class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        where = f"status=1 ORDER BY date DESC "
        limit = 10000
        options = f'OPTION max_matches=10000'
        return XxxHub.objects.raw(
            f"SELECT * FROM {settings.MANTICORE_DATABASE_NAME} "
            f"WHERE {where}"
            f"LIMIT {limit} {options}")

    # def lastmod(self, item):
    #     return item.datetime

    def location(self, item):
        url = f'/watch/{item.pk}/{item.title.replace(" ", "-").lower()}/'
        return url


def search_people(request):
    query = request.GET.get('q').lower().replace('_', ' ')
    query = re.sub('[\W+]', ' ', query)
    query = " ".join(query.split())
    return redirect(f'/search/{query}/', permanent=True)
