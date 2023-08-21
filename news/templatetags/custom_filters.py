from django import template

register = template.Library()

censor_list = ["слово1", "слово2", "слово3", "слово4"]


@register.filter(name="censor")
def censor(value):
    if value in censor_list:
        return "***"
    return value
