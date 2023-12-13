from django import forms

DOCUMENT_TYPE_CHOICES = [
    ('research_paper', 'Research Paper'),
    ('research_bookk', 'Research Boo'),
    ('personal_document', 'Personal Document'),
    ('others', 'Others'),
]

class DocumentForm(forms.Form):
    document_type = forms.ChoiceField(choices=DOCUMENT_TYPE_CHOICES)
    file = forms.FileField()

