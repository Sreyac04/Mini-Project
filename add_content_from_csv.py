import csv
from app import app, mysql

def add_content_from_csv(csv_file_path):
    """
    Add book content from a CSV file.
    
    CSV format expected:
    title,author,genre,isbn,content
    """
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            # Read the CSV file
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                added_count = 0
                updated_count = 0
                
                for row in csv_reader:
                    title = row.get('title', '').strip()
                    author = row.get('author', '').strip()
                    genre = row.get('genre', '').strip()
                    isbn = row.get('isbn', '').strip()
                    content = row.get('content', '').strip()
                    
                    if not title or not author or not content:
                        print(f"Skipping row with missing required fields: {row}")
                        continue
                    
                    # Check if book exists
                    cur.execute(
                        "SELECT book_id FROM new_book_table WHERE title = %s AND author = %s",
                        (title, author)
                    )
                    existing_book = cur.fetchone()
                    
                    if existing_book:
                        # Update existing book with content
                        cur.execute(
                            "UPDATE new_book_table SET content = %s WHERE book_id = %s",
                            (content, existing_book[0])
                        )
                        print(f"Updated content for existing book: '{title}' by {author}")
                        updated_count += 1
                    else:
                        # Add new book with content
                        cur.execute(
                            "INSERT INTO new_book_table (title, author, genre, ISBN, content) VALUES (%s, %s, %s, %s, %s)",
                            (title, author, genre, isbn, content)
                        )
                        print(f"Added new book: '{title}' by {author}")
                        added_count += 1
                
                mysql.connection.commit()
                cur.close()
                
                print(f"\nSuccessfully processed books from CSV!")
                print(f"Added {added_count} new books")
                print(f"Updated content for {updated_count} existing books")
                
        except FileNotFoundError:
            print(f"Error: CSV file '{csv_file_path}' not found.")
        except Exception as e:
            print(f"Error processing CSV file: {e}")

def create_sample_csv(csv_file_path):
    """
    Create a sample CSV file with book data for testing
    """
    sample_data = [
        {
            "title": "The Adventures of Sherlock Holmes",
            "author": "Arthur Conan Doyle",
            "genre": "Mystery",
            "isbn": "9780451527096",
            "content": """<h1>The Adventures of Sherlock Holmes</h1>
<h2>A Scandal in Bohemia</h2>
<p>To Sherlock Holmes she is always the woman. I have seldom heard him mention her under any other name. In his eyes she eclipses and predominates the whole of her sex. It was not that he felt any emotion akin to love for Irene Adler. All emotions, and that one particularly, were abhorrent to his cold, precise but admirably balanced mind. He was, I take it, the most perfect reasoning and observing machine that the world has seen, but as a lover he would have placed himself in a false position.</p>
<p>We had sat down nearly half an hour in silence when our door opened and a woman entered. She was a lovely woman, with a face that was winsome and yet alert, with clear, bright eyes and a delicate, curved nose.</p>"""
        },
        {
            "title": "The Time Machine",
            "author": "H.G. Wells",
            "genre": "Science Fiction",
            "isbn": "9780451527089",
            "content": """<h1>The Time Machine</h1>
<h2>Chapter 1</h2>
<p>The Time Traveller (for so it will be convenient to speak of him) was expounding a recondite matter to us. His grey eyes shone and twinkled, and his usually pale face was flushed and animated. The fire burned brightly, and the soft radiance of the incandescent lights in the lilies of silver caught the bubbles that flashed and passed in our glasses. Our chairs, being his patents, embraced and caressed us rather than submitted to be sat upon, and there was that luxurious after-dinner atmosphere when thought runs gracefully free of the trammels of precision.</p>
<p>And he put it to us in this way—marking the points with a lean forefinger—as we sat and lazily admired his earnestness over this new paradox (as we thought it) and his fecundity.</p>"""
        },
        {
            "title": "Dracula",
            "author": "Bram Stoker",
            "genre": "Horror",
            "isbn": "9780451527058",
            "content": """<h1>Dracula</h1>
<h2>Chapter 1</h2>
<p>Left Munich at 8:35 P.M., on 1st May, arriving at Vienna early next morning; should have arrived at 6:46, but train was an hour late. Buda-Pesth seems a wonderful place, from the glimpse which I got of it from the train and the little I could walk through the streets. I feared to go very far from the station, as we had arrived late and would start as near the correct time as possible.</p>
<p>The impression I had was that we were leaving the West and entering the East; the most western of splendid bridges over the Danube, which is here of noble width and depth, took us among the traditions of Turkish rule.</p>"""
        }
    ]
    
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['title', 'author', 'genre', 'isbn', 'content']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for book in sample_data:
            writer.writerow(book)
    
    print(f"Sample CSV file created at: {csv_file_path}")
    return csv_file_path

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        csv_file_path = sys.argv[1]
        add_content_from_csv(csv_file_path)
    else:
        print("No CSV file provided. Creating a sample CSV file...")
        sample_csv = create_sample_csv("sample_books.csv")
        print(f"\nNow importing the sample data...")
        add_content_from_csv(sample_csv)
        print("\nTo import your own CSV file, run:")
        print("python add_content_from_csv.py your_file.csv")