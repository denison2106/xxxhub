import datetime

from django import template
register = template.Library()


@register.filter(name='timestamp_to_time')
def convert_timestamp_to_time(timestamp):
    import time
    return datetime.date.fromtimestamp(int(timestamp))
