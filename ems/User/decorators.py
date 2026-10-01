"""
Custom decorators for view access control
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


def inventory_controller_restricted(view_func):
    """
    Decorator to prevent Inventory Controller users from accessing non-inventory views.
    Redirects them to the spares page with a message.
    
    Usage:
        @inventory_controller_restricted
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            # Check if user is ONLY in Inventory Controller group
            user_groups = request.user.groups.values_list('name', flat=True)
            if 'Inventory Controller' in user_groups:
                # Redirect to spares page
                messages.warning(
                    request, 
                    'You only have access to the Inventory Management section.'
                )
                return redirect('User:spares')
        
        # User is not restricted, proceed normally
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_inventory_controller(view_func):
    """
    Decorator to ensure only Inventory Controller users can access a view.
    
    Usage:
        @require_inventory_controller
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name='Inventory Controller').exists():
                return view_func(request, *args, **kwargs)
        
        # User is not in Inventory Controller group
        messages.error(request, 'Access denied. Inventory Controller access required.')
        return redirect('User:home')
    
    return wrapper

