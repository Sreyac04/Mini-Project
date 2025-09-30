# This script would help verify database content
# Since we can't run database queries directly, I'll provide a solution

solution = """
To fix the database issues and ensure the reading progress is saved correctly:

1. First, make sure the required tables exist with correct structure:
   - reading_progress_table
   - rating_table
   - feedback_table

2. Make sure there are valid users and books in the database:
   - user_table should have at least user_id = 1
   - new_book_table should have at least book_id = 1

3. Test with valid data that matches the foreign key constraints

The Flask routes we added should now work correctly with the proper database setup.
"""

print(solution)