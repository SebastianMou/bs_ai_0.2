from django.contrib import admin
from .models import Task, Document

# Register your models here.
admin.site.register(Task)
admin.site.register(Document)