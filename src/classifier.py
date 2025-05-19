from werkzeug.datastructures import FileStorage
import anthropic
import os
import base64
import mimetypes

def classify_file(file: FileStorage):
    """
    Classify a file using Anthropic's API by analyzing its content
    """
    # Get file information
    filename = file.filename.lower()
    
    # Read the file content
    file_content = file.read()
    
    # Determine the MIME type
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type:
        mime_type = "application/octet-stream"  # Default MIME type
    
    # Convert binary file to base64 for API
    file_base64 = base64.b64encode(file_content).decode('utf-8')
    
    # Initialize the Anthropic client
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "Error: ANTHROPIC_API_KEY not set in environment"
        
    client = anthropic.Anthropic(api_key=api_key)
    
    try:
        # Create content array based on file type
        content = [
            {
                "type": "text",
                "text": """Please analyze this file and classify it into one of the following categories:
                - drivers_licence
                - bank_statement
                - invoice
                - unknown file
                
                Only respond with the exact category name. If unsure or if the file doesn't match any of the specified categories, respond with 'unknown file'.
                
                Filename: {}
                """.format(filename)
            }
        ]
        
        # Add file content based on MIME type
        if mime_type == 'application/pdf':
            # Use document type for PDFs
            content.append({
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": file_base64
                }
            })
        elif mime_type in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
            # Use image type for supported image formats
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": file_base64
                }
            })
        else:
            # Fall back to filename-based classification for unsupported types
            if "drivers_license" in filename:
                return "drivers_licence"
            if "bank_statement" in filename:
                return "bank_statement"
            if "invoice" in filename:
                return "invoice"
            return "unknown file"
        
        # Create the message with the appropriate content
        message = client.messages.create(
            model="claude-3-7-sonnet-20250219",  # Use a model that supports PDF
            max_tokens=1024,
            system="You are a document classification expert. Analyze the file and determine its type. Be concise.",
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ]
        )
        
        # Extract the classification from the response
        classification = message.content[0].text.strip().lower()
        
        # Map the response to our expected categories
        valid_categories = {"drivers_licence", "bank_statement", "invoice", "unknown file"}
        if classification not in valid_categories:
            classification = "unknown file"
        
        return classification
        
    except Exception as e:
        # Return error message if there's an issue with Anthropic API call
        return f"Error classifying file: {str(e)}"
