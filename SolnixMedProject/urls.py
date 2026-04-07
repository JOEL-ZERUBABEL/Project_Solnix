
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('backend/', include('Backend.urls')),
    path('frontend/',include('Frontend.urls')),
]

