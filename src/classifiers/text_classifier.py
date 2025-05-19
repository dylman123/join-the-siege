import base64
from typing import Dict, List, Tuple

def classify_text_files(client, text_files, batch_size: int = 5) -> Dict[str, str]:
    """
    Classify text files or files with unknown MIME types in batches
    """
    results = {}
    
    for i in range(0, len(text_files), batch_size):
        batch = text_files[i:i+batch_size]
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
                    If you can't determine the file type, classify it as 'unknown file'.
                    Example: file1.txt: invoice
                    
                    Here are the files to classify:
                    """ + "\n".join([f"File {idx+1}: {file[0]}" for idx, file in enumerate(batch)])
                }
            ]
            
            # Add each text file to the content
            for filename, mime_type, file_base64 in batch:
                try:
                    # Try to decode base64 content as text
                    file_content = base64.b64decode(file_base64).decode('utf-8', errors='replace')
                    
                    # Add the text content (limit to first 10000 chars to avoid token limits)
                    file_content = file_content[:10000]
                    content.append({
                        "type": "text",
                        "text": f"\nFile: {filename}\nContent:\n{file_content}"
                    })
                except Exception as e:
                    # If we can't decode as text, describe the error
                    content.append({
                        "type": "text",
                        "text": f"\nFile: {filename}\nNote: Unable to read content as text. Error: {str(e)}"
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