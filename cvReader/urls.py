from django.contrib import admin
from django.urls import path
from reader.views import index
from django.conf import settings
from django.conf.urls.static import static
from reader.views import export_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('export/', export_data, name='export_data'),
]
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)