from app import app, mysql

# Sample book content (shortened versions for demonstration)
sample_books_content = {
    "The Lord of the Rings": """<h2>Chapter 1: A Long-expected Party</h2>
<p>When Mr. Bilbo Baggins of Bag End announced that he would shortly be celebrating his eleventy-first birthday with a party of special magnificence, there was much talk and excitement in Hobbiton.</p>
<p>Bilbo was very rich and very peculiar, and had been the wonder of the Shire for sixty years, ever since his remarkable disappearance and unexpected return. The riches he had brought back from his travels had now become a local legend, and it was popularly believed, whatever the old folk might say, that the Hill at Bag End was full of tunnels stuffed with treasure.</p>
<p>And if that was not enough for fame, there was also his prolonged vigour to marvel at. Time wore on, but it seemed to have little effect on Mr. Baggins. At ninety he was much the same as at fifty. At ninety-nine they began to call him well-preserved; but unchanged would have been nearer the mark. There were some that shook their heads and thought this was too much of a good thing; it seemed unfair that anyone should possess (apparently) perpetual youth as well as (reputedly) inexhaustible wealth.</p>
<p>"It will have to be paid for," they said. "There's no such thing as a free lunch." But Mr. Baggins had always been very careful about saying anything about his wealth, and the only satisfaction which the gossip-mongers could get was to insist that he was obviously growing peculiar.</p>
<p>As a matter of fact, he was growing peculiar, but not at all in the way that people believed. The view that he was growing avaricious, for instance, was generally believed to be an error. He had been generous with his money, and had spent most of it in providing for the needs of his friends and relations. When he was younger he had been very adventurous, and had led a rather solitary life until his adoption of his nephew Frodo.</p>
<p>Now, however, he was content with his quiet life in the country, and was growing old gracefully, without any obvious signs of senility. The only thing that seemed to worry him was the approaching date of his birthday, for he had begun to talk about giving up the Bag End and moving to Rivendell.</p>
<p>But that, as we shall see, was not to be for many a long year yet.</p>""",

    "Harry Potter and the Sorcerer's Stone": """<h2>Chapter 1: The Boy Who Lived</h2>
<p>Mr. and Mrs. Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal, thank you very much. They were the last people you'd expect to be involved in anything strange or mysterious, because they just didn't hold with such nonsense.</p>
<p>Mr. Dursley was the director of a firm called Grunnings, which made drills. He was a big, beefy man with hardly any neck, although he did have a very large moustache. Mrs. Dursley was thin and blonde and had nearly twice the usual amount of neck, which came in very useful as she spent so much of her time craning over garden fences, spying on the neighbours. The Dursleys had a small son called Dudley and in their opinion there was no finer boy anywhere.</p>
<p>The Dursleys had everything they wanted, but they also had a secret, and their greatest fear was that somebody would discover it. They didn't think they could bear it if anyone found out about the Potters. Mrs. Potter was Mrs. Dursley's sister, but they hadn't met for several years; in fact, Mrs. Dursley pretended she didn't have a sister, because her sister and her good-for-nothing husband were as unDursleyish as it was possible to be. The Dursleys shuddered to think what the neighbours would say if the Potters arrived in the street. The Dursleys knew that the Potters had a small son, too, but they had never even seen him. This boy was another good reason for keeping the Potters away; they didn't want Dudley mixing with a child like that.</p>
<p>When Mr. and Mrs. Dursley woke up on the dull, grey Tuesday our story starts, there was nothing about the cloudy sky outside to suggest that strange and mysterious things would soon be happening all over the country. Mr. Dursley hummed as he picked out his most boring tie for work, and Mrs. Dursley gossiped away happily as she wrestled a screaming Dudley into his high chair.</p>
<p>None of them noticed a large, tawny owl flutter past the window.</p>
<p>At half past eight, Mr. Dursley picked up his briefcase, pecked Mrs. Dursley on the cheek, and tried to kiss Dudley good-bye but missed, because Dudley was now having a tantrum and throwing his cereal at the walls.</p>
<p>"Little tyke," chortled Mr. Dursley as he left the house. He got into his car and backed out of number four's drive.</p>
<p>It was on the corner of the street that he noticed the first sign of something peculiar-a cat reading a map. For a second, Mr. Dursley didn't realize what he had seen-then he jerked his head around to look again. There was a tabby cat standing on the corner of Privet Drive, but there wasn't a map in sight. What could he have been thinking of? It must have been a trick of the light. Mr. Dursley blinked and stared at the cat. It stared back. As Mr. Dursley drove around the corner and up the road, he watched the cat in his mirror. It was now reading the sign that said Privet Drive-no, looking at the sign; cats couldn't read maps or signs. Mr. Dursley gave himself a little shake and put the cat out of his mind. As he drove towards town he thought of nothing except a large order of drills he was hoping to get that day.</p>""",

    "Pride and Prejudice": """<h2>Chapter 1</h2>
<p>It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.</p>
<p>However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered as the rightful property of some one or other of their daughters.</p>
<p>"My dear Mr. Bennet," said his lady to him one day, "have you heard that Netherfield Park is let at last?"</p>
<p>Mr. Bennet replied that he had not.</p>
<p>"But it is," returned she; "for Mrs. Long has just been here, and she told me all about it."</p>
<p>Mr. Bennet made no answer.</p>
<p>"Do not you want to know who has taken it?" cried his wife impatiently.</p>
<p>"You want to tell me, and I have no objection to hearing it."</p>
<p>This was invitation enough.</p>
<p>"Why, my dear, you must know, Mrs. Long says that Netherfield is taken by a young man of large fortune from the north of England; that he came down on Monday in a chaise and four to see the place, and was so much delighted with it that he agreed with Mr. Morris immediately; that he is to take possession before Michaelmas, and some of his servants are to be in the house by the end of next week."</p>
<p>"What is his name?"</p>
<p>"Bingley."</p>
<p>"Is he married or single?"</p>
<p>"Oh! single, my dear, to be sure! A single man of large fortune; four or five thousand a year. What a fine thing for our girls!"</p>
<p>"How so? How can it affect them?"</p>
<p>"My dear Mr. Bennet," replied his wife, "how can you be so tiresome! You must know that I am thinking of his marrying one of them."</p>
<p>"Is that his design in settling here?"</p>
<p>"Design! nonsense, how can you talk so! But it is very likely that he may fall in love with one of them, and therefore you must visit him as soon as he comes."</p>
<p>"I see no occasion for that. You and the girls may go, or you may send them by themselves, which perhaps will be still better, for as you are as handsome as any of them, Mr. Bingley might like you the best of the party."</p>""",

    "To Kill a Mockingbird": """<h2>Chapter 1</h2>
<p>When he was nearly thirteen, my brother Jem got his arm badly broken at the elbow. When it healed, and Jem's fears of never being able to play football were assuaged, he was seldom self-conscious about his injury. His left arm was somewhat shorter than his right; when he stood or walked, the back of his hand was at right angles to his body, his thumb parallel to his thigh. He couldn't have cared less, so long as he could pass and punt.</p>
<p>When I asked him where he got his injury, Jem would say: "In the line of duty." He was more to the point when he said that the way he got it all began when Dill arrived.</p>
<p>Dill was from Meridian, Mississippi, was spending the summer months in Maycomb with his aunt, Miss Rachel, and would be moving down to live with us. He was from the north, Jem told me, from Meridian, and that was all he knew about him. He had a little money, but he would never tell us exactly how much, except that it was a lot. He wore blue linen shorts that buttoned to his shirt, his hair was snow white and stuck to his head like duckfluff; he was a year my senior but I towered over him. As he told us on the first day, "I can read."</p>
<p>As I told Jem, "There ain't no need to fear a country that's gone soft." This was a blessing, I added, in disguise. "Besides," I said, "if we had no casualties, we'd have to go to school all the year 'round."</p>
<p>Jem demoted me from the team because I was a girl, then he suffered my presence on the condition that I play no more than fifteen minutes a day, and that I would not make any of the signals I used to make to the team in the stands. When I balked at such restrictions, Jem threatened to quit the team if I didn't abide by them. I knew he would, too, so I was careful.</p>
<p>When Dill arrived, Jem asked him what he reckoned to do that summer. Dill said he reckoned to give the only baby-doll house he had ever seen, no good to anyone, to me. Jem said he reckoned he would give me his bow and arrows. Dill said he reckoned he could make me a picture of Boo Radley. Jem said he reckoned he could make me a picture of Tom Sawyer. Dill said he reckoned he could make me a picture of Huckleberry Finn. Jem said he reckoned he could make me a picture of Becky Thatcher. Dill said he reckoned he could make me a picture of Joe Harper. Jem said he reckoned he could make me a picture of Muff Potter. Dill said he reckoned he could make me a picture of Injun Joe. Jem said he reckoned he could make me a picture of the Ku Klux Klan. Dill said he reckoned he could make me a picture of the Radley Place.</p>""",

    "The Great Gatsby": """<h2>Chapter 1</h2>
<p>In my younger and more vulnerable years my father gave me some advice that I've carried with me ever since.</p>
<p>"Whenever you feel like criticizing anyone," he told me, "just remember that all the people in this world haven't had the advantages that you've had."</p>
<p>He didn't say any more, but we've always been unusually communicative in a reserved way, and I understood that he meant a great deal more than that. In consequence, I'm inclined to reserve all judgments, a habit that has opened up many curious natures to me and also made me the victim of not a few veteran bores. The abnormal mind is quick to detect and attach itself to this quality when it appears in a normal person, and so it came about that in college I was unjustly accused of being a politician, because I was privy to the secret griefs of wild, unknown men. Most of the confidences were unsought-frequently I have feigned sleep, preoccupation, or a hostile levity when I realized by some unmistakable sign that an intimate revelation was quivering on the horizon; for the intimate revelations of young men, or at least the terms in which they express them, are usually plagiaristic and marred by obvious suppressions. Reserving judgments is a matter of infinite hope. I am still a little afraid of missing something if I forget that, as my father snobbishly suggested, and I snobbishly repeat, a sense of the fundamental decencies is parcelled out unequally at birth.</p>
<p>And, after boasting this way of my tolerance, I come to the admission that it has a limit. Conduct may be founded on the hard rock or the wet marshes, but after a certain point I don't care what it's founded on. When I came back from the East last autumn I felt that I wanted the world to be in uniform and at a sort of moral attention forever; I wanted no more riotous excursions with privileged glimpses into the human heart. Only Gatsby, the man who gives his name to this book, was exempt from my reaction-Gatsby, who represented everything for which I have an unaffected scorn. If personality is an unbroken series of successful gestures, then there was something gorgeous about him, some heightened sensitivity to the promises of life, as if he were related to one of those intricate machines that register earthquakes ten thousand miles away. This responsiveness had nothing to do with that flabby impressionability which is dignified under the name of the "creative temperament"-it was an extraordinary gift for hope, a romantic readiness such as I have never found in any other person and which it is not likely I shall ever find again. No-Gatsby turned out all right at the end; it is what preyed on Gatsby, what foul dust floated in the wake of his dreams that temporarily closed out my interest in the abortive sorrows and short-winded elations of men.</p>""",
}

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        # Update books with content
        for title, content in sample_books_content.items():
            cur.execute(
                "UPDATE new_book_table SET content = %s WHERE title = %s",
                (content, title)
            )
            if cur.rowcount > 0:
                print(f"Updated content for '{title}'")
            else:
                print(f"No book found with title '{title}'")
        
        mysql.connection.commit()
        cur.close()
        
        print("Book content update completed!")
        
    except Exception as e:
        print(f"Error updating book content: {e}")