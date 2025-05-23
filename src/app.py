from flask import Flask, request, jsonify
from dotenv import load_dotenv

from src.classifier import classify_batch
app = Flask(__name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'tif', 'webp', 'eml', 'txt'}
MAX_FILES = 100  # Maximum number of files allowed in a single request
BATCH_SIZE = 5   # Number of files to process in a single Anthropic API call

# Load environment variables
load_dotenv()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/classify_files', methods=['POST'])
def classify_files_route():
    # Check if any files are in the request
    if 'files' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400
    
    files = request.files.getlist('files')
    
    # Check if too many files
    if len(files) > MAX_FILES:
        return jsonify({"error": f"Too many files. Maximum allowed is {MAX_FILES}"}), 400
        
    # Check if no files were selected
    if len(files) == 0 or (len(files) == 1 and files[0].filename == ''):
        return jsonify({"error": "No selected files"}), 400
        
    # Filter valid files
    valid_files = [file for file in files if file.filename != '' and allowed_file(file.filename)]
    
    if not valid_files:
        return jsonify({"error": "No valid files to classify"}), 400
    
    # Process files in batches
    results = classify_batch(valid_files, BATCH_SIZE)
    
    # Add skipped files to results
    for file in files:
        if file.filename != '' and not allowed_file(file.filename):
            results[file.filename] = "skipped - invalid file type"
    
    return jsonify({"results": results}), 200

if __name__ == '__main__':
    app.run(debug=True)
