import PDFJSExpress from '@pdftron/pdfjs-express'
import WebViewer from '@pdftron/pdfjs-express-viewer';




  PDFJSExpress({
    path: '/static/pdfjsexpress/core/webviewer-core.min.js',
    licenseKey: 'C59uR47FqvpvnqDTSCPB',
  }, document.getElementById('pdf-container'))
    .then(instance => {
      // use APIs here
      WebViewer({
        licenseKey: 'C59uR47FqvpvnqDTSCPB',
        initialDoc: 'https://myserver.com/myfile.pdf',
      }, document.getElementById('pdf-container')).then(instance => {
          const { documentViewer } = instance.Core;
      
          documentViewer.addEventListener('documentLoaded', () => {
            // perform document operations
          });
      
      });
    })