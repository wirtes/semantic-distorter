#!/usr/bin/python

import sqlite3

# Define the SQLite database file name
db_filename = "database/book_lines.db"

# Create a connection to the database (this will create the database file if it doesn't exist)
conn = sqlite3.connect(db_filename)

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Create the "lines" table with three string fields: "line," "author," and "title"
cursor.execute('''
    CREATE TABLE IF NOT EXISTS lines (
        line TEXT,
        author TEXT,
        title TEXT
    )
''') 

# Commit the changes
conn.commit()

# Open and read the text file
text_file_name = "sample.txt"  # Replace with the name of your text file
with open("books/lines/Alices Adventures in Wonderland by Lewis Carroll.txt", "r") as text_file:
    for line in text_file:
        # Assuming you want to insert each line as a row with the author and file fields empty
        line = line.strip()
        author = "Lewis Carrol"
        title = "Alices Adventures in Wonderland"

        # Insert the line into the database
        cursor.execute("INSERT INTO lines (line, author, title) VALUES (?, ?, ?)", (line, author, title))

# Commit the changes
conn.commit()
conn.close()

print(f"SQLite database '{db_filename}' with 'lines' table has been created.")
