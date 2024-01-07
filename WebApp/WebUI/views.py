
# Create your views here.
from django.shortcuts import render
from .forms import DocumentForm
from document_process_pipeline import DocumentProcessPipeline  # Import pipeline
from DocumentIndexing.Elastic.search_engine import SearchEngine
from DocumentIndexing.Embedding.embedding_local import embeddings_multilingual



def home(request):
    return render(request, 'homepage.html')  # or 'home.html' if extending base.html


def document_upload_old(request):
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

def document_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the selected document type
            document_type = form.cleaned_data['document_type']
            file = request.FILES['file']

            # Process the file using document process pipeline
            pipeline = DocumentProcessPipeline()
            pipeline.document_pipeline(file, document_type)  # Adjust as needed

            # Return a JSON response instead of rendering a page
            return JsonResponse({'status': 'success', 'message': 'File uploaded successfully'})
        else:
            # Return an error message if form is not valid
            return JsonResponse({'status': 'error', 'message': 'Invalid form submission'}, status=400)

    else:
        form = DocumentForm()
        return render(request, 'document_upload.html', {'form': form})

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



def search_documents(request):
    if request.method == 'POST':
        print('Performing search...')
        # Extract data from the POST request
        search_query = request.POST.get('searchQuery',None)
        document_type = request.POST.get('documentType')
        language = request.POST.get('language','en')
        author = request.POST.get('author') if request.POST.get('author') != '' else None
        title = request.POST.get('title',None) if request.POST.get('title') != '' else None
        subject = request.POST.get('subject',None) if request.POST.get('subject') != '' else None
        date = request.POST.get('date',None) if request.POST.get('date') != '' else None
        semantic_search = True if request.POST.get('semanticSearch')=='true' else False
        exact_match = True if request.POST.get('exactMatch') == 'true' else False
        additional_query = {}
        for key,value in zip(['Author','Title','Subject',],[author,title,subject]):
            if value != None:
                additional_query[key] = value
        if search_query != None: 
            print('Search query:', search_query, 'Document type:', document_type, 'Language:', language, 'Author:', author, 'Title:', title, 'Subject:', subject, 'Date:', date, 'Semantic search:', semantic_search, 'Exact match:', exact_match)
            # Search the index
            search_engine = SearchEngine()
            if semantic_search:
                print('Performing semantic search...')
                vect = embeddings_multilingual(search_query)
                search_results = search_engine.vector_search(index_name= document_type,query_vector=vect, language = language, additional_metadata=additional_query)
            else:
                print('Performing term search...')
                search_results = search_engine.search_for_terms(index_name= document_type,word=search_query,exact_match =exact_match , language = language, additional_metadata=additional_query)
            if search_results['hits']['hits']:
                result_count = len(search_results['hits']['hits'])
                search_results = [{'Page_number': hit['_source']['original_page_number'], 'Text': hit['_source']['text_piece'], 'Metadata': hit['_source']['metadata']} for hit in search_results['hits']['hits']]
            else:
                search_results = [{'Page_number': 'No results found', 'Text': 'No results found', 'Metadata': 'No results found'}]
            print(search_results) 
    # Return a JsonResponse or render a template with the search 
 
        return JsonResponse({'results': search_results, 'resultCount': result_count})
    else:
        return render(request, 'document_search.html')
    
    #return JsonResponse({'results': 'Search results here'})

