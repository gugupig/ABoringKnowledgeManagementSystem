# paper_extraction.py

import pdfplumber

import re
from typing import Optional





def extract_publication_date(first_page: pdfplumber.page.Page) -> Optional[str]:
    """
    Extracts the publication date from the left margin of the first page of a PDF.
    The date is assumed to be vertical and in the format "DD MMM YYYY".
    """
    vertical_texts = first_page.extract_words(keep_blank_chars=True, x_tolerance=1, y_tolerance=1)
    vertical_text = " ".join([word['text'] for word in vertical_texts if word['upright'] == False])

    # Regular expression to match the date format in both normal and reversed order
    date_pattern = r'\b(\d{2} \w{3} 20\d{2}|\d{2}02 \w{3} \d{2})\b'
    date_match = re.search(date_pattern, vertical_text)

    if date_match:
        date_str = date_match.group(0)
        return date_str[::-1]

    return None











def extract_text_from_pdf(file_path, extract_title=True, extract_authors=True, extract_abstract=True, extract_references=True, extract_pub_date=True):
    """
    Extracts text from a PDF file along with optional extraction of title, authors, abstract, and references.
    """
    text = {}
    title = "Extraction Error"
    authors = "Extraction Error"
    abstract = "Extraction Error"
    references_text = "Extraction Error"
    publication_date = "Extraction Error"
    with pdfplumber.open(file_path) as pdf:
        # Extracting text from the first page
        first_page_text = pdf.pages[0].extract_text()
        if first_page_text:
            lines = first_page_text.split('\n')
            if extract_pub_date:
                # Extracting publication date
                publication_date = extract_publication_date(pdf.pages[0])
                if publication_date:
                    publication_date = publication_date.strip()
                else:
                    publication_date = "Publication Date Extraction Error or No Date Found"
            if extract_title:
                # Extracting title
                title_candidate = []
                for line in lines:
                    if "@" in line or "†" in line or "‡" in line or "*" in line or "Abstract" in line:
                        break
                    title_candidate.append(line.strip())
                if title_candidate:
                    title = ' '.join(title_candidate)
                else:
                    title = "Title Extraction Error or No Title Found"

            if extract_authors:
                # Extracting authors
                author_endocument_idx = next((i for i, line in enumerate(lines) if 'Abstract' in line), len(lines))
                authors = ' '.join(lines[len(title_candidate):author_endocument_idx]).strip()

            if extract_abstract:
                # Extracting abstract
                abstract_start_idx = first_page_text.find('Abstract')
                abstract_endocument_idx = first_page_text.find('\n\n', abstract_start_idx)
                abstract = first_page_text[abstract_start_idx:abstract_endocument_idx].strip()

        # Extracting full text
        for page in pdf.pages:
            try:
                page_text = page.extract_text()
            except:
                page_text = None
            if page_text:
                text[page.page_number] = page.extract_text()
            else:
                text[page.page_number] = "Extraction Error"

        # Extracting references
        if extract_references:
            references_extracted = False
            for i in range(-1, -16, -1):  # Last 15 pages
                page = pdf.pages[i]
                page_text = page.extract_text()
                if page_text and 'References' in page_text:
                    references_start = page_text.find('References')
                    references_text = page_text[references_start:]
                    references_extracted = True
                    break
            if not references_extracted:
                references_text = "References Extraction Error"


    return text, title, publication_date ,authors, abstract, references_text


# Example usage
# file_path = 'path/to/academic_paper.pdf'
# full_text, title, authors, abstract, references = extract_text_from_pdf(file_path)
# print("Title:", title)
# print("Authors:", authors)
# print("Abstract:", abstract)
# print("References:", references)
# print("Full Text:", full_text[:500])  # Displaying first 500 characters of the full text


