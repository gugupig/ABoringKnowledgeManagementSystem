
from openai import OpenAI
import streamlit as st
import os
import pickle
from rag import one_document_prompt,search_one_document,two_step_retrival_page,two_step_prompt_page



CHAT_BOT_STATUT_CACHE_PATH = "/root/gpt_projects/ABoringKnowledgeManagementSystem/WebApp/WebUI/static/chat_bot_statut_cache/chat_bot_statut_cache.pkl"
PDF_VIEWER_CACHE_PATH = "/root/gpt_projects/ABoringKnowledgeManagementSystem/WebApp/WebUI/static/pdf_viewer_cache/pdf_viewer_cache.pkl"
CROSS_DOCUMENT_SEARCH_CACHE_PATH = "/root/gpt_projects/ABoringKnowledgeManagementSystem/WebApp/WebUI/static/cross_document_search_cache/cross_document_search_cache.pkl"
os.environ['PYTHONPATH'] = f"{os.environ.get('PYTHONPATH')}:/root/gpt_projects/ABoringKnowledgeManagementSystem/"
chat_bot_statut = pickle.load(open(CHAT_BOT_STATUT_CACHE_PATH, 'rb'))
pdf_file = pickle.load(open(PDF_VIEWER_CACHE_PATH, 'rb'))
pdf_file_id = pdf_file[0]
pdf_file_index = pdf_file[1]+"_chunk_level"
chat_bot_statut_text = f" {chat_bot_statut} Mode"
if chat_bot_statut == 'PDF VIEWER':
    pdf_file_text = f"Chat bot is on the document : {pdf_file_id} "
else:
    pdf_file_text = ''
corss_document_search_results = pickle.load(open(CROSS_DOCUMENT_SEARCH_CACHE_PATH, 'rb'))

# Combined markdown string
markdown_string_combined = f"""
<style>
.fixed-header {{
    background-color: #ffffff;
    padding: 10px 0;
    position: fixed;
    top: 6px;
    width: 100%;
    z-index: 2;
}}

/* Adjust the .streamlit-container margin-top value to be slightly greater than the header's total height */
#root > div:nth-child(1) > div > div > div > div > section > div {{padding-top: 0rem;}}
</style>
<div class="fixed-header">
    <h1 style="margin-left: 40px;">{chat_bot_statut_text}</h1>
    <h5 style="margin-left: 40px;">{pdf_file_text}</h5>
</div>
"""

# Render the combined markdown
st.markdown(markdown_string_combined, unsafe_allow_html=True)
for i in range(3):
    st.markdown('---')

with st.sidebar:
    if st.button('Reset Session'):
        st.session_state.messages = []  # Clear the chat history
        st.rerun()  # Rerun the app to reflect 
    #rag_toggle = st.toggle("Using RAG", False)
    model = st.selectbox(
        'Model',
        ['gpt-3.5-turbo', 'gpt-4-1106-preview'])
    rag_number = st.sidebar.slider(
    'Number of Context Texts Used',  # Title of the slider
    min_value=0,                     # Minimum value
    max_value=10,                     # Maximum value
    value=0                        # Default value
    )
    send_full_history = st.toggle("Send full chat history (WIP)", False)
    reranker = st.toggle("Use Reranker (WIP)", False)
    advanced_RAG = st.toggle("Use Advanced RAG (WIP)", False)
    graph_tool = st.toggle("Show Graph tool (WIP)", False)
    rag_option = st.selectbox(
        'RAG Strategy',
        ['Single Text piece', 'Page', 'Text Piece Adjacents'])
    if rag_option == 'Text Piece Adjacents':
        text_pice_adjacents_windows = st.slider(
        'Number of Text Piece Adjacents',  # Title of the slider
        min_value=1,                     # Minimum value
        max_value=3,                     # Maximum value
        value=1                        # Default value
        )
    if chat_bot_statut != 'PDF VIEWER':
        dt_option = st.selectbox(
            'What type of document do you want to search?',
            ['research_paper', 'research_book', 'personal_document', 'others'])
        lang_option = st.selectbox(
                'What language do you want to search?',
            ['en','fr','cn'])
        title = st.text_input('Title', placeholder = 'Enter the title of the document') 
        author = st.text_input('Author',placeholder= 'Enter the author of the document')
        subject = st.text_input('Subject',placeholder= 'Enter the subject of the document')

# Existing setup code
system_message = {'role':"system","content":"""
                    You are a chatbot to help users to search documents, summarize documents, and answer questions about documents.
                    Be precise and do not hallucinate."""}
if chat_bot_statut == 'PDF VIEWER' and pdf_file and rag_number!=0:
    system_message = {'role':"system","content":f"""
                    You are a chatbot to help users to search documents, summarize documents, and answer questions about documents.
                    you will be provided with {rag_number} context text pieces from the document,based on the context to answer the question.
                    If neccesary,you can use your own knowledge with the context text pieces to answer the question,but be precise and do not hallucinate.
                    when your knowledge is conflicting with the context text pieces, use the context text pieces to answer the question."""}
elif chat_bot_statut == 'Cross Document Search' and rag_number!=0:
    system_message = {'role':"system","content":f""" 
                    You are a chatbot to help users to search documents, summarize documents, and answer questions about documents.
                    you will be provided with {rag_number} context text pieces from the documents,based on the context to answer the question.
                    If neccesary,you can use your own knowledge with the context text pieces to answer the question,but be precise and do not hallucinate.
                    when your knowledge is conflicting with the context text pieces, use the context text pieces to answer the question."""}
        

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.session_state.setdefault("openai_model", model)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
from SL_ReactFlow import SL_ReactFlow
import pickle
if graph_tool:
    if 'numClicks' not in st.session_state:
        st.session_state['numClicks'] = 0

    if 'lastButtonClick' not in st.session_state:
        st.session_state['lastButtonClick'] = None

    if 'canvas' not in st.session_state:
        st.session_state['canvas'] = {'nodes': [], 'edges':[]}

    if 'last_canvas' not in st.session_state: 
        st.session_state['last_canvas'] = {'nodes': [], 'edges':[]}

    canvas_cahche = st.session_state.get('last_canvas', {'nodes': [], 'edges':[]})
    label = st.text_input('Enter the label of the button')
    if st.button('Add Node', key="Add Node"):
        st.session_state['numClicks'] = st.session_state.get('numClicks', 0) + 1
        st.session_state['lastButtonClick'] = 'Add Node'

    if st.button('Load Canvas', key="Load Canvas"):
        st.session_state['numClicks'] = st.session_state.get('numClicks', 0) + 1
        st.session_state['lastButtonClick'] = 'Load Canvas'
        canvas_cahche = st.session_state.get('canvas', {'nodes': [], 'edges':[]})



    cs = {'width': '100vw', 'height': 1000}
    canvas = SL_ReactFlow('K-MAP',
                    canvasStyle=cs,
                    label=label, 
                    numClicks=st.session_state.get('numClicks', 0), 
                    lastClickButton=st.session_state.get('lastButtonClick', None),
                    canvas = canvas_cahche,
                    key="graph_component",
                    )
    if isinstance(canvas, dict) and any(value for value in canvas.values()):
        st.session_state['canvas'] = canvas_cahche



# Handling user input and context integration
if prompt := st.chat_input("?"):
    original_prompt = prompt
    context_appended = False # Flag to indicate whether context was appended to the prompt
    retrieved_page_nb = None  # Initialize with None to handle the case where no pages are retrieved
    # Context 
    with st.spinner('Searching documents...'):
        if rag_number!=0 and chat_bot_statut == 'PDF VIEWER':
            if pdf_file:
                context_appended = True
                if rag_option == 'Single Text piece':
                    rag_search_results = search_one_document(prompt, document_id=pdf_file_id, index_name=pdf_file_index, return_top_n=rag_number)
                    retrieved_page_nb = [hit['Page_number'] for hit in rag_search_results] if rag_search_results else 'No result found.'
                    context = one_document_prompt(rag_search_results)
                    prompt = f"{context}\n Question: {prompt}"
                elif rag_option == 'Page':
                    rag_search_results = two_step_retrival_page(prompt, document_id=pdf_file_id, index_name=pdf_file_index, return_top_n=rag_number)
                    retrieved_page_nb = list(rag_search_results.keys())
                    context = two_step_prompt_page(rag_search_results)
                    prompt = f"{context}\n Question: {prompt}"
                #WIP
                elif rag_option == 'Text Piece Adjacents':
                    pass
        if rag_number!=0 and chat_bot_statut == 'Cross Document Search':
            pass

                
    # Append the user's input (with context if added) to the session state
    st.session_state.messages.append({"role": "user", "content": original_prompt})

    with st.chat_message("user"):
        st.markdown(original_prompt)
    
    

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Determine which messages to send to the API
        if send_full_history:
            messages_to_send = st.session_state.messages
        else:
            messages_to_send = [system_message, {"role": "user", "content": prompt}]

        # API request to OpenAI
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=messages_to_send,
            stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        if retrieved_page_nb:
                full_response += f"\nRetrieved pages: {retrieved_page_nb}"
        message_placeholder.markdown(full_response)
  

    # Append the assistant's response to the session state
    if context_appended:
        # Use the prompt with context for the API call
        # But store the original prompt for the user's message
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        # If no context was appended, use the original prompt as is
        st.session_state.messages.append({"role": "user", "content": original_prompt})
 
    


