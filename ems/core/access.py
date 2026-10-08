"""Department-based visibility rules shared by views, APIs and context processors."""
from core.models import Employee, Machines


def user_department(user):
    """Return the department of the employee linked to this user, or None."""
    if not user.is_authenticated:
        return None
    employee = Employee.objects.filter(user=user).select_related('department').first()
    return employee.department if employee else None


def can_view_all_machines(user):
    return user.is_authenticated and user.has_perm('core.view_all_machines')


def visible_machines(user):
    """
    Machines this user may see:
    - view_all_machines (Engineers, admin, superusers) -> every machine
    - everyone else -> only machines of their own department
    """
    machines = Machines.objects.all()
    if can_view_all_machines(user):
        return machines
    department = user_department(user)
    if department is None:
        return machines.none()
    return machines.filter(Department=department)
