from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class videos_watched_status(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.TextField(max_length=15)
    watched = models.TextField(max_length=50)

    def __str__(self):
        return self.user