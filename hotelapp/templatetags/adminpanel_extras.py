from django import template

register = template.Library()


@register.filter(name="attr")
def attr(obj, name: str):
    if obj is None or not name:
        return ""
    return getattr(obj, name, "")

