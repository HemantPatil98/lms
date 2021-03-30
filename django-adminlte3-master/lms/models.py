from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.
class notice(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    generateddate = models.DateTimeField(default=datetime.now)
    file = models.FileField(upload_to="notice/")

    def __str__(self):
        return self.title

    def addnoticein(request):
        title = request.POST['subject']
        description = request.POST['description']
        file = request.FILES['file']
        note = notice(title=title,description=description,file=file)
        note.save()

