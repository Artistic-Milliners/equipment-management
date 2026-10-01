from django.conf import settings
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Contractor_Person, Employee, MachineIssue

User = get_user_model()

@receiver(post_save, sender=User)
def create_employee(sender, instance, created, **kwargs):        
    if created:
        if instance.is_employee:
            Employee.objects.create(user=instance, name=instance.username)
        if instance.is_contractor:
            Contractor_Person.objects.create(visiting_person=instance.username)


@receiver(post_save, sender=MachineIssue)
def ticket(sender, instance, created, **kwargs):
    if created and not instance.ticket_num:
        instance.generate_ticket()
        instance.save()