from django.urls import path
from . import views


urlpatterns = [
    #path('', views.home, name='home'),
    path('', views.home, name='document_upload'),
    path('document_upload/', views.document_upload, name='document_upload'),
    path('document_viewer/', views.document_viewer, name='document_viewer'),
    path('serve_pdf/', views.serve_pdf, name='serve_pdf'),
    path('list_pdf_files/', views.list_pdf_files, name='list_pdf_files'),
    path('search/', views.search_documents, name='search')
]
