'''
import streamlit as st
from DocumentIndexing.Elastic import search_engine 
from DocumentIndexing.Embedding.embedding_local import embeddings_multilingual as embed

search_engine = search_engine.SearchEngine()
vector_search = search_engine.vector_search

st.title("RAG Chat Interface")

# Text input for user query
user_query = st.text_input("Your question:")

# Button to send the query
if st.button("Send"):
    if user_query:
        # Embed the query using your function
        embedded_query = embed(user_query)[0]

        # Search in Elasticsearch and perform RAG
        response = vector_search(es, embedded_query)

        # Display the response
        st.text_area("Response:", value=response, height=100)
    else:
        st.error("Please enter a question.")
'''
# .streamlit/secrets.toml

import streamlit as st
from openai import OpenAI


from openai import OpenAI
import streamlit as st

st.title("ChatGPT-like clone")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.session_state["openai_model"] = "gpt-4-1106-preview"

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})