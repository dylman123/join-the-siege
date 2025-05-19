import base64
from typing import Dict
from .classifier_utils import parse_response, VALID_CATEGORIES

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
            # Create content for batch request with dynamic categories
            categories_text = "\n    - " + "\n    - ".join(VALID_CATEGORIES)
            
            content = [
                {
                    "type": "text",
                    "text": f"""Please analyze each file and classify it into one of the following categories:
                    {categories_text}
                    
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
            
            results.update(parse_response(message.content[0].text, batch))
            
        except Exception as e:
            # If batch processing fails, add error for all files in batch
            for filename, _, _ in batch:
                results[filename] = f"Error classifying file: {str(e)}"
    
    return results 