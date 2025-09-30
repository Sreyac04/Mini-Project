# This script would typically be used to check table structures
# but since we can't run it directly, I'll provide the solution instead

print("Since we can't directly check the table structures,")
print("I'll provide the correct table creation SQL that should work with our code.")

table_creation_sql = """
-- For reading_progress_table
CREATE TABLE IF NOT EXISTS reading_progress_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    page_number INT DEFAULT 1,
    paused_word VARCHAR(255),
    paused_sentence TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_table(user_id),
    FOREIGN KEY (book_id) REFERENCES new_book_table(book_id)
);

-- For rating_table
CREATE TABLE IF NOT EXISTS rating_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    rating INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_table(user_id),
    FOREIGN KEY (book_id) REFERENCES new_book_table(book_id)
);

-- For feedback_table
CREATE TABLE IF NOT EXISTS feedback_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    feedback TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_table(user_id),
    FOREIGN KEY (book_id) REFERENCES new_book_table(book_id)
);
"""

print(table_creation_sql)