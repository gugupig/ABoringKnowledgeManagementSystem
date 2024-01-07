from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTAnno, LTTextContainer
from pdftitle import get_title_from_file
import re

def clean_extracted_text(text):
    # Pattern to identify meaningless sequences and isolated characters
    pattern = r'\b[a-zA-Z0-9]\b|[\[\]\.:,;(){}<>!?\-\"\'\*%&$/\\#_=+|@^`~]'
    cleaned_text = re.sub(pattern, '', text)
    # Remove excessive newlines
    cleaned_text = re.sub(r'\n{2,}', '\n', cleaned_text)
    return cleaned_text.strip()

def extract_text_from_pdf(file_path):
    text = {}
    consecutive_pages_without_text = 0

    for page_layout in extract_pages(file_path):
        page_text = ''
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                page_text += element.get_text()

        cleaned_page_text = clean_extracted_text(page_text)

        if not cleaned_page_text:
            consecutive_pages_without_text += 1
            if consecutive_pages_without_text == 10:
                raise ValueError("PDF seems to contain only images. Please use OCR first.")
        else:
            consecutive_pages_without_text = 0

        text[page_layout.pageid] = cleaned_page_text

    return text





def extract_toc_from_pdf(pdf_path):
    """
    Extracts the table of contents (TOC) from a PDF file using pdfminer.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        list: A list of tuples with the title and page number of each item in the TOC.
    """
    toc = []
    with open(pdf_path, 'rb') as file:
        parser = PDFParser(file)
        doc = PDFDocument(parser)

        if doc.catalog.get('Outlines') is not None:
            outlines = resolve1(doc.catalog['Outlines'])
            toc = process_outlines(outlines)

    return toc

def process_outlines(outlines, toc=[], level=0):
    """
    Recursively processes the outlines of the PDF and extracts the TOC.
    Args:
        outlines: The outline dictionary or list from the PDF.
        toc: The current TOC being constructed (used for recursion).
        level: The current level in the TOC (used for recursion).
    Returns:
        list: A list of tuples with the title and page number of each item in the TOC.
    """
    if outlines:
        first_item = resolve1(outlines.get('First', None))
        while first_item:
            title = resolve1(first_item.get('Title', '')).decode('utf-8')
            page = resolve1(first_item.get('A', {})).get('D', [0])[0]
            toc.append((title, page))
            process_outlines(first_item, toc, level + 1)
            first_item = resolve1(first_item.get('Next', None))
    return toc



def extract_notes_from_pdf(file_path):
    """
    Extracts notes or annotations from a PDF file using pdfminer.
    Args:
        file_path (str): Path to the PDF file.
    Returns:
        list: List of notes/annotations found in the PDF.
    """
    notes = []
    for page_layout in extract_pages(file_path):
        for element in page_layout:
            if isinstance(element, LTAnno):
                notes.append(element.get_text())
    return notes

def get_title(file_path):
    try:
        title = get_title_from_file(file_path)
    except:
        title = None
    return title


import chardet

def extract_pdf_metadata(file_path):
    """
    Extracts metadata from a PDF file using pdfminer.
    Args:
        file_path (str): Path to the PDF file.
    Returns:
        dict: Metadata of the PDF, with byte strings converted to regular strings.
    """
    metadata = {}
    with open(file_path, 'rb') as file:
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







def structured_metadata_for_paper(file_path):
    metadata = extract_pdf_metadata(file_path)
    structured_metadata = {}
    target_fields = ['Author', 'ModDate', 'Keywords', 'Subject']
    if metadata:
        for field in target_fields:
            if field in metadata:
                structured_metadata[field] = metadata[field] if field != 'ModDate' else convert_date(metadata[field])
            else:
                structured_metadata[field] = ''
    if 'Title' in metadata:
        structured_metadata['Title'] = metadata['Title'] if metadata['Title'] != '' else get_title(file_path)
    return structured_metadata  

from datetime import datetime

def convert_date(date_str):
    try:
    # Extract the date part from the string
        date_part = date_str[2:10]

        # Convert it to a datetime object
        date_obj = datetime.strptime(date_part, "%Y%m%d")

        # Format the date
        formatted_date = date_obj.strftime("%d-%m-%Y")
    except:
        formatted_date = date_str
        print("Warning: Date format not recognized.Use the original date string.")

    return formatted_date










if __name__ == '__main__':
    pass