from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def role_required(required_role):

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('core:login')  # Redirect to login if the user is not authenticated
            if request.user.role != required_role:
                return HttpResponseForbidden("You do not have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def admin_required(view_func):

    return role_required('admin')(view_func)

def sales_rep_required(view_func):

    return role_required('sales_rep')(view_func)

def customer_required(view_func):

    return role_required('customer')(view_func)

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:login')
        if request.user.role not in ['admin', 'sales_rep']:
            return HttpResponseForbidden("You do not have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view