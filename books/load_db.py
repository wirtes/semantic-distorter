#!/usr/bin/python

import sqlite3

# CONFIGURE BOOK TO LOAD HERE:
text_file_name = "There Was an Old Woman-Robert Silverberg.txt"  # Replace with the name of your text file
author = "Robert Silverberg"
title = "here Was an Old Woman"


# Define the SQLite database file name
db_filename = "../database/book_lines.db"

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

total_lines = 0
written_lines = 0
# Open and read the text file
with open("lines/" + text_file_name, "r") as text_file:
    for line in text_file:
        total_lines = total_lines + 1
        if len(line) > 25 and len(line) < 400:
            written_lines = written_lines + 1
            line = line.strip()
            cursor.execute("INSERT INTO lines (line, author, title) VALUES (?, ?, ?)", (line, author, title))


# Commit the changes
conn.commit()
conn.close()

print(f"Completed processing book file '{text_file_name}'.")
print(f"SQLite database '{db_filename}' with 'lines' table has been created/updated.")
print(f"{total_lines} total lines in file, {written_lines} written to database")
