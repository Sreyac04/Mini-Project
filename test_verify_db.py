import requests

# Test the database verification
def test_verify_db():
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Test database verification
        response = requests.get(f"{base_url}/verify_db")
        print("Database verification response:", response.text)
        
        # Test table creation
        response = requests.get(f"{base_url}/create_tables")
        print("Create tables response:", response.text)
        
    except Exception as e:
        print("Error testing database:", e)

if __name__ == "__main__":
    test_verify_db()