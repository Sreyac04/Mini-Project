import requests
import json

# Base URL for the Flask app
base_url = "http://127.0.0.1:5001"

# Test data for reading progress
reading_progress_data = {
    "book_id": 1,
    "page_number": 5,
    "paused_word": "test",
    "paused_sentence": "This is a test sentence"
}

# Test data for rating
rating_data = {
    "book_id": 1,
    "rating": 4
}

# Test data for feedback
feedback_data = {
    "book_id": 1,
    "feedback": "This is a test feedback message"
}

print("Note: These tests will fail because there's no active session.")
print("In a real scenario, the user would be logged in and the session would provide the user_id.")
print("\nTesting reading progress saving...")
response = requests.post(f"{base_url}/save_reading_progress", 
                         json=reading_progress_data,
                         headers={"Content-Type": "application/json"})
print("Response:", response.json())

print("\nTesting rating saving...")
response = requests.post(f"{base_url}/save_rating", 
                         json=rating_data,
                         headers={"Content-Type": "application/json"})
print("Response:", response.json())

print("\nTesting feedback saving...")
response = requests.post(f"{base_url}/save_feedback", 
                         json=feedback_data,
                         headers={"Content-Type": "application/json"})
print("Response:", response.json())