from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import index as home  # use index as root view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('api/', include('accounts.urls')),  # All product/user routes
    path('', home),  # Default homepage
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
