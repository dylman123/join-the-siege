from typing import Dict, List, Tuple, Callable, Any

# Common constants
VALID_CATEGORIES = {"drivers_licence", "bank_statement", "invoice", "unknown file"}

def parse_response(response_text: str, batch: List[Tuple[str, str, str]]) -> Dict[str, str]:
    """
    Parse Claude's response to extract classifications
    
    Args:
        response_text: Text response from Claude
        batch: List of (filename, mime_type, base64_content) tuples
        
    Returns:
        Dictionary mapping filenames to their classifications
    """
    results = {}
    lines = response_text.split('\n')
    
    for line in lines:
        if ':' in line:
            parts = line.split(':', 1)
            filename_part = parts[0].strip()
            classification = parts[1].strip().lower()
            
            # Map to one of our valid categories
            if classification not in VALID_CATEGORIES:
                classification = "unknown file"
            
            # Find the correct original filename
            for original_filename, _, _ in batch:
                if original_filename.lower() in filename_part.lower():
                    results[original_filename] = classification
                    break
    
    # Make sure all files have a result
    for original_filename, _, _ in batch:
        if original_filename not in results:
            results[original_filename] = "unknown file"
            
    return results