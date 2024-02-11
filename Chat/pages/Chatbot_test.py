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



# Initialize session state for storing messages if not already present
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_input' not in st.session_state:
    st.session_state.user_input = ''  # Initialize user_input in session state
if 'trigger' not in st.session_state:
    st.session_state.trigger = False # Initialize trigger in session state
if 'retrieved_page_nb' not in st.session_state:
    st.session_state.retrieved_page_nb = []
if 'context' not in st.session_state:
    st.session_state.context = []

# Display existing messages
def display_messages():
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                 f"""
                :question:<span style="color: red; font-weight: bold;"> User Message:</span> \n\n{message['content']}
                """,
                unsafe_allow_html=True)
            
        elif message["role"] == "assistant":
            #st.text_area(f"Assistant Message {idx}", value=message["content"], height=75, disabled=True)
            st.markdown(
                f"""
                :robot_face:<span style="color: blue; font-weight: bold;">Bot Message:</span> \n\n{message['content']}
                """,
                unsafe_allow_html=True)

        st.markdown('###')

          
def submit():
    st.session_state.trigger = True
    st.session_state.user_input = st.session_state.widget
    st.session_state.widget = ''



tab1, tab2 = st.tabs(["Chatbot", "Knowleage Graph"])

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
        st.rerun()  # Rerun the app to reflect
    model = st.selectbox(
        'Model',
        ['gpt-3.5-turbo', 'gpt-4-1106-preview'])
    rag_number = st.slider(
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

# Prompt for the chatbot
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

#Set the GPT model
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.session_state.setdefault("openai_model", model)

#Chatbot
with tab1:
    st.text_input("Type your message here...", key="widget", on_change=submit)
    user_input = st.session_state.user_input
    original_prompt = user_input
    if user_input and st.session_state.trigger:
        st.session_state.messages.append({"role": "user", "content": st.session_state.user_input})
        print(st.session_state.trigger)
        st.session_state.trigger = False 
        retrieved_page_nb = None  # Initialize with None to handle the case where no pages are retrieved
        with st.spinner('Searching documents...'):
            if rag_number != 0 and chat_bot_statut == 'PDF VIEWER':
                rag_search_results = search_one_document(user_input, document_id=pdf_file_id, index_name=pdf_file_index, return_top_n=rag_number)
                retrieved_page_nb = [hit['Page_number'] for hit in rag_search_results] if rag_search_results else 'No result found.'
                context = one_document_prompt(rag_search_results)
                prompt = f"{context}\n Question: {user_input}"
            elif rag_option == 'Page':
                    rag_search_results = two_step_retrival_page(user_input, document_id=pdf_file_id, index_name=pdf_file_index, return_top_n=rag_number)
                    retrieved_page_nb = list(rag_search_results.keys())
                    context = two_step_prompt_page(rag_search_results)
                    prompt = f"{context}\n Question: {user_input}"
                #WIP
            elif rag_option == 'Text Piece Adjacents':
                    pass
            else:
                context = "N/A"
                retrieved_page_nb = "N/A"
                prompt = user_input    

            if send_full_history:
                messages_to_send = st.session_state.messages
            else:
                messages_to_send = [{"role": "user", "content": prompt}]

           #API Request to OpenAI
            full_response = ""
            for response in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=messages_to_send,
                stream=True,
                ):
                full_response += (response.choices[0].delta.content or "")

            if retrieved_page_nb:
                full_response += f"\n\nRetrieved pages: {', '.join(map(str, retrieved_page_nb)) if retrieved_page_nb else 'No result found.'}"
            st.session_state.messages.append({"role": "assistant", "content": full_response})  # Append assistant response
            st.session_state.context.append(context)
            st.session_state.retrieved_page_nb.append(retrieved_page_nb)
# Display messages
    with st.container():   
        display_messages()
    print(st.session_state.trigger)




with tab2:
    from SL_ReactFlow import SL_ReactFlow
    import pickle
    if 'numClicks' not in st.session_state:
        st.session_state['numClicks'] = 0

    if 'lastButtonClick' not in st.session_state:
        st.session_state['lastButtonClick'] = None

    if 'canvas' not in st.session_state:
        st.session_state['canvas'] = {'nodes': [], 'edges':[]}



    label = st.text_input('Enter the label of the button')
    if st.button('Add Node', key="Add Node"):
        st.session_state['numClicks'] = st.session_state.get('numClicks', 0) + 1
        st.session_state['lastButtonClick'] = 'Add Node'

    if st.button('Load Canvas', key="Load Canvas"):
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
    canvas = SL_ReactFlow('K-MAP',
                    canvasStyle=cs,
                    label=label, 
                    numClicks=st.session_state.get('numClicks', 0), 
                    lastClickButton=st.session_state.get('lastButtonClick', None),
                    canvas = st.session_state.get('canvas', {'nodes': [], 'edges':[]}),
                    key="graph_component",
                    )

    st.write(canvas)
    pickle.dump(canvas, open('canvas.pkl', 'wb'))

print(st.session_state.messages)
