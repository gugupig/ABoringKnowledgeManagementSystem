from django.urls import path
from . import views


urlpatterns = [
    #path('', views.home, name='home'),
    path('', views.document_upload, name='document_upload'),
    
]
