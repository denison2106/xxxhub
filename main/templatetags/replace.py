import re
from itertools import groupby
from django import template

register = template.Library()


@register.filter(name='replace')
def replace(value, arg):
    """
    Replacing filter
    Use `{{ "aaa"|replace:"a|b" }}`
    """
    if len(arg.split('|')) != 2:
        return value

    what, to = arg.split('|')
    return value.replace(what, to)


@register.filter(name='replace_title')
def replace_desc(value):
    value = re.sub('[\W+]', ' ', value)
    return " ".join(value.split())


@register.filter(name='replace_keywords')
def replace_desc(value):
    value = re.sub("[\W+]", " ", value).split()
    value_x = [el for el, _ in groupby(value)]
    value_2 = ", ".join(x for x in value_x if len(x) >= 4)

    return value_2

