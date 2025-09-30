import requests

# Test the API endpoints with a session
def test_api_with_session():
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    # First, let's try to login (you'll need to use actual credentials)
    # For now, let's directly test the functionality that doesn't require auth
    # by temporarily modifying the routes to not require login for testing
    
    # Test creating tables
    try:
        response = session.get(f"{base_url}/create_tables")
        print("Create tables response:", response.text)
    except Exception as e:
        print("Error creating tables:", e)

if __name__ == "__main__":
    test_api_with_session()