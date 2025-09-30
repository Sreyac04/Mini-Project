from app import app, mysql

# Sample book content (shortened versions for demonstration)
sample_books_content = {
    1: """<h2>Chapter 1: A Long-expected Party</h2>
<p>When Mr. Bilbo Baggins of Bag End announced that he would shortly be celebrating his eleventy-first birthday with a party of special magnificence, there was much talk and excitement in Hobbiton.</p>
<p>Bilbo was very rich and very peculiar, and had been the wonder of the Shire for sixty years, ever since his remarkable disappearance and unexpected return. The riches he had brought back from his travels had now become a local legend, and it was popularly believed, whatever the old folk might say, that the Hill at Bag End was full of tunnels stuffed with treasure.</p>""",

    4: """<h2>Chapter 1: The Boy Who Lived</h2>
<p>Mr. and Mrs. Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal, thank you very much. They were the last people you'd expect to be involved in anything strange or mysterious, because they just didn't hold with such nonsense.</p>
<p>Mr. Dursley was the director of a firm called Grunnings, which made drills. He was a big, beefy man with hardly any neck, although he did have a very large moustache. Mrs. Dursley was thin and blonde and had nearly twice the usual amount of neck, which came in very useful as she spent so much of her time craning over garden fences, spying on the neighbours. The Dursleys had a small son called Dudley and in their opinion there was no finer boy anywhere.</p>""",

    18: """<h2>Chapter 1</h2>
<p>It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.</p>
<p>However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered as the rightful property of some one or other of their daughters.</p>""",

    29: """<h2>Chapter 1</h2>
<p>When he was nearly thirteen, my brother Jem got his arm badly broken at the elbow. When it healed, and Jem's fears of never being able to play football were assuaged, he was seldom self-conscious about his injury. His left arm was somewhat shorter than his right; when he stood or walked, the back of his hand was at right angles to his body, his thumb parallel to his thigh. He couldn't have cared less, so long as he could pass and punt.</p>""",

    30: """<h2>Chapter 1</h2>
<p>In my younger and more vulnerable years my father gave me some advice that I've carried with me ever since.</p>
<p>"Whenever you feel like criticizing anyone," he told me, "just remember that all the people in this world haven't had the advantages that you've had."</p>"""
}

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        # Update books with content using book_id
        for book_id, content in sample_books_content.items():
            cur.execute(
                "UPDATE new_book_table SET content = %s WHERE book_id = %s",
                (content, book_id)
            )
            if cur.rowcount > 0:
                print(f"Updated content for book ID {book_id}")
            else:
                print(f"No book found with ID {book_id}")
        
        mysql.connection.commit()
        cur.close()
        
        print("Book content update completed!")
        
    except Exception as e:
        print(f"Error updating book content: {e}")