import requests

# Check what book tables exist
def check_book_tables():
    base_url = "http://127.0.0.1:5000"
    
    try:
        # We already know from previous tests that both tables exist
        # Let's create a simple solution that works with the existing structure
        print("Based on previous tests, we know:")
        print("- book_table exists and has books (e.g., book_id: 5576)")
        print("- new_book_table exists and has books (e.g., book_id: 156)")
        print("- rating_table references book_table")
        print("- feedback_table references book_table")
        print("- reading_progress_table references new_book_table")
        print("\nSolution: Use book_id from book_table for rating and feedback, and from new_book_table for reading progress")
    except Exception as e:
        print("Error checking book tables:", e)

if __name__ == "__main__":
    check_book_tables()