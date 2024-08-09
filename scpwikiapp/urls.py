# urls.py

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
path('', views.login, name='login'),
path('signup/', views.signup, name='signup'),
path('home/', views.start_chat_session, name='start'),
#path('chat/<int:id>/', views.)

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)