from app import app, mysql

# Test to check if the read_book route works with a logged-in session
with app.test_client() as client:
    # First, let's create a session to simulate a logged-in user
    with client.session_transaction() as session:
        session['loggedin'] = True
        session['user_id'] = 1  # Assuming user ID 1 exists
        session['username'] = 'testuser'
        session['role'] = 'user'
    
    # Now try to access the read route with a book ID
    response = client.get('/read/1')
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    
    # Check if it's redirecting to another page
    if response.status_code == 302:
        print(f"Redirecting to: {response.headers.get('Location')}")
    
    # Print first 500 characters of response
    content = response.get_data(as_text=True)
    print(f"Response preview: {content[:500]}")
    
    # Check if there's an error message in the response
    if "error" in content.lower():
        print("Found error in response")