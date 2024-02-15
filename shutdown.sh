#!/bin/bash

echo "Shutting down server on port 8000..."
fuser -k 8000/tcp

echo "Shutting down server on port 5000..."
fuser -k 5000/tcp

echo "Shutting down server on port 8501..."
fuser -k 8501/tcp

echo "All servers shut down successfully."
