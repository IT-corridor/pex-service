from django import template

register = template.Library()
def floatadd(value,arg):
    return (float(value) + float(arg))
def assign(varname,arg):
    if arg.isdigit():
        varname=float(arg)
    else:
        varname = arg
    return varname
def split(value, seperator):
    return value.split(seperator)

register.filter('floatadd', floatadd)
register.filter('assign', assign)
register.filter('split', split)