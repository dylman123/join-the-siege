from typing import Dict
from .classifier_utils import parse_response, VALID_CATEGORIES

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
            # Create content for batch request with dynamic categories
            categories_text = "\n    - " + "\n    - ".join(VALID_CATEGORIES)
            
            content = [
                {
                    "type": "text",
                    "text": f"""Please analyze each image and classify it into one of the following categories:
                    {categories_text}
                    
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
            results.update(parse_response(message.content[0].text, batch))
            
        except Exception as e:
            # If batch processing fails, add error for all files in batch
            for filename, _, _ in batch:
                results[filename] = f"Error classifying file: {str(e)}"
    
    return results 