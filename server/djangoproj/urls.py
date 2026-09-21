from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Django REST/API endpoints
    path('djangoapp/', include('djangoapp.urls')),

    # Existing landing page
    path('', TemplateView.as_view(template_name='Home.html')),

    # React frontend routes
    re_path(
        r'^(?:login|register|dealers(?:/.*)?|dealer(?:/.*)?|postreview(?:/.*)?)$',
        TemplateView.as_view(template_name='index.html'),
    ),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)