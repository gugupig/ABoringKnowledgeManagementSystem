
from pdf_processing.pdf_processor import (
    extract_text_from_pdf, 
    extract_toc_from_pdf, 
    extract_notes_from_pdf, 
    extract_pdf_metadata
)
from DocumentProcessing.docx_processing.docx_processor import (
    extract_text_from_docx, 
    extract_word_metadata
)
from txt_processing.txt_processor import extract_text_from_txt
import os

class DocumentProcessor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filetype = self.check_file_type()
        self.support_file_type = {'.pdf' : 'pdf','.docx': 'docx','.txt':'txt'}

    def check_file_type(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        return file_extension

    def process_document(self):
        if self.filetype == 'pdf':
            return self.process_pdf()
        elif self.filetype == 'docx':
            return self.process_docx()
        elif self.filetype == 'txt':
            return self.process_txt()
        else:
            raise ValueError("Unsupported file type")

    def process_pdf(self,extract_toc = False,extract_notes = False):
        text = extract_text_from_pdf(self.filepath)
        metadata = extract_pdf_metadata(self.filepath)
        toc = {}
        notes ={}
        if extract_toc:
            toc = extract_toc_from_pdf(self.filepath)
        if extract_notes:
            notes = extract_notes_from_pdf(self.filepath)
        return {"text": text, "toc": toc, "notes": notes, "metadata": metadata}

    def process_docx(self):
        text = extract_text_from_docx(self.filepath)
        metadata = extract_word_metadata(self.filepath)
        return {"text": text, "metadata": metadata}

    def process_txt(self):
        text = extract_text_from_txt(self.filepath)
        return {"text": text}

