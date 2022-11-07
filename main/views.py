from django.shortcuts import render, get_object_or_404
from .models import Content, XxxHub
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView

import json
import re


class HomeView(ListView):
    model = XxxHub
    template_name = 'home.html'
    context_object_name = 'news'
    queryset = Content.objects.filter(status=1).order_by('-date')[:settings.RELATED_LIMIT_PAGE]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cloud_tags'] = XxxHub.objects.raw(f"SELECT * FROM main_xxxhub ORDER BY RAND() LIMIT 20")
        return context

    def get_queryset(self):
        where = f"status = 1 ORDER BY id DESC"
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
        options = 'OPTION ranker=sph04, max_matches=5'
        context['related_rows'] = XxxHub.objects.raw(f"SELECT * FROM main_xxxhub WHERE MATCH('\"{self.object.title}\"/0.1') AND id<>{self.object.pk} AND status=1 LIMIT 5 {options}")
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


def search_people(request):
    query = request.GET.get('q').lower().replace('_', ' ')
    query = re.sub('[\W+]', ' ', query)
    query = " ".join(query.split())
    return redirect(f'/search/{query}/', permanent=True)
