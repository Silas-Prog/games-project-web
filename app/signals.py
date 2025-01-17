from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import User_Game
from random import randint

@receiver(post_save, sender=User)
def my_handler(sender, instance, created, **kwargs):
    if created:
        user = User.objects.filter().last()
        if not User_Game.objects.filter(user=user.id).exists():
            User_Game.objects.create(user=User.objects.get(id=user.id) , code=randint(100000,999999))
    else:
        print("User has been updated!")
