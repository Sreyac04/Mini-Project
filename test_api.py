import requests
import json

# Test the API endpoints
def test_api():
    base_url = "http://127.0.0.1:5000"
    
    # Use valid user and book IDs
    user_id = 66
    book_id = 5576  # Using a book ID from book_table to match foreign key constraints
    
    # Test saving reading progress
    progress_data = {
        "user_id": user_id,
        "book_id": book_id,
        "page_number": 5,
        "paused_word": "test",
        "paused_sentence": "This is a test sentence."
    }
    
    try:
        response = requests.post(f"{base_url}/save_reading_progress", 
                               json=progress_data,
                               headers={"Content-Type": "application/json"})
        print("Save reading progress response:", response.json())
    except Exception as e:
        print("Error saving reading progress:", e)
    
    # Test saving rating
    rating_data = {
        "user_id": user_id,
        "book_id": book_id,
        "rating": 5
    }
    
    try:
        response = requests.post(f"{base_url}/save_rating", 
                               json=rating_data,
                               headers={"Content-Type": "application/json"})
        print("Save rating response:", response.json())
    except Exception as e:
        print("Error saving rating:", e)
    
    # Test saving feedback
    feedback_data = {
        "user_id": user_id,
        "book_id": book_id,
        "feedback": "This is a test feedback."
    }
    
    try:
        response = requests.post(f"{base_url}/save_feedback", 
                               json=feedback_data,
                               headers={"Content-Type": "application/json"})
        print("Save feedback response:", response.json())
    except Exception as e:
        print("Error saving feedback:", e)

if __name__ == "__main__":
    test_api()