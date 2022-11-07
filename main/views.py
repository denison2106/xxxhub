from django.shortcuts import render, get_object_or_404
from .models import Content, XxxHub
from django.conf import settings
from django.views.generic import ListView, DetailView

import json
import re


class HomeView(ListView):
    model = Content
    template_name = 'home.html'
    context_object_name = 'news'
    queryset = Content.objects.filter(status=1).order_by('-date')[:20]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cloud_tags'] = XxxHub.objects.raw(f"SELECT * FROM main_xxxhub ORDER BY RAND() LIMIT 20")
        return context


class TagView(DetailView):
    model = Content
    template_name = 'tag.html'
    pk_url_kwarg = 'id'
    context_object_name = 'rows'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_rows'] = XxxHub.objects.raw(f"SELECT * FROM main_xxxhub WHERE MATCH('\"{self.object.title}\"/0.1') AND id<>{self.object.pk} AND status=1 LIMIT 5")
        context['cloud_tags'] = XxxHub.objects.raw(f"SELECT * FROM main_xxxhub WHERE id < {self.object.pk} ORDER BY id DESC LIMIT 10")
        return context


def tag_view(request, pk, slug):
    row = get_object_or_404(Content, pk=pk)
    where = f"status = 1 ORDER BY RAND()"
    related = XxxHub.objects.raw(f"SELECT * FROM main_xxxhub LIMIT 10")

    # query_list = re.sub('[\W+]', ' ', re.sub('\s+', ' ', row.title)).split()
    # min_query_list = query_list[:5]
    # query = '|'.join(x for x in min_query_list if len(x) >= 2)


    context = {
        'rows': row,
        'related_rows': related,
    }
    return render(request, 'tag.html', context=context)

# class TagView(DetailView):
#     model = Content
#     template_name = 'tag.html'
#     pk_url_kwarg = 'id'
#     context_object_name = 'rows'
