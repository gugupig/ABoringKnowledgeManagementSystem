
# Create your views here.
from django.shortcuts import render
from .forms import DocumentForm
from document_process_pipeline import DocumentProcessPipeline  # Import pipeline



def home(request):
    return render(request, 'base.html')  # or 'home.html' if extending base.html


def document_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the selected document type
            document_type = form.cleaned_data['document_type']
            file = request.FILES['file']

            # Process the file using your pipeline
            pipeline = DocumentProcessPipeline()
            pipeline.document_pipeline(file, document_type)  # Adjust as needed

            return render(request, 'upload_success.html')
    else:
        form = DocumentForm()
    return render(request, 'upload.html', {'form': form})

def document_viewer(request):
    return render(request, 'document_viewer.html')

from django.http import FileResponse
from django.http import HttpResponseNotFound
import os

def serve_pdf(request):
    file_name = request.GET.get('file')
    base_path = '/root/gpt_projects/ABoringKnowledgeManagementSystem/DocumentBank/research_paper/'
    file_path = os.path.join(base_path, file_name)

    print("Requested file name:", file_name)  # Check the file name
    print("Attempting to serve file:", file_path)  # Check the full file path

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    else:
        
        print("File not found:", file_path)  # Log if the file is not found
        return HttpResponseNotFound('<h1>File not found</h1>')


from django.http import JsonResponse

def list_pdf_files(request):
    directory_path = '/root/gpt_projects/ABoringKnowledgeManagementSystem/DocumentBank/research_paper/'
    pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]

    return JsonResponse(pdf_files, safe=False)