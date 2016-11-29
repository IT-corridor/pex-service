from django.http import HttpResponseRedirect


def admin_only(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated():
            if user.level == 3:
                return function(request, *args, **kwargs)
        return HttpResponseRedirect('/Admin/login/')

    wrap.__doc__=function.__doc__
    wrap.__name__=function.__name__
    return wrap


def customer_only(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated():
            if user.level == 1:
                return function(request, *args, **kwargs)
        return HttpResponseRedirect('/customer/login/')

    wrap.__doc__=function.__doc__
    wrap.__name__=function.__name__
    return wrap    
