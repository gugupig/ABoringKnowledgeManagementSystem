# word_processor.py

from docx import Document

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = {}
    for para in doc.paragraphs:
        text[para.part.element.rId] = para.text
    return text


from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.opc.package import OpcPackage

def extract_word_metadata(docx_path):
    package = OpcPackage.open(docx_path)
    core_props = package.core_properties
    metadata = {
        'title': core_props.title,
        'author': core_props.author,
        'created': core_props.created,
        'modified': core_props.modified,
        # Add more properties as needed
    }
    return metadata


# Example usage
if __name__ == "__main__":
    text = extract_text_from_docx('path/to/your/file.docx')
    print(text)
