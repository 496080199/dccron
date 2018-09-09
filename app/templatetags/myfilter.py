from django import template
register = template.Library()

@register.filter
def getrun(obj):
    return obj.getrun()

@register.filter
def getnextruntime(obj):
    return obj.getnextruntime()
