"""
Safe Content Adder for new_book_table
This script safely adds content to existing books without affecting any other data.
"""
import csv
from app import app, mysql

def safe_add_content_to_existing_books(csv_file_path):
    """
    Safely add content to existing books in new_book_table.
    This will NOT affect any existing data - only add content to books that already exist.
    """
    print("Starting safe content addition process...")
    print("=" * 50)
    
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            # First, let's see what books we currently have
            cur.execute("SELECT book_id, title, author FROM new_book_table")
            existing_books = cur.fetchall()
            
            print(f"Found {len(existing_books)} existing books in database:")
            for book in existing_books:
                print(f"  ID: {book[0]}, Title: {book[1]}, Author: {book[2]}")
            
            # Read the CSV file
            print(f"\nReading content from: {csv_file_path}")
            books_updated = 0
            
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                # Try comma first, then tab
                if ',' in sample:
                    csv_reader = csv.DictReader(file)
                else:
                    csv_reader = csv.DictReader(file, delimiter='\t')
                
                for row_num, row in enumerate(csv_reader, start=2):  # start=2 because header is row 1
                    title = row.get('title', '').strip()
                    author = row.get('author', '').strip()
                    content = row.get('content', '').strip()
                    
                    if not title or not author or not content:
                        print(f"  Warning: Skipping row {row_num} due to missing data")
                        continue
                    
                    # Check if this book exists in our database
                    cur.execute(
                        "SELECT book_id FROM new_book_table WHERE title = %s AND author = %s",
                        (title, author)
                    )
                    existing_book = cur.fetchone()
                    
                    if existing_book:
                        # Only update if there's no content yet, or if you want to overwrite
                        cur.execute(
                            "UPDATE new_book_table SET content = %s WHERE book_id = %s",
                            (content, existing_book[0])
                        )
                        print(f"  ✓ Updated content for: '{title}' by {author}")
                        books_updated += 1
                    else:
                        print(f"  i Book not found in database: '{title}' by {author}")
            
            mysql.connection.commit()
            cur.close()
            
            print(f"\nProcess completed!")
            print(f"Successfully updated content for {books_updated} books.")
            
        except FileNotFoundError:
            print(f"Error: CSV file '{csv_file_path}' not found.")
            print("Please make sure the file exists and the path is correct.")
        except Exception as e:
            print(f"Error: {e}")
            print("No changes were made to your database.")

def create_sample_content_csv():
    """
    Create a sample CSV with your existing books (if we can find them)
    """
    sample_books = [
        {
            "title": "The Lord of the Rings",
            "author": "J.R.R. Tolkien",
            "content": """<h1>The Lord of the Rings</h1>
<h2>Chapter 1: A Long-expected Party</h2>
<p>When Mr. Bilbo Baggins of Bag End announced that he would shortly be celebrating his eleventy-first birthday with a party of special magnificence, there was much talk and excitement in Hobbiton.</p>
<p>Bilbo was very rich and very peculiar, and had been the wonder of the Shire for sixty years, ever since his remarkable disappearance and unexpected return. The riches he had brought back from his travels had now become a local legend.</p>"""
        },
        {
            "title": "Harry Potter and the Sorcerer's Stone",
            "author": "J.K. Rowling",
            "content": """<h1>Harry Potter and the Sorcerer's Stone</h1>
<h2>Chapter 1: The Boy Who Lived</h2>
<p>Mr. and Mrs. Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal, thank you very much. They were the last people you'd expect to be involved in anything strange or mysterious, because they just didn't hold with such nonsense.</p>
<p>Mr. Dursley was the director of a firm called Grunnings, which made drills. He was a big, beefy man with hardly any neck, although he did have a very large moustache. Mrs. Dursley was thin and blonde and had nearly twice the usual amount of neck.</p>"""
        },
        {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "content": """<h1>Pride and Prejudice</h1>
<h2>Chapter 1</h2>
<p>It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.</p>
<p>However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered as the rightful property of some one or other of their daughters.</p>"""
        }
    ]
    
    csv_filename = "book_content_template.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['title', 'author', 'content']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for book in sample_books:
            writer.writerow(book)
    
    print(f"Sample CSV template created: {csv_filename}")
    print("You can edit this file to add content for your actual books.")
    return csv_filename

if __name__ == "__main__":
    print("Safe Book Content Adder")
    print("=" * 30)
    print("This tool will safely add content to your existing books without affecting any other data.\n")
    
    # Ask user what they want to do
    print("What would you like to do?")
    print("1. Create a sample CSV template")
    print("2. Add content from an existing CSV file")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        csv_file = create_sample_content_csv()
        print(f"\nNext steps:")
        print(f"1. Open {csv_file} in a spreadsheet editor or text editor")
        print(f"2. Replace the sample content with your actual book content")
        print(f"3. Run this script again and choose option 2")
    elif choice == "2":
        csv_file_path = input("Enter the path to your CSV file: ").strip()
        if csv_file_path:
            safe_add_content_to_existing_books(csv_file_path)
        else:
            print("No file path provided.")
    else:
        print("Invalid choice.")