from app import app, mysql

def list_books_without_content():
    """List all books that don't have content yet"""
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            cur.execute(
                "SELECT book_id, title, author, genre FROM new_book_table WHERE content IS NULL OR content = ''"
            )
            books = cur.fetchall()
            
            if books:
                print("Books without content:")
                print("-" * 50)
                for book in books:
                    book_id, title, author, genre = book
                    print(f"ID: {book_id} | {title} by {author} ({genre})")
            else:
                print("All books have content!")
            
            cur.close()
            
        except Exception as e:
            print(f"Error listing books: {e}")

def view_book_content(book_id):
    """View the content of a specific book"""
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            cur.execute(
                "SELECT title, author, genre, content FROM new_book_table WHERE book_id = %s",
                (book_id,)
            )
            book = cur.fetchone()
            
            if book:
                title, author, genre, content = book
                print(f"Title: {title}")
                print(f"Author: {author}")
                print(f"Genre: {genre}")
                print("-" * 50)
                if content:
                    print(content[:500] + "..." if len(content) > 500 else content)
                    if len(content) > 500:
                        print(f"\n[Content truncated. Total length: {len(content)} characters]")
                else:
                    print("No content available for this book.")
            else:
                print(f"No book found with ID {book_id}")
            
            cur.close()
            
        except Exception as e:
            print(f"Error viewing book content: {e}")

def update_book_content(book_id, new_content):
    """Update the content of a specific book"""
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            cur.execute(
                "UPDATE new_book_table SET content = %s WHERE book_id = %s",
                (new_content, book_id)
            )
            
            if cur.rowcount > 0:
                mysql.connection.commit()
                print(f"Successfully updated content for book ID {book_id}")
                return True
            else:
                print(f"No book found with ID {book_id}")
                return False
            
            cur.close()
            
        except Exception as e:
            print(f"Error updating book content: {e}")
            return False

def add_sample_content_to_all_books():
    """Add sample content to all books that don't have content"""
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            cur.execute(
                "SELECT book_id, title, author, genre FROM new_book_table WHERE content IS NULL OR content = ''"
            )
            books = cur.fetchall()
            
            updated_count = 0
            
            for book in books:
                book_id, title, author, genre = book
                
                # Generate sample content
                sample_content = f"""<h1>{title}</h1>
<h2>Chapter 1</h2>
<p>Welcome to "{title}" by {author}. This is a sample content for the book in the {genre} genre.</p>
<p>In a full implementation, this would contain the actual text of the book with proper formatting.</p>

<h2>Chapter 2</h2>
<p>This is additional sample content to demonstrate how the book reading feature works.</p>
<p>Users can read through the content, highlight words, adjust font size, and save their reading progress.</p>"""
                
                # Update the book with sample content
                cur.execute(
                    "UPDATE new_book_table SET content = %s WHERE book_id = %s",
                    (sample_content, book_id)
                )
                
                print(f"Added sample content for '{title}' by {author}")
                updated_count += 1
            
            mysql.connection.commit()
            cur.close()
            
            print(f"\nSuccessfully added sample content to {updated_count} books!")
            
        except Exception as e:
            print(f"Error adding sample content: {e}")

# Menu system for easy use
def main_menu():
    while True:
        print("\n" + "="*50)
        print("BOOK CONTENT MANAGEMENT SYSTEM")
        print("="*50)
        print("1. List books without content")
        print("2. View book content")
        print("3. Update book content")
        print("4. Add sample content to all books without content")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            list_books_without_content()
        elif choice == "2":
            try:
                book_id = int(input("Enter book ID: "))
                view_book_content(book_id)
            except ValueError:
                print("Please enter a valid book ID.")
        elif choice == "3":
            try:
                book_id = int(input("Enter book ID: "))
                print("Enter the new content (press Enter twice to finish):")
                content_lines = []
                while True:
                    line = input()
                    if line == "" and content_lines and content_lines[-1] == "":
                        break
                    content_lines.append(line)
                content = "\n".join(content_lines[:-1])  # Remove the last empty line
                update_book_content(book_id, content)
            except ValueError:
                print("Please enter a valid book ID.")
        elif choice == "4":
            confirm = input("This will add sample content to all books without content. Continue? (y/n): ")
            if confirm.lower() == 'y':
                add_sample_content_to_all_books()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()