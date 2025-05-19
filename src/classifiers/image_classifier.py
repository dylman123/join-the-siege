from typing import Dict, List, Tuple

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