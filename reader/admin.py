from django.contrib import admin
from .models import Resume

class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'category')

admin.site.register(Resume, ResumeAdmin)