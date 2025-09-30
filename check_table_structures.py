import requests

# Check the table structures
def check_table_structures():
    base_url = "http://127.0.0.1:5000"
    
    try:
        response = requests.get(f"{base_url}/describe_tables")
        print("Table structures:", response.text)
    except Exception as e:
        print("Error checking table structures:", e)

if __name__ == "__main__":
    check_table_structures()