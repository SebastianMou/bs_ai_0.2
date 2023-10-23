from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from ckeditor.fields import RichTextField

# Create your models here.
class Task(models.Model):
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]
    title = models.CharField(max_length=255)
    completion_time = models.DateTimeField(null=True, blank=True)
    description = HTMLField(blank=True, null=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='NOT_STARTED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    position = models.PositiveIntegerField(default=0, blank=False, null=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return str(self.title) + ' - ' + str(self.owner)
    
class Document(models.Model):
    title = models.CharField(max_length=255)
    content = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')

    def __str__(self):
        return str(self.title) + ' - ' + str(self.owner)