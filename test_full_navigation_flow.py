from app import app

def test_full_navigation_flow():
    with app.test_client() as client:
        # Create a session to simulate a logged-in user
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['user_id'] = 1  # Assuming user ID 1 exists
            session['username'] = 'testuser'
            session['role'] = 'user'
        
        print("=== Testing Full Navigation Flow ===")
        
        # 1. Test accessing book details page
        print("\n1. Testing book details page (/book/1)...")
        response = client.get('/book/1')
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("   SUCCESS: Book details page loaded")
            content = response.get_data(as_text=True)
            if 'The Lord of the Rings' in content:
                print("   SUCCESS: Book title found in book details page")
            else:
                print("   WARNING: Book title not found in book details page")
        elif response.status_code == 302:
            location = response.headers.get('Location')
            print(f"   Redirecting to: {location}")
        
        # 2. Test accessing read page
        print("\n2. Testing read page (/read/1)...")
        response = client.get('/read/1')
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("   SUCCESS: Read page loaded")
            content = response.get_data(as_text=True)
            if 'The Lord of the Rings' in content:
                print("   SUCCESS: Book title found in read page")
            else:
                print("   WARNING: Book title not found in read page")
        elif response.status_code == 302:
            location = response.headers.get('Location')
            print(f"   Redirecting to: {location}")
        
        # 3. Test with non-existent book
        print("\n3. Testing with non-existent book (/read/999999)...")
        response = client.get('/read/999999')
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location')
            print(f"   Redirecting to: {location}")
            if 'recommended_books' in location:
                print("   SUCCESS: Correctly redirected to recommended books for non-existent book")

if __name__ == "__main__":
    test_full_navigation_flow()