from langchain.text_splitter import RecursiveCharacterTextSplitter
from .embedding_toolkits import w2v_token_len

def split_text_with_langchain(text, max_length = 512,length_function = w2v_token_len):
    if length_function(text) <= max_length:
        return [text]
    else:
        splitter = RecursiveCharacterTextSplitter(chunk_size=max_length, chunk_overlap=0,length_function=length_function,separators=['。','；','？','！',' ',''])
        return splitter.split_text(text)


