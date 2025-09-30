import requests

# Visit the create_tables route to create missing tables
def create_tables():
    base_url = "http://127.0.0.1:5000"
    
    try:
        response = requests.get(f"{base_url}/create_tables")
        print("Create tables response:", response.text)
    except Exception as e:
        print("Error creating tables:", e)

if __name__ == "__main__":
    create_tables()