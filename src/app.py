from flask import Flask, request, jsonify
from dotenv import load_dotenv

from src.classifier import classify_file
app = Flask(__name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg'}
MAX_FILES = 100  # Maximum number of files allowed in a single request

# Load environment variables
load_dotenv()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/classify_file', methods=['POST'])
def classify_file_route():
    # Check if any files are in the request
    if 'files' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400
    
    results = {}
    
    if 'files' in request.files:
        files = request.files.getlist('files')
        
        # Check if too many files
        if len(files) > MAX_FILES:
            return jsonify({"error": f"Too many files. Maximum allowed is {MAX_FILES}"}), 400
            
        # Check if no files were selected
        if len(files) == 0 or (len(files) == 1 and files[0].filename == ''):
            return jsonify({"error": "No selected files"}), 400
            
        # Process each valid file
        for file in files:
            if file.filename != '' and allowed_file(file.filename):
                file_class = classify_file(file)
                results[file.filename] = file_class
            else:
                # Skip invalid files
                if file.filename != '':
                    results[file.filename] = "skipped - invalid file type"
    
    if not results:
        return jsonify({"error": "No valid files to classify"}), 400
        
    return jsonify({"results": results}), 200


if __name__ == '__main__':
    app.run(debug=True)
