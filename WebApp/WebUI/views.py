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


def document_upload(request):
    # Using pickle as a temporary solution to cache the project and tag options
    cache = pickle.load(open('/root/gpt_projects/ABoringKnowledgeManagementSystem/WebApp/WebUI/static/tags_and_projects_cache/tags_and_projects_cache.pkl', 'rb'))
    project_options = cache['project_options']
    tag_options = cache['tag_options']
    if request.method == 'POST':
        #print(request.POST)
        # Get the selected document data
        document_type = request.POST.get('document_type')
        file = request.FILES['file']
        author = request.POST.get('author',None) if request.POST.get('author') != '' else None
        title = request.POST.get('title',None) if request.POST.get('title') != '' else None
        subject = request.POST.get('subject',None) if request.POST.get('subject') != '' else None
        date = request.POST.get('date',None) if request.POST.get('date') != '' else None
        keywords = request.POST.get('Keywords',None) if request.POST.get('Keywords') != '' else None
        projects = json.loads(request.POST.get('projects',None)) if request.POST.get('proje cts') != '' else None
        document_tags = json.loads(request.POST.get('tags',None)) if request.POST.get('tags') != '' else None
        # Convert the JSON data to a list of values
        if projects:
            projects = [v['value'] for v in projects]
        if document_tags:
            document_tags = [v['value'] for v in document_tags]
        metadata = {'Author':author,'Title':title,'Subject':subject,'Date':date,'Keywords':keywords}
        # Process the file using document process pipeline
        pipeline = DocumentProcessPipeline()
        document_id = pipeline.document_pipeline(file, document_type,metadata = metadata,tags = document_tags,projects = projects)
        if projects:
            project_options_set = set(project_options)
            project_options_set.update(projects)
        else:
            project_options_set = project_options
        if document_tags:
            tag_options_set = set(tag_options)
            tag_options_set.update(document_tags)
        else:
            tag_options_set = tag_options
        cache['project_options'] = list(project_options_set)
        cache['tag_options'] = list(tag_options_set)
        pickle.dump(cache, open('/root/gpt_projects/ABoringKnowledgeManagementSystem/WebApp/WebUI/static/tags_and_projects_cache/tags_and_projects_cache.pkl', 'wb'))   
        # Return a JSON response instead of rendering a page
        return JsonResponse({'status': 'success', 'message': 'File uploaded successfully'}) 
    else:
        form = DocumentForm()
        return render(request, 'document_upload.html', {'form': form,'project_options': project_options,'tag_options': tag_options})

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
    cache = pickle.load(open('/root/gpt_projects/ABoringKnowledgeManagementSystem/WebApp/WebUI/static/tags_and_projects_cache/tags_and_projects_cache.pkl', 'rb'))
    project_options = cache['project_options']
    tag_options = cache['tag_options']
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
        document_tags = request.POST.get('tags',None) if request.POST.get('tags') != '' else None
        projects = request.POST.get('projects',None) if request.POST.get('projects') != '' else None
        if document_tags:
            document_tags = [v['value'] for v in json.loads(document_tags)]
        if projects:
            projects = [v['value'] for v in json.loads(projects)]
        additional_query = {key: value for key, value in zip(['Author', 'Title', 'Subject', 'Keyword'], [author, title, subject, keywords]) if value is not None}
        if search_query != None: 
            #print('Search query:', search_query, 'Document type:', document_type, 'Language:', 'Tags:',document_tags,"projects:",projects,language, 'Author:', author, 'Title:', title, 'Subject:', subject, 'Date:', date, 'keywords', keywords ,'Semantic search:', semantic_search, 'Exact match:', exact_match)
            # Search the index
            search_engine = SearchEngine()
            if semantic_search:
                print('Performing semantic search...')
                vect =  embedder.embedding_listoftext([search_query],'local')[0]
                search_results = search_engine.vector_search(index_name= document_type,query_vector=vect, language = language, tags = document_tags , projects= projects ,additional_metadata=additional_query)
            else:
                print('Performing term search...')
                search_results = search_engine.search_for_terms(index_name= document_type,word=search_query,exact_match =exact_match , language = language, tags = document_tags , projects= projects ,additional_metadata=additional_query)
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
        return render(request, 'document_search.html',{'tag_options': tag_options,'project_options': project_options})

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

