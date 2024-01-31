from langchain.text_splitter import RecursiveCharacterTextSplitter
from .embedding_toolkits import token_length_calculator
from config import TEXT_SPLIT_SIZE
from langchain.text_splitter import SentenceTransformersTokenTextSplitter
   

class TextSplitter_SentenceTransformers:
    def __init__(self, model_name="sentence-transformers/distiluse-base-multilingual-cased-v2",overlap = 25):
        self.splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=overlap, model_name=model_name)

    def split_text(self,text):
        return self.remove_special_tokens(self.splitter.split_text(text))
    
    def split_text_generator(self,text):
        for chunk in self.splitter.split_text(text):
            yield chunk

    def remove_special_tokens(self,text_list):
        special_tokens = ["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"]  # special tokens to remove
        filtered_texts = []

        for text in text_list:
            for token in special_tokens:
                text = text.replace(token, "")
            filtered_texts.append(text.strip())

        return filtered_texts


class TextSplitter_Recursive:
    def __init__(self,overlap = 25):
        self.token_length_calculator = token_length_calculator()
        self.token_length = self.token_length_calculator.token_length
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=TEXT_SPLIT_SIZE, chunk_overlap=overlap, length_function=self.token_length)
    
    def get_separators_for_language(self,language_code):
        if language_code == "zh":
            return ['。', '；', '？', '！', ' ']
        elif language_code in ["en", "fr"]:
            return ['.', '?', '!', ';', ':', ' ']
        else:
            return ['.', '?', '!', ';', ':', ' ']
        
    def split_text(self,text,max_length=TEXT_SPLIT_SIZE, language_code="en"):
        try:
            separators = self.get_separators_for_language(language_code)

            if self.token_length(text) <= max_length:
                return [text]
            else:
                return self.splitter.split_text(text)
        except Exception as e:
            print(f"An error occurred while splitting text: {e}")
            return [text]  # Return the original text as a single chunk in case of an error

class TextSplitter_Spacy:
    def __init__(self):
        self.token_length_calculator = token_length_calculator()

    #Here sentence is generator of spacy sentence
    def chunk_sentences_with_sentence_overlap_generator(self,sentences, max_tokens=TEXT_SPLIT_SIZE, overlap=1,cleanned = True):
        chunks = []
        current_chunk = []
        current_token_count = 0
        overlap_sentences = []

        for sentence in sentences:
            token_count = self.token_length_calculator.token_length(sentence.text)

            if current_token_count + token_count > max_tokens:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                # Start new chunk with overlap from previous chunk
                current_chunk = overlap_sentences + [sentence.text]
                current_token_count = len(' '.join(current_chunk).split())
                # Prepare overlap sentences for next chunk
                overlap_sentences = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk[:]
            else:
                current_chunk.append(sentence.text)
                current_token_count += token_count
                if len(current_chunk) > overlap:
                    overlap_sentences = current_chunk[-overlap:]

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return [chunk.replace('\n', '') for chunk in chunks] if cleanned else chunks

    #Take a list of sentences and return a list of chunks
    def chunk_sentences_with_sentence_overlap(self,sentences:list, max_tokens=TEXT_SPLIT_SIZE, overlap=1,cleanned = True):
        chunks = []
        current_chunk = []
        current_token_count = 0
        overlap_sentences = []

        for sentence in sentences:
            token_count = self.token_length_calculator.token_length(sentence)

            if current_token_count + token_count > max_tokens:
                if current_chunk:  # Ensure current chunk is not empty
                    chunks.append(' '.join(current_chunk))
                # Start new chunk with overlap from previous chunk
                current_chunk = overlap_sentences + [sentence]
                current_token_count = len(' '.join(current_chunk).split())
                # Update overlap sentences
                overlap_sentences = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk[:]
            else:
                # Add the sentence to the current chunk
                current_chunk.append(sentence)
                current_token_count += token_count
                # Update overlap sentences
                if len(current_chunk) > overlap:
                    overlap_sentences = current_chunk[-overlap:]

        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return [chunk.replace('\n', '') for chunk in chunks] if cleanned else chunks



