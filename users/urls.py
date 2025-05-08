from django.urls import path
from . import views
from . import zoom_controller

urlpatterns = [
    path('zoom/authorize/', zoom_controller.zoom_authorize, name='zoom_authorize'),
    path('zoom/callback/', zoom_controller.zoom_callback, name='zoom_callback'),
    path('zoom/create-meeting/', zoom_controller.create_zoom_meeting, name='create_zoom_meeting'),
]