from werkzeug.datastructures import FileStorage
import anthropic
import os
import base64
import mimetypes
from typing import Dict, List, Tuple

from src.classifiers.pdf_classifier import classify_pdfs
from src.classifiers.image_classifier import classify_images
from src.classifiers.text_classifier import classify_text_files

def prepare_file_for_api(file: FileStorage) -> Tuple[str, str, str]:
    """
    Prepare a file for the Anthropic API by extracting its content and metadata
    Returns: (filename, mime_type, base64_content)
    """
    filename = file.filename.lower()
    file_content = file.read()
    
    # Determine the MIME type
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type:
        mime_type = "application/octet-stream"  # Default MIME type
    
    # Convert binary file to base64 for API
    file_base64 = base64.b64encode(file_content).decode('utf-8')
    
    return filename, mime_type, file_base64

def classify_batch(files: List[FileStorage], batch_size: int = 5) -> Dict[str, str]:
    """
    Classify multiple files in batches to minimize API calls
    """
    # Initialize Anthropic client
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {file.filename: "Error: ANTHROPIC_API_KEY not set in environment" for file in files}
    
    client = anthropic.Anthropic(api_key=api_key)
    results = {}
    
    # Group files by MIME type for more efficient processing
    pdf_files = []
    image_files = []
    text_files = []
    
    for file in files:
        filename, mime_type, file_base64 = prepare_file_for_api(file)
        
        # Sort files by type
        if mime_type == 'application/pdf':
            pdf_files.append((file.filename, mime_type, file_base64))
        elif mime_type in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
            image_files.append((file.filename, mime_type, file_base64))
        else:
            text_files.append((file.filename, mime_type, file_base64))
    
    # Process files by type
    pdf_results = classify_pdfs(client, pdf_files, batch_size)
    image_results = classify_images(client, image_files, batch_size)
    text_results = classify_text_files(client, text_files, batch_size)
    
    # Combine results
    results.update(pdf_results)
    results.update(image_results)
    results.update(text_results)
    
    return results
