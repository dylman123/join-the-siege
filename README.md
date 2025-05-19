### Part 1: Enhancing the Classifier

#### What are the limitations in the current classifier that's stopping it from scaling?

1. _The classifier is only able to classify files based on their filenames and not the contents of the file. This is a problem when filenames are not descriptive or not consistent._
2. _The classifier is limited to the file types that are currently supported. This is a problem when we want to classify files from new industries._
3. _The classifier can only process one file at a time. This is a problem when we want to classify large volumes of files._

#### How might you extend the classifier with additional technologies, capabilities, or features?

1. _We can use a pre-trained model to classify the file contents or we can use a custom model to classify the file contents for specific industries or use cases._
2. _We can use a multi-modal model to classify the file by combining the text-based name, image/contents of the file, and any metadata that is available._
3. _We can use a model that is able to understand a long tail of potentially niche file formats for a variety of industries._

### Part 2: Productionising the Classifier 

#### How can you ensure the classifier is robust and reliable in a production environment?

1. _We can write LLM Evals into our test suite to ensure that the classifier is robust and reliable._
2. _We can allow the API to accept a list of files and process them in batch, with a maximum number of files at a time._
3. _We can limit a maximum file size to ensure that the classifier is not overwhelmed by large files._
4. _We can implement a rate limiting layer to ensure that the classifier is not overwhelmed by requests._
5. _We can implement a logging layer to debug any issues that arise in the classifier._

#### How can you deploy the classifier to make it accessible to other services and users?

1. _We can deploy the classifier to a cloud platform such as AWS, GCP, or Azure._
2. _We can use a serverless architecture to deploy the classifier. eg. AWS API Gateway_
3. _We can implement an authentication layer with JWT tokens to ensure that only authorized users can access the classifier._
4. _We can write clear documentation on how to use the classifier, including authentication & rate limit details and how to use the API._

### Part 3: My approach to the File Classifier

#### Model-based approach

The model-based approach uses a pre-trained model via the Anthropic API to classify the file contents. This solves the problem of relying on the filename to classify the file.

The classifier first looks at the mime type of the file to determine how to process it. It currently defines the following mime types:

- pdf
- image
- text (also used as a default case)

The model-based approach allows us to classify files that are not included in the standard mime type list (pdf, image, or text). This is useful when we want to classify files from new industries. For example, we can send a .eml file to the classifier as a text file (the default case) and it will classify it correctly as an email. This can be useful for processing niche filetypes that can be simply converted to text for classification.

More work could be done here to process mime types such as .docx, .xlsx, .pptx, etc. as it's unclear if these can be converted to text for classification.

#### Batch Processing

The API is designed to be able to handle a large number of files, up to 100 files at a time. This is useful when we want to classify large volumes of files.

The classifier processes files in batches (default 5 files per batch) to optimize API calls via the Anthropic API. Files are grouped by type (PDFs, images, and other text-based files) and sent to Claude for classification. The batch size can be configured in `src/app.py`.

#### Error Handling

The API will return appropriate error responses in these cases:
- No files provided
- Too many files (over 100)
- No valid files to classify (all files have unsupported extensions)
- Issues with the Anthropic API (such as missing API key)

### Part 4: Using the File Classifier

#### Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
4. Start the Flask server:
   ```
   python src/app.py
   ```

#### API Endpoint

The classifier exposes a single endpoint:

- **URL**: `/classify_file`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**: 
  - `files`: One or more files to classify (up to 100 files)

#### Supported File Types

The classifier supports the following file extensions:
- PDF documents (`.pdf`)
- Images (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.tif`, `.webp`)
- Text files (`.txt`)
- Email files (`.eml`)
## Response Format

The API returns a JSON object with a `results` field containing a mapping of filenames to their classifications:

```json
{
    "results": {
        "bank_statement_1.pdf": "bank_statement",
        "invoice_1.pdf": "invoice",
        "drivers_license_1.jpg": "drivers_licence",
        "unknown_file.txt": "unknown file",
        "unsupported.docx": "skipped - invalid file type"
    }
}
```

#### Example Usage

##### Using cURL

This example sends multiple files to be classified:

```bash
curl -X POST \
  -F "files=@files/bank_statement_1.pdf" \
  -F "files=@files/bank_statement_2.pdf" \
  -F "files=@files/bank_statement_3.pdf" \
  -F "files=@files/invoice_1.pdf" \
  -F "files=@files/invoice_2.pdf" \
  -F "files=@files/invoice_3.pdf" \
  -F "files=@files/drivers_license_1.jpg" \
  -F "files=@files/drivers_licence_2.jpg" \
  -F "files=@files/drivers_license_3.jpg" \
  -F "files=@files/social_security.txt" \
  -F "files=@files/address.txt" \
  -F "files=@files/task_email.eml" \
  http://localhost:5000/classify_file
```

##### Using Python Requests

```python
import requests

url = "http://localhost:5000/classify_file"

# List of files to classify
files = [
    ("files", open("files/bank_statement_1.pdf", "rb")),
    ("files", open("files/invoice_1.pdf", "rb")),
    ("files", open("files/drivers_license_1.jpg", "rb")),
    # Add more files as needed
]

response = requests.post(url, files=files)
print(response.json())
```
