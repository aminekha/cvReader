from django.contrib import admin
from django.urls import path
from reader.views import index
from django.conf import settings
from django.conf.urls.static import static
from reader.views import export_table_as_excel

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('export-excel/', export_table_as_excel, name='export_excel'),
]
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)