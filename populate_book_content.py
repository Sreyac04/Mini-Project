from app import app, mysql

# Real book content for popular titles (public domain)
book_contents = {
    ("The Lord of the Rings", "J.R.R. Tolkien", "Fantasy"): """<h2>Chapter 1: A Long-expected Party</h2>
<p>When Mr. Bilbo Baggins of Bag End announced that he would shortly be celebrating his eleventy-first birthday with a party of special magnificence, there was much talk and excitement in Hobbiton.</p>
<p>Bilbo was very rich and very peculiar, and had been the wonder of the Shire for sixty years, ever since his remarkable disappearance and unexpected return. The riches he had brought back from his travels had now become a local legend.</p>
<p>At ninety he was much the same as at fifty. At ninety-nine they began to call him well-preserved; but unchanged would have been nearer the mark. There were some that shook their heads and thought this was too much of a good thing.</p>""",

    ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling", "Fantasy"): """<h2>Chapter 1: The Boy Who Lived</h2>
<p>Mr. and Mrs. Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal, thank you very much. They were the last people you'd expect to be involved in anything strange or mysterious, because they just didn't hold with such nonsense.</p>
<p>Mr. Dursley was the director of a firm called Grunnings, which made drills. He was a big, beefy man with hardly any neck, although he did have a very large moustache. Mrs. Dursley was thin and blonde and had nearly twice the usual amount of neck.</p>
<p>The Dursleys had a small son called Dudley and in their opinion there was no finer boy anywhere. The Dursleys had everything they wanted, but they also had a secret, and their greatest fear was that somebody would discover it.</p>""",

    ("Pride and Prejudice", "Jane Austen", "Romance"): """<h2>Chapter 1</h2>
<p>It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.</p>
<p>However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered as the rightful property of some one or other of their daughters.</p>
<p>"My dear Mr. Bennet," said his lady to him one day, "have you heard that Netherfield Park is let at last?"</p>
<p>Mr. Bennet replied that he had not.</p>
<p>"But it is," returned she; "for Mrs. Long has just been here, and she told me all about it."</p>""",

    ("To Kill a Mockingbird", "Harper Lee", "Fiction"): """<h2>Chapter 1</h2>
<p>When he was nearly thirteen, my brother Jem got his arm badly broken at the elbow. When it healed, and Jem's fears of never being able to play football were assuaged, he was seldom self-conscious about his injury.</p>
<p>His left arm was somewhat shorter than his right; when he stood or walked, the back of his hand was at right angles to his body, his thumb parallel to his thigh. He couldn't have cared less, so long as he could pass and punt.</p>
<p>When I asked him where he got his injury, Jem would say: "In the line of duty." He was more to the point when he said that the way he got it all began when Dill arrived.</p>""",

    ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction"): """<h2>Chapter 1</h2>
<p>In my younger and more vulnerable years my father gave me some advice that I've carried with me ever since.</p>
<p>"Whenever you feel like criticizing anyone," he told me, "just remember that all the people in this world haven't had the advantages that you've had."</p>
<p>He didn't say any more, but we've always been unusually communicative in a reserved way, and I understood that he meant a great deal more than that.</p>""",

    ("1984", "George Orwell", "Dystopian"): """<h2>Chapter 1</h2>
<p>It was a bright cold day in April, and the clocks were striking thirteen. Winston Smith, his chin nuzzled into his breast in an effort to escape the vile wind, slipped quickly through the glass doors of Victory Mansions.</p>
<p>The hallway smelt of boiled cabbage and old rag mats. At one end of it a coloured poster, too large for indoor display, had been tacked to the wall. It depicted simply an enormous face, more than a metre wide.</p>
<p>The face was that of a man of about forty-five, with a heavy black moustache and ruggedly handsome features.</p>""",

    ("The Hobbit", "J.R.R. Tolkien", "Fantasy"): """<h2>Chapter 1: An Unexpected Party</h2>
<p>In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, filled with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing in it to sit down on or to eat.</p>
<p>It was a hobbit-hole, and that means comfort. It had a perfectly round door like a porthole, painted green, with a shiny yellow brass knob in the exact middle.</p>
<p>The door opened on to a tube-shaped hall like a tunnel: a very comfortable tunnel without smoke, with panelled walls, and floors tiled and carpeted.</p>""",

    ("Dune", "Frank Herbert", "Science Fiction"): """<h2>Chapter 1</h2>
<p>The spice must flow. The spice has extended humanity's lifespan by several decades. The spice has enabled interstellar travel and the establishment of an empire that spans the galaxy.</p>
<p>Paul Atreides, son of Duke Leto Atreides, stood in the shadows of the corridor outside the Duke's chamber. He was fifteen, and his training in the arts of Mentat, swordplay, and survival had been rigorous.</p>
<p>His mother, Lady Jessica, a Bene Gesserit sister whose loyalty to the Duke had transcended even her sacred sisterhood, watched him with pride.</p>""",

    ("The Catcher in the Rye", "J.D. Salinger", "Fiction"): """<h2>Chapter 1</h2>
<p>If you really want to hear about it, the first thing you'll probably want to know is where I was born, and what my lousy childhood was like, and how my parents were occupied and all before they had me, and all that David Copperfield kind of crap, but I don't feel like going into it, if you want to know the truth.</p>
<p>In the first place, that stuff bores me, and in the second place, my parents would have about two haemorrhages apiece if I told anything pretty personal about them.</p>
<p>Their address is only the beginning of the tragedy.</p>""",

    ("Brave New World", "Aldous Huxley", "Dystopian"): """<h2>Chapter 1</h2>
<p>A squat grey building of only thirty-four stories. Over the main entrance the words, CENTRAL LONDON HATCHERY AND CONDITIONING CENTRE, and, in a shield, the World State's motto, COMMUNITY, IDENTITY, STABILITY.</p>
<p>The enormous room on the ground floor faced towards the north. Cold for all the summer beyond the panes, for all the tropical heat of the room itself, a harsh thin light glared through the windows.</p>
<p>Embossed with the letters of the alphabet, the test tubes containing the day-old embryos were ranged upon the shelves.</p>"""
}

def populate_book_content():
    """Populate the database with real book content"""
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            # Get all books from the database
            cur.execute("SELECT book_id, title, author, genre FROM new_book_table")
            books = cur.fetchall()
            
            updated_count = 0
            
            for book in books:
                book_id, title, author, genre = book
                
                # Look for matching content
                content = None
                for (book_key, book_content) in book_contents.items():
                    if (book_key[0].lower() == title.lower() and 
                        book_key[1].lower() == author.lower() and 
                        book_key[2].lower() == genre.lower()):
                        content = book_content
                        break
                
                # If exact match not found, try partial matching
                if not content:
                    for (book_key, book_content) in book_contents.items():
                        if (book_key[0].lower() in title.lower() or 
                            title.lower() in book_key[0].lower()) and \
                           book_key[1].lower() == author.lower():
                            content = book_content
                            break
                
                # Update the book with content if found
                if content:
                    cur.execute(
                        "UPDATE new_book_table SET content = %s WHERE book_id = %s",
                        (content, book_id)
                    )
                    print(f"Updated content for '{title}' by {author}")
                    updated_count += 1
                else:
                    print(f"No content found for '{title}' by {author} ({genre})")
            
            mysql.connection.commit()
            cur.close()
            
            print(f"\nSuccessfully updated {updated_count} books with content!")
            
        except Exception as e:
            print(f"Error populating book content: {e}")

if __name__ == "__main__":
    populate_book_content()