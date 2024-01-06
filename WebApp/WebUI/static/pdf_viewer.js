// Import the pdfjsLib from the ES module CDN URL
import * as pdfjsLib from 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0/+esm';

// Ensure the workerSrc property is specified.
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0/build/pdf.worker.mjs';

// Function to load and display a PDF
window.loadPDF = function loadPDF(fileName) {
    pdfjsLib.getDocument('/serve_pdf/?file=' + encodeURIComponent(fileName)).promise.then(function(pdfDoc) {
        const pdfContainer = document.getElementById('pdf-container');
        pdfContainer.innerHTML = ''; // Clear existing content

        for (let num = 1; num <= pdfDoc.numPages; num++) {
            const canvas = document.createElement('canvas');
            canvas.className = 'pdf-page-canvas';
            pdfContainer.appendChild(canvas);

            renderPage(pdfDoc, num, canvas, pdfContainer);
        }
    }).catch(function(error) {
        console.error('Error during PDF initialization: ', error);
    });
}

// Function to render each page of the PDF
function renderPage(pdfDoc, pageNumber, canvas, pdfContainer) {
    pdfDoc.getPage(pageNumber).then(function(page) {
        const viewport = page.getViewport({ scale: 2 });
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        const renderContext = {
            canvasContext: canvas.getContext('2d'),
            viewport: viewport
        };
        page.render(renderContext);

        // Additional logic for text layer
        // ...
    }).catch(function(error) {
        console.error('Error rendering page: ', error);
    });
}

// Fetch and list PDF files



