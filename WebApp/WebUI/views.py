
# Create your views here.
from django.shortcuts import render
from .forms import DocumentForm
from document_process_pipeline import DocumentProcessPipeline  # Import your pipeline



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

            return render(request, 'WebUI/upload_success.html')
    else:
        form = DocumentForm()
    return render(request, 'upload.html', {'form': form})
