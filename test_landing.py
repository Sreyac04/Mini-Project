from app import app

with app.test_client() as client:
    # Test the landing page
    response = client.get('/')
    
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response.content_type}")
    
    # Check if the response contains expected content
    content = response.get_data(as_text=True)
    
    # Check if the title is in the response
    if 'Book Bot' in content:
        print("✓ Book Bot title found in response")
    else:
        print("✗ Book Bot title NOT found in response")
    
    print(f"Response length: {len(content)} characters")