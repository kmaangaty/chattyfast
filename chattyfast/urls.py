from chat.views import login
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('chat/', include('chat.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # Include default auth URLs
    path('', include('chat.urls')),  # Include your app URLs
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
