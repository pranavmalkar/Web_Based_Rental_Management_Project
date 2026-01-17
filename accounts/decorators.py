from django.core.exceptions import PermissionDenied

def owner_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_owner():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped

def traveller_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_traveller():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped
