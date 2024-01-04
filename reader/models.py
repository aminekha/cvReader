from django.db import models

class Resume(models.Model):
    title = models.CharField(max_length=255, default="")
    content = models.TextField(default="")
    category = models.CharField(max_length=255, default="")