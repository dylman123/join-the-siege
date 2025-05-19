from typing import Dict
from .classifier_utils import parse_response, VALID_CATEGORIES

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
            # Create content for batch request with dynamic categories
            categories_text = "\n    - " + "\n    - ".join(VALID_CATEGORIES)
            
            content = [
                {
                    "type": "text",
                    "text": f"""Please analyze each file and classify it into one of the following categories:
                    {categories_text}
                    
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
            results.update(parse_response(message.content[0].text, batch))
            
        except Exception as e:
            # If batch processing fails, add error for all files in batch
            for filename, _, _ in batch:
                results[filename] = f"Error classifying file: {str(e)}"
    
    return results 