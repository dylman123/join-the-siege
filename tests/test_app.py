from io import BytesIO

import pytest
from src.app import app, allowed_file

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize("filename, expected", [
    ("file.pdf", True),
    ("file.png", True),
    ("file.jpg", True),
    ("file.txt", False),
    ("file", False),
])
def test_allowed_file(filename, expected):
    assert allowed_file(filename) == expected

def test_no_file_in_request(client):
    response = client.post('/classify_file')
    assert response.status_code == 400

def test_no_selected_file(client):
    data = {'file': (BytesIO(b""), '')}  # Empty filename
    response = client.post('/classify_file', data=data, content_type='multipart/form-data')
    assert response.status_code == 400

def test_success(client, mocker):
    # Mock the classification function to return different values for different files
    classify_file_mock = mocker.patch('src.app.classify_file')
    classify_file_mock.side_effect = lambda file: 'test_class_1' if file.filename == 'file1.pdf' else 'test_class_2'

    # Create multiple files for upload
    data = {
        'files': [
            (BytesIO(b"dummy content 1"), 'file1.pdf'),
            (BytesIO(b"dummy content 2"), 'file2.pdf')
        ]
    }
    
    response = client.post('/classify_file', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.get_json() == {
        "results": {
            "file1.pdf": "test_class_1",
            "file2.pdf": "test_class_2"
        }
    }