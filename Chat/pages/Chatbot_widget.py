

from openai import OpenAI
import streamlit as st
import os
import pickle
from rag import one_document_prompt,search_one_document,two_step_retrival_page,two_step_prompt_page
from streamlit_extras.stylable_container import stylable_container


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

st.set_page_config(page_title='Chatbot-widget', page_icon=':star', layout='wide')



with st.sidebar:
    st.markdown(f""" 
                <strong> Chatbot is in </strong>  <span style="color: red; font-weight: bold;"> {chat_bot_statut} mode </span>
                <br> 
                <strong> Current document is </strong> <br>
                <span style="color: red; font-weight: bold;"> {pdf_file_id}</span>
                """,
                unsafe_allow_html=True)

    if st.button('Reset Session'):
        st.session_state.messages = []  # Clear the chat history
        st.session_state.user_input = ''
        st.session_state.assistant_response = ''
        st.session_state.context = ''
        st.session_state.retrieved_page_nb = ''
        st.session_state.last_user_input = ''
        st.session_state.last_assistant_response = ''
        st.rerun()  # Rerun the app to reflect
    model = st.selectbox(
        'Model',
        ['gpt-3.5-turbo', 'gpt-4-1106-preview'])
    rag_number = st.slider(
    'Number of Context Texts Used',  # Title of the slider
    min_value=0,                     # Minimum value
    max_value=5,                     # Maximum value
    value=0                        # Default value
    )
    send_full_history = st.toggle("Send full chat history (WIP)", False)
    reranker = st.toggle("Use Reranker (WIP)", False)
    advanced_RAG = st.toggle("Use Advanced RAG (WIP)", False)
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
tab1, tab2 ,tab3 = st.tabs(["Chatbot","Notes","Knowleage Graph"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if 'retrieved_page_nb' not in st.session_state:
    st.session_state.retrieved_page_nb = ''
if 'context' not in st.session_state:
    st.session_state.context = ''
if 'last_user_input' not in st.session_state:
    st.session_state.last_user_input = ''
if 'last_assistant_response' not in st.session_state:    
    st.session_state.last_assistant_response = ''

        
spinner_text = 'Searching documents...' if rag_number!=0 else 'Thinking...'

  
with tab1:
    context = None  # Initialize with None to handle the case where no context is retrieved 
    retrieved_page_nb = None  # Initialize with None to handle the case where no pages are retrieved
# Handling user input and context integration
    with stylable_container(
    key="bottom_content",
    css_styles="""
        {
            position: fixed;
            bottom: 30px;
            z-index: 1;
            max-width: 100vw;
        }
        """,
        ):
        if prompt := st.chat_input("?",):
            original_prompt = prompt
            context_appended = False # Flag to indicate whether context was appended to the prompt

            # Context 
            with st.spinner(f'{spinner_text}'):
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
                    st.session_state.context = context
                    st.session_state.retrieved_page_nb = retrieved_page_nb
                if rag_number!=0 and chat_bot_statut == 'Cross Document Search':
                    pass
                if rag_number == 0 :
                    st.session_state.context = None
                    st.session_state.retrieved_page_nb = None
                st.session_state.messages.append({"role": "user", "content": original_prompt})

                full_response = ""
                    # Determine which messages to send to the API
                if send_full_history:
                    messages_to_send = st.session_state.messages
                else:
                    messages_to_send = [system_message, {"role": "user", "content": prompt}]

                    # API request to OpenAI
                
                full_response = ""
                for response in client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=messages_to_send,
                    stream=True,
                ):
                    full_response += (response.choices[0].delta.content or "")
                if retrieved_page_nb:
                    full_response += f"\n\nRetrieved pages: {', '.join(map(str, retrieved_page_nb)) if retrieved_page_nb else 'No result found.'}"
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            
    with stylable_container(
    key="top_content",
    css_styles="""
        {
            position: fixed;
            top: 150px;
            z-index: 1;
            overflow-y: auto;
            height: 70vh;
            max-width: 100vw;
            padding: 20px;
            
        }
        """,
        ):        
        for i,message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                with st.chat_message('user'):
                    st.markdown(message["content"])
            elif message["role"] == "assistant":
                with st.chat_message('assistant'):
                    st.markdown(message["content"])
                    if st.session_state.context !=None and i == len(st.session_state.messages)-1:
                        expander = st.expander(f"Retrieved Context at page {st.session_state.retrieved_page_nb}")
                        expander.write(f'{st.session_state.context}')


from SL_ReactFlow import SL_ReactFlow
import pickle
with tab3:
    label = ''

    if 'numClicks' not in st.session_state:
        st.session_state['numClicks'] = 0

    if 'lastButtonClick' not in st.session_state:
        st.session_state['lastButtonClick'] = None

    if 'canvas' not in st.session_state:
        st.session_state['canvas'] = {'nodes': [], 'edges':[]}
    
    canvas_container = st.container()
    form_container = st.container()
    
    with form_container:
        with st.form("Question",clear_on_submit=True):
            _label = st.text_input('Enter the label of the button')
            add_node = st.form_submit_button("Submit")
            load_canvas = st.form_submit_button("Load Canvas")

        if add_node:
            st.session_state['numClicks'] = st.session_state.get('numClicks', 0) + 1
            st.session_state['lastButtonClick'] = 'Add Node'
            label = _label

        if load_canvas:
            st.session_state['numClicks'] = st.session_state.get('numClicks', 0) + 1
            st.session_state['lastButtonClick'] = 'Load Canvas'
            try:
                canvas = pickle.load(open('canvas.pkl', 'rb'))
                print(canvas)
            except:
                canvas = {'nodes': [], 'edges':[]}
            if isinstance(canvas, dict) and any(value for value in canvas.values()):
                st.session_state['canvas'] = canvas
            else:
                st.write ('Canvas is empty')


    cs = {'width': '100vw', 'height': 1000}
    with canvas_container:
        canvas = SL_ReactFlow('K-MAP',
                        canvasStyle=cs,
                        label=label, 
                        numClicks=st.session_state.get('numClicks', 0), 
                        lastClickButton=st.session_state.get('lastButtonClick', None),
                        canvas = st.session_state.get('canvas', {'nodes': [], 'edges':[]}),
                        key="graph_component",
                        )

        #st.write(canvas)
        pickle.dump(canvas, open('canvas.pkl', 'wb'))

with tab2:
    st.write('Notes')
print(st.session_state.context)
print(st.session_state.retrieved_page_nb)
