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
def assignval(record):
    row_count = 0 
    for row in record:
        row_count = row_count+1
    return row_count
def split(value, seperator):
    datalist = value.split(seperator)
    return datalist

def lookup(var,key):
    return var[key]

def increament(val):
    return val+1;

def lower(value):
    #print "test",value.lower()
    return value.lower()
def divisition(value):
    return float(value)/1000

register.filter('divisition', divisition)
register.filter('lower', lower)     
register.filter('increament', increament)            
register.filter('lookup', lookup)        
register.filter('floatadd', floatadd)
register.filter('assign', assign)
register.filter('split', split)
register.filter('assignval', assignval)

@register.filter(name='slug')
def slug(value):
    return value.split("(")[0].strip().lower().replace(' ','-')

@register.filter(name='brief_name')
def brief_name(value):
    return value.split("(")[0].strip()