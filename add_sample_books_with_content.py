from app import app, mysql

# Sample book content - you can replace this with real book content
sample_books = [
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "genre": "Fiction",
        "isbn": "9780743273565",
        "content": """<h1>The Great Gatsby</h1>
<h2>Chapter 1</h2>
<p>In my younger and more vulnerable years my father gave me some advice that I've carried with me ever since.</p>
<p>"Whenever you feel like criticizing anyone," he told me, "just remember that all the people in this world haven't had the advantages that you've had."</p>
<p>He didn't say any more, but we've always been unusually communicative in a reserved way, and I understood that he meant a great deal more than that.</p>
<p>In consequence, I'm inclined to reserve all judgments, a habit that has opened up many curious natures to me and also made me the victim of not a few veteran bores.</p>
<p>The abnormal mind is quick to detect and attach itself to this quality when it appears in a normal person, and so it came about that in college I was unjustly accused of being a politician, because I was privy to the secret griefs of wild, unknown men.</p>
<p>Most of the confidences were unsought—frequently I have feigned sleep, preoccupation, or a hostile levity when I realized by some unmistakable sign that an intimate revelation was quivering on the horizon; for the intimate revelations of young men, or at least the terms in which they express them, are usually plagiaristic and marred by obvious suppressions.</p>"""
    },
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "genre": "Fiction",
        "isbn": "9780061120084",
        "content": """<h1>To Kill a Mockingbird</h1>
<h2>Chapter 1</h2>
<p>When he was nearly thirteen, my brother Jem got his arm badly broken at the elbow. When it healed, and Jem's fears of never being able to play football were assuaged, he was seldom self-conscious about his injury.</p>
<p>His left arm was somewhat shorter than his right; when he stood or walked, the back of his hand was at right angles to his body, his thumb parallel to his thigh. He couldn't have cared less, so long as he could pass and punt.</p>
<p>When I asked him where he got his injury, Jem would say: "In the line of duty." He was more to the point when he said that the way he got it all began when Dill arrived.</p>
<p>Dill was from Meridian, Mississippi, was spending the summer with his aunt, Miss Rachel, and would be spending every summer in Maycomb from now on.</p>
<p>He was a year my senior but I had known him ever since he lived next door to us when I was almost six and he was nearly seven.</p>"""
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "genre": "Dystopian",
        "isbn": "9780451524935",
        "content": """<h1>1984</h1>
<h2>Chapter 1</h2>
<p>It was a bright cold day in April, and the clocks were striking thirteen. Winston Smith, his chin nuzzled into his breast in an effort to escape the vile wind, slipped quickly through the glass doors of Victory Mansions.</p>
<p>The hallway smelt of boiled cabbage and old rag mats. At one end of it a coloured poster, too large for indoor display, had been tacked to the wall. It depicted simply an enormous face, more than a metre wide.</p>
<p>The face was that of a man of about forty-five, with a heavy black moustache and ruggedly handsome features.</p>
<p>Winston made for the stairs. It was no use trying the lift. Even at the best of times it was seldom working, and at present the electric current was cut off during daylight hours.</p>
<p>It was one of the improvements that were to have been completed for the celebration of Hate Week.</p>"""
    }
]

def add_sample_books_with_content():
    """Add sample books with content to the database"""
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            added_count = 0
            
            for book in sample_books:
                # Check if book already exists
                cur.execute(
                    "SELECT book_id FROM new_book_table WHERE title = %s AND author = %s",
                    (book["title"], book["author"])
                )
                existing_book = cur.fetchone()
                
                if existing_book:
                    # Update existing book with content
                    cur.execute(
                        "UPDATE new_book_table SET content = %s WHERE book_id = %s",
                        (book["content"], existing_book[0])
                    )
                    print(f"Updated content for existing book: '{book['title']}' by {book['author']}")
                else:
                    # Add new book with content
                    cur.execute(
                        "INSERT INTO new_book_table (title, author, genre, ISBN, content) VALUES (%s, %s, %s, %s, %s)",
                        (book["title"], book["author"], book["genre"], book["isbn"], book["content"])
                    )
                    print(f"Added new book: '{book['title']}' by {book['author']}")
                
                added_count += 1
            
            mysql.connection.commit()
            cur.close()
            
            print(f"\nSuccessfully processed {added_count} books!")
            
        except Exception as e:
            print(f"Error adding sample books: {e}")

if __name__ == "__main__":
    add_sample_books_with_content()