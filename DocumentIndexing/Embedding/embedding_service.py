from flask import Flask, request, jsonify
from TextEmbedder import TextEmbedder
import numpy as np

app = Flask(__name__)
embedder = TextEmbedder()

@app.route('/embeddings/', methods=['POST'])
def create_embeddings():
    data = request.json
    text_list = data['text_list']
    embedding_type = data.get('embedding_type', 'local')  # Default to 'local'
    try:
        embeddings = embedder.embedding_listoftext(text_list, embedding_type)
        embeddings_list = [embedding.tolist() if isinstance(embedding, np.ndarray) else embedding for embedding in embeddings]
        return jsonify({"embeddings": embeddings_list})
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")  # Log the error
        print(f"Error: {e}")  # Optionally print to console
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
