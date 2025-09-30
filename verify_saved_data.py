import requests

# Verify saved data
def verify_saved_data():
    base_url = "http://127.0.0.1:5000"
    
    try:
        response = requests.get(f"{base_url}/verify_saved_data")
        print("Saved data verification:", response.text)
    except Exception as e:
        print("Error verifying saved data:", e)

if __name__ == "__main__":
    verify_saved_data()