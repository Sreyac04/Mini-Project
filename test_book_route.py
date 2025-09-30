from app import app

with app.test_client() as client:
    # Test the book details route for book ID 1
    response = client.get('/book/1')
    
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response.content_type}")
    
    # Check if the response contains book content
    content = response.get_data(as_text=True)
    
    # Check if the title is in the response
    if 'The Lord of the Rings' in content:
        print("✓ Book title found in response")
    else:
        print("✗ Book title NOT found in response")
    
    # Check if the content section is properly rendered
    if 'Read Now' in content:
        print("✓ Read Now button found in response")
    else:
        print("✗ Read Now button NOT found in response")