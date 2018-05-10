from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve

from settings import MEDIA_ROOT

from multiplefilefield_example import views as sample_views

admin.autodiscover()

urlpatterns = [
    url(r'^$', sample_views.index),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
]
