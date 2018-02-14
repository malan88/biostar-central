from django.contrib.auth.models import Group
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.conf import settings
import uuid

MAX_UID_LEN = 32
MAX_NAME_LEN = 80

def generate_uuid(limit=32):
    return str(uuid.uuid4())[:limit]


class Profile(models.Model):
    # ForeignKey runs the risk of one user having multiple profiles
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uid = models.CharField(max_length=MAX_UID_LEN, unique=True)
    name = models.CharField(max_length=MAX_NAME_LEN, default='')

    NEW, TRUSTED, SUSPENDED, BANNED = range(1,5)
    STATE_CHOICES = [(NEW, "New"), (TRUSTED, "Active"), (SUSPENDED, "Suspended"),
                     (BANNED, "Banned")]

    state = models.IntegerField(default=NEW, choices=STATE_CHOICES)

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        self.uid = self.uid or generate_uuid(8)
        super(Profile, self).save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):

    if created:
        # Create a profile for user
        Profile.objects.create(user=instance, name=instance.first_name)

