from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Poll(models.Model):
    question = models.TextField()
    total_votes = models.IntegerField(default=0)
    all_options = models.BooleanField(default=False)
    anyone_options = models.BooleanField(default=False)
    protect = models.BooleanField(default=False)
    expires_in = models.IntegerField(null=True) 

    user = models.ForeignKey(User,related_name='polls',on_delete=models.CASCADE)


class Option(models.Model):
    answer = models.TextField()
    votes = models.IntegerField(default=0)
    is_all = models.BooleanField(default=False)
    is_any = models.BooleanField(default=False)
    poll = models.ForeignKey(Poll,related_name='options',on_delete=models.CASCADE)

class ControlField(models.Model):
    control_field = models.CharField(max_length=255,default='None')
    option = models.ForeignKey(Option,related_name='controllers',on_delete=models.CASCADE,null=True)

class PollToken(models.Model):
    token = models.CharField(max_length=255,default='none')
    time = models.DateTimeField(default=timezone.now)
    poll = models.OneToOneField(Poll,on_delete=models.SET_NULL,null=True,related_name='token')



    



