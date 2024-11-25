from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from config.utils.otp_utils import send_otp_for_signal
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def create_and_send_otp(sender, instance, created, **kwargs):

    if created and instance.usertype == 'patient':
        status, message = send_otp_for_signal(instance)
        if status:
            instance.is_sent = True
            instance.save()
