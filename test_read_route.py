from app import app

with app.test_client() as client:
    # Test the read route for book ID 1
    response = client.get('/read/1')
    
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response.content_type}")
    
    # Check if the response contains book content
    content = response.get_data(as_text=True)
    
    # Check if the title is in the response
    if 'The Lord of the Rings' in content:
        print("✓ Book title found in response")
    else:
        print("✗ Book title NOT found in response")
    
    # Check if the content is in the response
    if 'Bilbo Baggins' in content:
        print("✓ Book content found in response")
    else:
        print("✗ Book content NOT found in response")
    
    # Check if the content section is properly rendered
    if '<div class="book-text"' in content:
        print("✓ Book text div found in response")
    else:
        print("✗ Book text div NOT found in response")