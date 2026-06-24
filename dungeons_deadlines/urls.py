from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('django.contrib.auth.urls')),
    path('', include('core.urls')),
]

handler400 = 'core.views.bad_request'
handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
