import requests

# Get sample data
def get_sample_data():
    base_url = "http://127.0.0.1:5000"
    
    try:
        response = requests.get(f"{base_url}/sample_data")
        print("Sample data:", response.text)
    except Exception as e:
        print("Error getting sample data:", e)

if __name__ == "__main__":
    get_sample_data()