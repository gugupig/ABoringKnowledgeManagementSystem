from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTAnno, LTTextContainer
from pdftitle import get_title_from_file
import re
from datetime import datetime
import chardet
import spacy
from spacypdfreader.spacypdfreader import pdf_reader
from Utils.common_utils import detect_language

class PDFProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.language = ''
        self.set_language()

    def structured_metadata_for_paper(self):
        metadata = self.extract_pdf_metadata()
        structured_metadata = {'Author': '', 'ModDate': '', 'Keywords': '', 'Subject': ''}
        if metadata:
            for field in structured_metadata.keys():
                structured_metadata[field] = metadata.get(field, '') if field != 'ModDate' else self.convert_date(metadata.get(field, ''))
        structured_metadata['Date'] = structured_metadata.pop('ModDate')
        structured_metadata['Title'] = metadata.get('Title', '') if metadata.get('Title', '') != '' else self.get_title()
        return structured_metadata

    def convert_date(self, date_str):
        try:
            # Extract the date part from the string
            date_part = date_str[2:10]

            # Convert it to a datetime object
            date_obj = datetime.strptime(date_part, "%Y%m%d")

            # Format the date
            formatted_date = date_obj.strftime("%d-%m-%Y")
        except:
            formatted_date = date_str
            print("Warning: Date format not recognized. Use the original date string.")

        return formatted_date

    def clean_extracted_text(self, text):
        # Pattern to identify meaningless sequences and isolated characters
        pattern = r'\b[a-zA-Z0-9]\b|[\[\]\.:,;(){}<>!?\-\"\'\*%&$/\\#_=+|@^`~]'
        cleaned_text = re.sub(pattern, '', text)
        # Remove excessive newlines
        cleaned_text = re.sub(r'\n{2,}', '\n', cleaned_text)
        return cleaned_text.strip()

    def extract_text_from_pdf(self, clean=False):
        text = {}
        consecutive_pages_without_text = 0

        for page_layout in extract_pages(self.file_path):
            page_text = ''
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    page_text += element.get_text()

            cleaned_page_text = self.clean_extracted_text(page_text) if clean else page_text

            if not cleaned_page_text:
                consecutive_pages_without_text += 1
                if consecutive_pages_without_text == 10:
                    raise ValueError("PDF seems to contain only images. Please use OCR first.")
            else:
                consecutive_pages_without_text = 0

            text[page_layout.pageid] = cleaned_page_text

        return text

    def extract_first_500_from_first_page(self):
        for page_layout in extract_pages(self.file_path):
            page_text = ''
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    page_text += element.get_text()
                    if len(page_text) >= 500:
                        return page_text[:500]
            return page_text  # Return the text if it's shorter than 500 characters

    def set_language(self):
        try:
            text_sample = self.extract_first_500_from_first_page()
            self.language = detect_language(text_sample)
        except:
            self.language = 'en' #default language is english

    def extract_toc_from_pdf(self):
        toc = []
        with open(self.file_path, 'rb') as file:
            parser = PDFParser(file)
            doc = PDFDocument(parser)

            if doc.catalog.get('Outlines') is not None:
                outlines = resolve1(doc.catalog['Outlines'])
                toc = self.process_outlines(outlines)

        return toc

    def process_outlines(self, outlines, toc=[], level=0):
        if outlines:
            first_item = resolve1(outlines.get('First', None))
            while first_item:
                title = resolve1(first_item.get('Title', '')).decode('utf-8')
                page = resolve1(first_item.get('A', {})).get('D', [0])[0]
                toc.append((title, page))
                self.process_outlines(first_item, toc, level + 1)
                first_item = resolve1(first_item.get('Next', None))
        return toc

    def extract_notes_from_pdf(self):
        notes = []
        for page_layout in extract_pages(self.file_path):
            for element in page_layout:
                if isinstance(element, LTAnno):
                    notes.append(element.get_text())
        return notes

    def get_title(self):
        try:
            title = get_title_from_file(self.file_path)
        except:
            title = None
        return title

    def extract_pdf_metadata(self):
        metadata = {}
        with open(self.file_path, 'rb') as file:
            parser = PDFParser(file)
            doc = PDFDocument(parser)
            if doc.info:  # Check if metadata is available
                for key, value in doc.info[0].items():
                    if isinstance(value, bytes):
                        # Detect the character encoding of the byte string
                        encoding = chardet.detect(value)['encoding']
                        # Decode using the detected encoding
                        if encoding:
                            try:
                                metadata[key] = value.decode(encoding, errors='replace')
                            except Exception:
                                metadata[key] = value.decode('utf-8', errors='replace')
                        else:
                            metadata[key] = value.decode('utf-8', errors='replace')
                    else:
                        metadata[key] = value
        return metadata


class SpacyPdfProcessor(PDFProcessor):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.nlp = spacy.load(f'{self.language}_core_web_sm')
        self.doc = pdf_reader(self.file_path,self.nlp)
        self.first,self.last = self.doc._.page_range

    #Return a dict of sentences text on each page
    def extract_text_from_pdf(self): 
        text = {}
        for i in range(self.first,self.last+1):
            text[i] = [s.text for s in self.doc._.page(i).sents]
        return text
    
    #Return a dict of sentences generator for each page
    def extract_toc_from_pdf_generator(self):
        text = {}
        for i in range(self.first,self.last+1):
            text[i] = self.doc._.page(i).sents

    #A generator retruns all sentences text on each page
    def generate_senteces(self):
        for i in range(self.first,self.last+1):
            yield (i,[sentence.text for sentence in list(self.doc._.page(i).sents)])


    #A generator returns sentences generator for each page
    def generate_senteces_generator(self):
        for i in range(self.first,self.last+1):
            yield (i,self.doc._.page(i).sents)

    def remove_linebreaks(self):
        new_text = ""
        for token in self.doc:
            if token.text.endswith('\n'):
                # Remove the line break and do not add a space
                new_text += token.text.rstrip('\n')
            else:
                # Add token text with a following space
                new_text += token.text_with_ws

        return new_text
