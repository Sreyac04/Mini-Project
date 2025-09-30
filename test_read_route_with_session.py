from app import app

def test_read_route_with_session():
    with app.test_client() as client:
        # Create a session to simulate a logged-in user
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['user_id'] = 1  # Assuming user ID 1 exists
            session['username'] = 'testuser'
            session['role'] = 'user'
        
        print("Testing read_book route with book ID 1...")
        
        # Try to access the read route with a book ID
        response = client.get('/read/1')
        print(f"Status code: {response.status_code}")
        
        # Check the response
        if response.status_code == 200:
            print("SUCCESS: Book page loaded correctly")
            # Check if the response contains book content
            content = response.get_data(as_text=True)
            if 'The Lord of the Rings' in content:
                print("SUCCESS: Book title found in response")
            else:
                print("WARNING: Book title not found in response")
        elif response.status_code == 302:
            # Redirect
            location = response.headers.get('Location')
            print(f"Redirecting to: {location}")
            if 'recommended_books' in location:
                print("ERROR: Redirected to recommended_books - book not found or database error")
            elif 'login' in location:
                print("ERROR: Redirected to login - session not set correctly")
        else:
            print(f"ERROR: Unexpected status code {response.status_code}")

if __name__ == "__main__":
    test_read_route_with_session()