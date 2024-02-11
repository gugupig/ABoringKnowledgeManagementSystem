from django.urls import path
from . import views


urlpatterns = [
    #path('', views.home, name='home'),
    path('', views.home, name='document_upload'),
    path('document_upload/', views.document_upload, name='document_upload'),
    path('document_viewer/', views.document_viewer, name='document_viewer'),
    path('list_pdf_files/', views.list_pdf_files, name='list_pdf_files'),
    path('search/', views.search_documents, name='search'),
    path('chat/', views.chat, name='chat'),
    path('document_manager/', views.document_manager, name='document_manager'),
    path('write_pdf_viewer_cache/', views.write_pdf_viewer_cache, name='write_article_name'),
    path('wip/', views.wip, name='wip'),
    ]
    

from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
