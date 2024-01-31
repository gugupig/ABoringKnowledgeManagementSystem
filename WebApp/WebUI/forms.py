from django import forms

DOCUMENT_TYPE_CHOICES = [
    ('research_paper', 'Research Paper'),
    ('research_bookk', 'Research Book'),
    ('personal_document', 'Personal Document'),
    ('others', 'Others'),
]
DOCUMENT_TAG_CHOICES = [
    ('Linguistics', 'Linguistics'),
    ("Linguistics>Phonetics", "Linguistics>Phonetics"),
    ("Linguistics>Phonology", "Linguistics>Pphonology"),
    ("Linguistics>Morphology", "Linguistics>Morphology"),
    ("Linguistics>Syntax", "Linguistics>Syntax"),
    ("Linguistics>Semantics", "Linguistics>Semantics"),
    ("Linguistics>Pragmatics", "Linguistics>Pragmatics"),
    ("Linguistics>NLP", "Linguistics>NLP"),
    ("Machine Learning", "Machine Learning"),
    
    
]

class DocumentForm(forms.Form):
    document_type = forms.ChoiceField(choices=DOCUMENT_TYPE_CHOICES)
    #TO DO : add title and tags in the document pipeline
    #title = forms.CharField(max_length=100)
    tags= forms.MultipleChoiceField(choices=DOCUMENT_TAG_CHOICES)
    file = forms.FileField()

