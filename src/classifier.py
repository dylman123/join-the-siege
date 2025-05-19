from werkzeug.datastructures import FileStorage
import anthropic
import os
import base64
import mimetypes
from typing import Dict, List, Tuple

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
    
    for file in files:
        filename, mime_type, file_base64 = prepare_file_for_api(file)
        
        # Sort files by type
        if mime_type == 'application/pdf':
            pdf_files.append((file.filename, mime_type, file_base64))
        elif mime_type in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
            image_files.append((file.filename, mime_type, file_base64))
        else:
            results[file.filename] = "unknown file"
    
    # Process files by type
    pdf_results = classify_pdfs(client, pdf_files, batch_size)
    image_results = classify_images(client, image_files, batch_size)
    
    # Combine results
    results.update(pdf_results)
    results.update(image_results)
    
    return results

def classify_pdfs(client, pdf_files, batch_size: int = 5) -> Dict[str, str]:
    """
    Classify PDF files in batches
    """
    results = {}
    
    for i in range(0, len(pdf_files), batch_size):
        batch = pdf_files[i:i+batch_size]
        if not batch:
            continue
            
        try:
            # Create content for batch request
            content = [
                {
                    "type": "text",
                    "text": """Please analyze each file and classify it into one of the following categories:
                    - drivers_licence
                    - bank_statement
                    - invoice
                    - unknown file
                    
                    For each file, respond with the filename followed by a colon and the category. 
                    Example: file1.pdf: drivers_licence
                    
                    Here are the files to classify:
                    """ + "\n".join([f"File {idx+1}: {file[0]}" for idx, file in enumerate(batch)])
                }
            ]
            
            # Add each PDF file to the content
            for filename, mime_type, file_base64 in batch:
                content.append({
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": mime_type,
                        "data": file_base64
                    }
                })
            
            # Make the API call
            message = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=1024,
                system="You are a document classification expert. Analyze each file and determine its type. Be concise.",
                messages=[{"role": "user", "content": content}]
            )
            
            # Parse the response to extract classifications for each file
            response_text = message.content[0].text.strip()
            lines = response_text.split('\n')
            
            for line in lines:
                if ':' in line:
                    parts = line.split(':', 1)
                    filename_part = parts[0].strip()
                    classification = parts[1].strip().lower()
                    
                    # Map to one of our valid categories
                    valid_categories = {"drivers_licence", "bank_statement", "invoice", "unknown file"}
                    if classification not in valid_categories:
                        classification = "unknown file"
                    
                    # Find the correct original filename
                    for original_filename, _, _ in batch:
                        if original_filename.lower() in filename_part.lower():
                            results[original_filename] = classification
                            break
            
        except Exception as e:
            # If batch processing fails, add error for all files in batch
            for filename, _, _ in batch:
                results[filename] = f"Error classifying file: {str(e)}"
    
    return results

def classify_images(client, image_files, batch_size: int = 5) -> Dict[str, str]:
    """
    Classify image files in batches
    """
    results = {}
    
    for i in range(0, len(image_files), batch_size):
        batch = image_files[i:i+batch_size]
        if not batch:
            continue
            
        try:
            # Create content for batch request
            content = [
                {
                    "type": "text",
                    "text": """Please analyze each image and classify it into one of the following categories:
                    - drivers_licence
                    - bank_statement
                    - invoice
                    - unknown file
                    
                    For each image, respond with the filename followed by a colon and the category. 
                    Example: image1.jpg: drivers_licence
                    
                    Here are the images to classify:
                    """ + "\n".join([f"Image {idx+1}: {file[0]}" for idx, file in enumerate(batch)])
                }
            ]
            
            # Add each image file to the content
            for filename, mime_type, file_base64 in batch:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": mime_type,
                        "data": file_base64
                    }
                })
            
            # Make the API call
            message = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=1024,
                system="You are a document classification expert. Analyze each image and determine its type. Be concise.",
                messages=[{"role": "user", "content": content}]
            )
            
            # Parse the response to extract classifications for each file
            response_text = message.content[0].text.strip()
            lines = response_text.split('\n')
            
            for line in lines:
                if ':' in line:
                    parts = line.split(':', 1)
                    filename_part = parts[0].strip()
                    classification = parts[1].strip().lower()
                    
                    # Map to one of our valid categories
                    valid_categories = {"drivers_licence", "bank_statement", "invoice", "unknown file"}
                    if classification not in valid_categories:
                        classification = "unknown file"
                    
                    # Find the correct original filename
                    for original_filename, _, _ in batch:
                        if original_filename.lower() in filename_part.lower():
                            results[original_filename] = classification
                            break
            
        except Exception as e:
            # If batch processing fails, add error for all files in batch
            for filename, _, _ in batch:
                results[filename] = f"Error classifying file: {str(e)}"
    
    return results
