# Create your views here.
from django.shortcuts import render
from .forms import DocumentForm
import pickle
from document_process_pipeline import DocumentProcessPipeline  # Import pipeline
from DocumentIndexing.Elastic.search_engine import SearchEngine
from DocumentIndexing.Embedding import embedding as embedder
import sys
sys.path.append('/root/gpt_projects/ABoringKnowledgeManagementSystem')
from config import CROSS_DOCUMENT_SEARCH_CACHE_PATH



def home(request):
    return render(request, 'homepage.html')  # or 'home.html' if extending base.html

def wip(request):
    return render(request, 'WIP_page.html')

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
        print(request.POST)
        #form = DocumentForm(request.POST, request.FILES)
        #if form.is_valid():
            # Get the selected document type
        #document_type = form.cleaned_data['document_type']
        #document_tags = form.cleaned_data['document_tags']
        document_type = request.POST.get('document_type')
        document_tags = request.POST.getlist('document_tags')
        file = request.FILES['file']
        author = request.POST.get('author',None) if request.POST.get('author') != '' else None
        title = request.POST.get('title',None) if request.POST.get('title') != '' else None
        subject = request.POST.get('subject',None) if request.POST.get('subject') != '' else None
        date = request.POST.get('date',None) if request.POST.get('date') != '' else None
        keywords = request.POST.get('Keywords',None) if request.POST.get('Keywords') != '' else None
        metadata = {'Author':author,'Title':title,'Subject':subject,'Date':date,'Keywords':keywords}
        # Process the file using document process pipeline
        pipeline = DocumentProcessPipeline()
        document_id = pipeline.document_pipeline(file, document_type,metadata = metadata,tags = document_tags)  # Adjust as needed
        # Return a JSON response instead of rendering a page
        return JsonResponse({'status': 'success', 'message': 'File uploaded successfully'}) 
        #else:
            # Return an error message if form is not valid
            #return JsonResponse({'status': 'error', 'message': 'Invalid form submission'}, status=400)

    else:
        form = DocumentForm()
        return render(request, 'document_upload.html', {'form': form})

from django.http import JsonResponse

# WIP,use for dynamically extracting and displaying the document's metadata
def file_selection_handler(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']

        return JsonResponse({'message': 'Preliminary file check done'})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def document_viewer(request):
    document_dir = os.path.join(settings.MEDIA_ROOT)  # Adjust this path if needed
    documents = os.listdir(document_dir)
    document_urls = [os.path.join(settings.MEDIA_URL, doc) for doc in documents]
    return render(request, 'document_viewer.html',{'documents': document_urls})

import os
import json
from django.conf import settings
from django.shortcuts import render

def document_viewer(request):
    # Path to your JSON file (adjust as necessary)
    json_file_path = '/root/gpt_projects/ABoringKnowledgeManagementSystem/WebApp/WebUI/static/document_list_cache/documents.json'

    # Read and parse the JSON file
    with open(json_file_path, 'r') as file:
        categories = json.load(file)

    # Convert paths to URLs
    for category, documents in categories.items():
        categories[category] = [(name, os.path.join(settings.MEDIA_URL, path)) for name, path in documents]

    return render(request, 'document_viewer.html', {'categories': categories})
from django.views.decorators.csrf import csrf_exempt
import pickle
@csrf_exempt  # Note: Better to handle CSRF properly in production
def write_pdf_viewer_cache(request):
    print('Writing to cache...')
    if request.method == 'POST':
        document_id = request.POST.get('document_id')
        index_name = request.POST.get('category')
        pickle.dump((document_id,index_name), open("/root/gpt_projects/ABoringKnowledgeManagementSystem/WebApp/WebUI/static/pdf_viewer_cache/pdf_viewer_cache.pkl", 'wb'))
        return JsonResponse({"status": "success"})


'''
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
'''



from django.http import JsonResponse

def list_pdf_files(request):
    directory_path = '/root/gpt_projects/ABoringKnowledgeManagementSystem/DocumentBank/research_paper/'
    pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]

    return JsonResponse(pdf_files, safe=False)


def search_documents(request):
    tag_form = DocumentForm()
    if request.method == 'POST':
        print('Performing search...')
        # Extract data from the POST request
        search_query = request.POST.get('searchQuery',None) if request.POST.get('searchQuery') != '' else None
        search_depth = request.POST.get('searchDepth',None) if request.POST.get('searchDepth') != '' else '_chunk_level'
        document_type = request.POST.get('documentType') + search_depth
        language = request.POST.get('language','en')
        author = request.POST.get('author',None) if request.POST.get('author') != '' else None
        title = request.POST.get('title',None) if request.POST.get('title') != '' else None
        subject = request.POST.get('subject',None) if request.POST.get('subject') != '' else None
        date = request.POST.get('date',None) if request.POST.get('date') != '' else None
        semantic_search = True if request.POST.get('semanticSearch')=='true' else False
        exact_match = True if request.POST.get('exactMatch') == 'true' else False
        keywords = request.POST.get('Keywords',None) if request.POST.get('Keywords') != '' else None
        document_tags = request.POST.getlist('document_tags') # TODO Modify the search engine to support tags
        additional_query = {key: value for key, value in zip(['Author', 'Title', 'Subject', 'Keyword'], [author, title, subject, keywords]) if value is not None}
        if search_query != None: 
            print('Search query:', search_query, 'Document type:', document_type, 'Language:', language, 'Author:', author, 'Title:', title, 'Subject:', subject, 'Date:', date, 'keywords', keywords ,'Semantic search:', semantic_search, 'Exact match:', exact_match)
            # Search the index
            search_engine = SearchEngine()
            if semantic_search:
                print('Performing semantic search...')
                vect =  embedder.embedding_listoftext([search_query],'local')[0]
                search_results = search_engine.vector_search(index_name= document_type,query_vector=vect, language = language, additional_metadata=additional_query)
            else:
                print('Performing term search...')
                search_results = search_engine.search_for_terms(index_name= document_type,word=search_query,exact_match =exact_match , language = language, additional_metadata=additional_query)
            if search_results['hits']['hits']:
                grouped_results = {}
                for hit in search_results['hits']['hits']:
                    doc_id = hit['_source']['document_id_elastic']
                    if doc_id not in grouped_results:
                        grouped_results[doc_id] = []
                    grouped_results[doc_id].append({
                        'Page_number': hit['_source']['page_number'],
                        'Text': hit['_source']['text_piece'],
                        'Metadata': hit['_source']['metadata']
                    })

                search_results = [{'document_id': doc_id, 'results': docs} for doc_id, docs in grouped_results.items()]
                result_count = sum(len(docs) for docs in grouped_results.values())
                pickle.dump(search_results, open(CROSS_DOCUMENT_SEARCH_CACHE_PATH, 'wb'))
                return JsonResponse({'results': search_results, 'resultCount': result_count})
            else:
                print('No results found')
                search_results = []
                pickle.dump(search_results, open(CROSS_DOCUMENT_SEARCH_CACHE_PATH, 'wb'))
                return JsonResponse({'results': search_results, 'resultCount': 0})
            #print(search_results) 
    # Return a JsonResponse or render a template with the search 
        else:
            search_results = []
            pickle.dump(search_results, open(CROSS_DOCUMENT_SEARCH_CACHE_PATH, 'wb'))
            return JsonResponse([])
    else:
        return render(request, 'document_search.html',{'form': tag_form})

import base64  
def byte_pdfview(request):
    with open('/root/gpt_projects/ABoringKnowledgeManagementSystem/DocumentBank/research_paper/e7fd33bc-6b64-4550-9b69-b8139487d37a.pdf', 'rb') as pdf_file:
        bytes_data = pdf_file.read()
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" style="border: none;"></iframe>'

    return render(request, 'byte_pdfview.html', {'pdf_display': pdf_display})

def chat(request):
    return render(request, 'document_chat.html')


def document_manager(request):
    return render(request, 'document_manager.html')

