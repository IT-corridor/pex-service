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
    datalist = value.split(seperator)
    i=0
    items=[]
    data=''
    val =''
    for item in datalist:
        val = data+str(i) 
        val = item
        i = i+1
        items.append(val)
    return items
    
        
register.filter('floatadd', floatadd)
register.filter('assign', assign)
register.filter('split', split)