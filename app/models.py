# MySQL table schema for user accounts
# Run this SQL in your MySQL database to create the table

"""
CREATE TABLE user_table (
    user_id INT(11) NOT NULL AUTO_INCREMENT,
    username VARCHAR(45) NOT NULL,
    password VARCHAR(45) NOT NULL,
    email VARCHAR(45) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    preference VARCHAR(45) DEFAULT NULL,
    role VARCHAR(45) NOT NULL,
    dob DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    PRIMARY KEY (user_id),
    UNIQUE KEY email (email)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
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