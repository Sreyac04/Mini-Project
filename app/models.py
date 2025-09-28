# MySQL table schema for user accounts
# Run this SQL in your MySQL database to create the table

"""
CREATE TABLE user_table (
    user_id INT(11) NOT NULL AUTO_INCREMENT,
    username VARCHAR(45) NOT NULL,
    password VARCHAR(45) NOT NULL,
    email VARCHAR(45) NOT NULL,
    phone_no VARCHAR(20) NOT NULL,
    role VARCHAR(45) NOT NULL DEFAULT 'user',
    dob DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    author VARCHAR(255) DEFAULT NULL,
    genre VARCHAR(100) DEFAULT NULL,
    PRIMARY KEY (user_id),
    UNIQUE KEY email (email)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

CREATE TABLE new_book_table (
    book_id INT(11) NOT NULL AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    ISBN VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (book_id),
    UNIQUE KEY unique_isbn (ISBN),
    INDEX idx_title (title),
    INDEX idx_author (author),
    INDEX idx_genre (genre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE favorite_book_table (
    fav_id INT(11) NOT NULL AUTO_INCREMENT,
    user_id INT(11) NOT NULL,
    book_id INT(11) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (fav_id),
    FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_book (user_id, book_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

# Python model (for reference, not used directly with flask_mysqldb)
class User:
    def __init__(self, user_id, username, password, email, phone_number, dob, gender, author=None, genre=None, role=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.phone_number = phone_number
        self.dob = dob
        self.gender = gender
        self.author = author
        self.genre = genre
        self.role = role

class Book:
    def __init__(self, book_id, title, author, genre, isbn, created_at=None, updated_at=None):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.isbn = isbn
        self.created_at = created_at
        self.updated_at = updated_at