import re
from django import template

register = template.Library()


@register.filter(name='img_token')
def img_token(value):
    # https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQp_dDL_1ULzFbIfasHNjjELx6BMsZsACSEmAnRz_MlZ2FX168&s
    token = re.search('tbn:(.+)', value).group(1)
    return token

