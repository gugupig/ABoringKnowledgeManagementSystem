function loadDocuments(filterTag = '') {
    fetch('/static/documents.json')
    .then(response => response.json())
    .then(documents => {
        const container = document.getElementById('documents-container');
        container.innerHTML = ''; // Clear existing content
        documents.forEach(doc => {
            if (filterTag === '' || doc.tags.includes(filterTag)) {
                const div = document.createElement('div');
                div.textContent = `Document: ${doc.name}`; // Customize as needed
                container.appendChild(div);
            }
        });
    })
    .catch(error => console.error('Error loading documents:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    loadDocuments(); // Load all documents initially

    const filterInput = document.getElementById('tagFilter');
    filterInput.addEventListener('input', function() {
        loadDocuments(this.value); // Load filtered documents as user types
    });
});

<div id="documents-container">
<!-- Documents will be loaded here -->
</div>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const jsonUrl = "{% static 'document_list_cache/research_paper.json' %}";
    fetch(jsonUrl)
    .then(response => response.json())
    .then(documents => {
        const container = document.getElementById('documents-container');
        documents.forEach(doc => {
            const div = document.createElement('div');
            const link = document.createElement('a');
            const title = doc.metadata.Title || doc._id
            link.textContent = `Document: ${title}`;
            link.href = doc.file_path;
            link.target = '_blank';  // Open in a new tab
            div.appendChild(link);
            container.appendChild(div);
        });
    })
    .catch(error => console.error('Error loading documents:', error));
});

</script>