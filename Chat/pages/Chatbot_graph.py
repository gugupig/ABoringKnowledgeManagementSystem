
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

col1,col2 = st.columns([1,1])
with col1:
    from streamlit_pdf_viewer import pdf_viewer
    path = '/root/gpt_projects/ABoringKnowledgeManagementSystem/DocumentBank/research_paper/6eaf87a4-e5fa-482b-8007-d978c784c8f1.pdf'
    with st.container():
        pdf_viewer(path)
with col2:
    st.chat_input("?",key="test")
 