from app import app

def test_url_generation():
    with app.test_request_context():
        # Test URL generation for read_book route
        from flask import url_for
        
        try:
            url = url_for('read_book', book_id=1)
            print(f"Generated URL for read_book with book_id=1: {url}")
        except Exception as e:
            print(f"Error generating URL: {e}")
            
        try:
            url = url_for('read_book', book_id=999)
            print(f"Generated URL for read_book with book_id=999: {url}")
        except Exception as e:
            print(f"Error generating URL: {e}")

if __name__ == "__main__":
    test_url_generation()